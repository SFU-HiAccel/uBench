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
    kernel_config_file.append('const int DWIDTH = ' + str(port_width) + ';' + '\n')
    kernel_config_file.append('#define INTERFACE_WIDTH ap_uint<DWIDTH>' + '\n')
    kernel_config_file.append('const int NUM_ITERATIONS = 10000;' + '\n')

    with open(kernel_config_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(kernel_config_file)

def generateKernelCode(access_type, num_concurrent_port, port_width, max_burst_length):
    generateKernelConfigCode(port_width)

    kernel_file_name = 'krnl_ubench.cpp'
    kernel_file = []

    kernel_file.append('#include "krnl_config.h"' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('extern "C" {' + '\n')
    kernel_file.append('    void krnl_ubench(' + '\n')

    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            kernel_file.append('        volatile INTERFACE_WIDTH* in' + str(port_index) + ',' + '\n') 
        elif (access_type == 'WR'):
            kernel_file.append('        volatile INTERFACE_WIDTH* out' + str(port_index) + ',' + '\n') 
        else:
            print('kernelcode_gen: Invalid access type')

    kernel_file.append('        const int size,' + '\n')
    kernel_file.append('        int* sum' + '\n')
    kernel_file.append('    ) {' + '\n')
            
    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            kernel_file.append('        #pragma HLS INTERFACE m_axi port=in' + str(port_index) + ' offset=slave bundle=gmem' + str(port_index) + ' max_read_burst_length=' + str(max_burst_length) + '\n')
            kernel_file.append('        #pragma HLS INTERFACE s_axilite port=in' + str(port_index) + ' bundle=control' + '\n')
        elif (access_type == 'WR'):
            kernel_file.append('        #pragma HLS INTERFACE m_axi port=out' + str(port_index) + ' offset=slave bundle=gmem' + str(port_index) + ' max_write_burst_length=' + str(max_burst_length) + '\n')
            kernel_file.append('        #pragma HLS INTERFACE s_axilite port=out' + str(port_index) + ' bundle=control' + '\n')
        else:
            print('kernelcode_gen: Invalid access type')
            
    kernel_file.append('        #pragma HLS INTERFACE s_axilite port=size bundle=control' + '\n')
    kernel_file.append('        #pragma HLS INTERFACE m_axi port=sum offset=slave bundle=gmem' + str(num_concurrent_port) + '\n')
    kernel_file.append('        #pragma HLS INTERFACE s_axilite port=sum bundle=control' + '\n')
    kernel_file.append('        #pragma HLS INTERFACE s_axilite port=return bundle=control' + '\n')
    kernel_file.append('' + '\n')
    kernel_file.append('#pragma HLS DATAFLOW' + '\n')
    
    kernel_file.append('\n')
    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            kernel_file.append('        ap_uint<DWIDTH> temp_data_' + str(port_index) + '\n')
        elif (access_type == 'WR'):
            kernel_file.append('        ap_uint<DWIDTH> temp_data_' + str(port_index) + ' = 100;' + '\n')
        else:
            print('kernelcode_gen: Invalid access type')
    kernel_file.append('\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('        int temp_sum_' + str(port_index) + ' = 0;' + '\n')
    kernel_file.append('\n')
    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            kernel_file.append('        for (int i = 0; i < NUM_ITERATIONS; i++) {' + '\n')
            kernel_file.append('            for (int j = 0; j < size; j++) {' + '\n')
            kernel_file.append('            #pragma HLS PIPELINE II=1' + '\n')
            kernel_file.append('                temp_data_' + str(port_index) + ' = in' + str(port_index) + '[j];' + '\n')
            kernel_file.append('                ap_int<32> temp_int = temp_data_' + str(port_index) + '.range(31,0);' + '\n')
            kernel_file.append('                temp_sum_' + str(port_index) + ' += temp_int;' + '\n')
            kernel_file.append('            }' + '\n')
            kernel_file.append('        }' + '\n')
        elif (access_type == 'WR'):
            kernel_file.append('        for (int i = 0; i < NUM_ITERATIONS; i++) {' + '\n')
            kernel_file.append('            for (int j = 0; j < size; j++) {' + '\n')
            kernel_file.append('            #pragma HLS PIPELINE II=1' + '\n')
            kernel_file.append('                out' + str(port_index) + '[j] = temp_data_' + str(port_index) + ';' + '\n')
            kernel_file.append('                temp_sum_' + str(port_index) + ' = temp_sum_' + str(port_index) + ' + temp_data_' + str(port_index) + ';' + '\n')
            kernel_file.append('            }' + '\n')
            kernel_file.append('        }' + '\n')
        else:
            print('kernelcode_gen: Invalid access type')
    kernel_file.append('\n')
    for port_index in range(num_concurrent_port):
        kernel_file.append('        sum[' + str(port_index) + '] = temp_sum_' + str(port_index) + ';' + '\n')
    kernel_file.append('\n')
    kernel_file.append('        return;' + '\n')
    kernel_file.append('    }' + '\n')
    kernel_file.append('}' + '\n')

    with open(kernel_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(kernel_file)

