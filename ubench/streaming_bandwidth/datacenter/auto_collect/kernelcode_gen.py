#!/usr/bin/python
import os
import re
import math

def generateKernelConfigCode(port_width):
    kernel_config_file_name = 'krnl_config.h'
    kernel_config_file = []

    kernel_config_file.append('#include \"ap_int.h\"' + '\n')
    kernel_config_file.append('#include <inttypes.h>' + '\n')
    kernel_config_file.append('' + '\n')
    kernel_config_file.append('#include \"ap_axi_sdata.h\"' + '\n')
    kernel_config_file.append('#include \"hls_stream.h\"' + '\n')
    kernel_config_file.append('' + '\n')
    kernel_config_file.append('const int DWIDTH = ' + str(port_width) + ';' + '\n')
    kernel_config_file.append('#define INTERFACE_WIDTH ap_uint<DWIDTH>' + '\n')
    kernel_config_file.append('typedef ap_axiu<DWIDTH, 0, 0, 0> pkt;' + '\n')
    kernel_config_file.append('const int NUM_ITERATIONS = 10000;' + '\n')

    with open(kernel_config_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(kernel_config_file)

def generateKernelWriteKernelCode(num_concurrent_port):
    kernel_file_name = 'krnl_streamWrite.cpp'
    kernel_file = []

    kernel_file.append('#include \"krnl_config.h\"' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('extern "C" {' + '\n')
    kernel_file.append('    void krnl_streamWrite(' + '\n')
    kernel_file.append('        volatile INTERFACE_WIDTH* in0,' + '\n')
    kernel_file.append('        const int size,' + '\n')
    for port_index in range(num_concurrent_port-1):
        kernel_file.append('        hls::stream<pkt> &kout' + str(port_index+1) + ',' + '\n')
    kernel_file.append('        hls::stream<pkt> &kout' + str(num_concurrent_port) + '\n')
    kernel_file.append('    ) {' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=in0 bundle=control' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('    #pragma HLS INTERFACE axis port = kout' + str(port_index+1) + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=size bundle=control' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=return bundle=control' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('    volatile INTERFACE_WIDTH temp_data_' + str(port_index+1) + ' = 100;' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('#pragma HLS DATAFLOW' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('        for (int i = 0; i < NUM_ITERATIONS; i++) {' + '\n')
        kernel_file.append('            for (int j = 0; j < size; j++) {' + '\n')
        kernel_file.append('            #pragma HLS PIPELINE II=1' + '\n')
        kernel_file.append('                pkt v' + str(port_index+1) + ';' + '\n')
        kernel_file.append('                v' + str(port_index+1) + '.data = temp_data_' + str(port_index+1) + ';' + '\n')
        kernel_file.append('                kout' + str(port_index+1) + '.write(v' + str(port_index+1) + ');' + '\n')
        kernel_file.append('            }' + '\n')
        kernel_file.append('        }' + '\n')
        kernel_file.append('' + '\n')
    kernel_file.append('        return;' + '\n')
    kernel_file.append('    }' + '\n')
    kernel_file.append('}' + '\n')

    with open(kernel_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(kernel_file)

def generateKernelReadKernelCode(num_concurrent_port):
    kernel_file_name = 'krnl_streamRead.cpp'
    kernel_file = []

    kernel_file.append('#include \"krnl_config.h\"' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('extern "C" {' + '\n')
    kernel_file.append('    void krnl_streamRead(' + '\n')
    kernel_file.append('        volatile INTERFACE_WIDTH* out0,' + '\n')
    kernel_file.append('        const int size,' + '\n')
    for port_index in range(num_concurrent_port-1):
        kernel_file.append('        hls::stream<pkt> &kin' + str(port_index+1) + ',' + '\n')
    kernel_file.append('        hls::stream<pkt> &kin' + str(num_concurrent_port) + '\n')
    kernel_file.append('    ) {' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE m_axi port=out0 offset=slave bundle=gmem0' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=out0 bundle=control' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('    #pragma HLS INTERFACE axis port = kin' + str(port_index+1) + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=size bundle=control' + '\n')
    kernel_file.append('    #pragma HLS INTERFACE s_axilite port=return bundle=control' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('    volatile INTERFACE_WIDTH temp_data_' + str(port_index+1) + ' = 100;' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('#pragma HLS DATAFLOW' + '\n')
    kernel_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('        for (int i = 0; i < NUM_ITERATIONS; i++) {' + '\n')
        kernel_file.append('            for (int j = 0; j < size; j++) {' + '\n')
        kernel_file.append('            #pragma HLS PIPELINE II=1' + '\n')
        kernel_file.append('                pkt v' + str(port_index+1) + ' = kin' + str(port_index+1) + '.read();' + '\n')
        kernel_file.append('                temp_data_' + str(port_index+1) + ' = v' + str(port_index+1) + '.data;' + '\n')
        kernel_file.append('            }' + '\n')
        kernel_file.append('        }' + '\n')
        kernel_file.append('' + '\n')
    kernel_file.append('        return;' + '\n')
    kernel_file.append('    }' + '\n')
    kernel_file.append('}' + '\n')

    with open(kernel_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(kernel_file)

def generateKernelCode(num_concurrent_port, port_width):
    generateKernelConfigCode(port_width)
    generateKernelWriteKernelCode(num_concurrent_port)
    generateKernelReadKernelCode(num_concurrent_port)

