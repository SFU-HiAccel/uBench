#!/usr/bin/python 
import os
import re
import math 

def generateHostCode(num_kernel, num_concurrent_port, port_width, consecutive_data_start_size, consecutive_data_stop_size):
    host_file_name = 'host.cpp'
    host_file = []

    host_file.append('#include <stdlib.h>' + '\n')
    host_file.append('#include <fstream>' + '\n')
    host_file.append('#include <iostream>' + '\n')
    host_file.append('#include <chrono>' + '\n')
    host_file.append('#include <time.h>' + '\n')
    host_file.append('#include "../../../include/host.h"' + '\n')
    host_file.append('#include "../../../include/my_timer.h"' + '\n')
    host_file.append('' + '\n')
    host_file.append('#define WIDTH_FACTOR (' + str(port_width) + '/32)' + '\n')
    host_file.append('' + '\n')
    host_file.append('int main(int argc, char* argv[]) {' + '\n')
    host_file.append('' + '\n')
    host_file.append('    //TARGET_DEVICE macro needs to be passed from gcc command line' + '\n')
    host_file.append('    if(argc != 2) {' + '\n')
    host_file.append('                std::cout << "Usage: " << argv[0] <<" <xclbin>" << std::endl;' + '\n')
    host_file.append('                return EXIT_FAILURE;' + '\n')
    host_file.append('        }' + '\n')
    host_file.append('' + '\n')
    host_file.append('    char* xclbinFilename = argv[1];' + '\n')
    host_file.append('' + '\n')
    host_file.append('    std::vector<cl::Device> devices;' + '\n')
    host_file.append('    cl::Device device;' + '\n')
    host_file.append('    std::vector<cl::Platform> platforms;' + '\n')
    host_file.append('    bool found_device = false;' + '\n')
    host_file.append('' + '\n')
    host_file.append('    //traversing all Platforms To find Xilinx Platform and targeted' + '\n')
    host_file.append('    //Device in Xilinx Platform' + '\n')
    host_file.append('    cl::Platform::get(&platforms);' + '\n')
    host_file.append('    for(size_t i = 0; (i < platforms.size() ) & (found_device == false) ;i++){' + '\n')
    host_file.append('        cl::Platform platform = platforms[i];' + '\n')
    host_file.append('        std::string platformName = platform.getInfo<CL_PLATFORM_NAME>();' + '\n')
    host_file.append('        if ( platformName == "Xilinx"){' + '\n')
    host_file.append('            devices.clear();' + '\n')
    host_file.append('            platform.getDevices(CL_DEVICE_TYPE_ACCELERATOR, &devices);' + '\n')
    host_file.append('            if (devices.size()){' + '\n')
    host_file.append('                    device = devices[0];' + '\n')
    host_file.append('                    found_device = true;' + '\n')
    host_file.append('                    break;' + '\n')
    host_file.append('            }' + '\n')
    host_file.append('        }' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('    if (found_device == false){' + '\n')
    host_file.append('       std::cout << "Error: Unable to find Target Device "' + '\n')
    host_file.append('           << device.getInfo<CL_DEVICE_NAME>() << std::endl;' + '\n')
    host_file.append('       return EXIT_FAILURE;' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Creating Context and Command Queue for selected device' + '\n')
    host_file.append('    cl::Context context(device);' + '\n')
    host_file.append('    cl::CommandQueue q(context, device, CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE | CL_QUEUE_PROFILING_ENABLE);' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Load xclbin' + '\n')
    host_file.append('    std::cout << "Loading: " << xclbinFilename << "\\n";' + '\n')
    host_file.append('    std::ifstream bin_file(xclbinFilename, std::ifstream::binary);' + '\n')
    host_file.append('    bin_file.seekg (0, bin_file.end);' + '\n')
    host_file.append('    unsigned nb = bin_file.tellg();' + '\n')
    host_file.append('    bin_file.seekg (0, bin_file.beg);' + '\n')
    host_file.append('    char *buf = new char [nb];' + '\n')
    host_file.append('    bin_file.read(buf, nb);' + '\n')
    host_file.append('    ' + '\n')
    host_file.append('    // Creating Program from Binary File' + '\n')
    host_file.append('    cl::Program::Binaries bins;' + '\n')
    host_file.append('    bins.push_back({buf,nb});' + '\n')
    host_file.append('    devices.resize(1);' + '\n')
    host_file.append('    cl::Program program(context, devices, bins);' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // This call will get the kernel object from program. A kernel is an' + '\n')
    host_file.append('    // OpenCL function that is executed on the FPGA.' + '\n')

    for kernel_index in range(num_kernel):
        host_file.append('cl::Kernel krnl_streamWrite_'+ str(kernel_index+1) +'(program, "krnl_streamWrite_'+ str(kernel_index+1) +'");' + '\n')
        host_file.append('cl::Kernel krnl_streamRead_'+ str(kernel_index+1) +'(program, "krnl_streamRead_'+ str(kernel_index+1) +'");' + '\n')
        host_file.append('' + '\n')

    host_file.append('    int dataSize(0);' + '\n')
    host_file.append('        for (int payload(' + str(consecutive_data_start_size*1024/4) + '); payload <= ' + str(consecutive_data_stop_size*1024/4) + '; payload*=2){' + '\n')
    host_file.append('            dataSize = payload;' + '\n')
    host_file.append('            // These commands will alddlocate memory on the Device. The cl::Buffer objects can' + '\n')
    host_file.append('            // be used to reference the memory locations on the device.' + '\n')

    for port_index in range(num_concurrent_port):
        host_file.append('        cl::Buffer buffer_in_'+ str(port_index+1) +'(context, CL_MEM_READ_ONLY, sizeof(int)*dataSize);' + '\n')
        host_file.append('        cl::Buffer buffer_out_'+ str(port_index+1) +'(context, CL_MEM_WRITE_ONLY, sizeof(int)*dataSize);' + '\n')
    host_file.append('' + '\n')
    host_file.append('        //set the kernel Arguments' + '\n')
    host_file.append('        int input_size = dataSize / WIDTH_FACTOR;' + '\n')

    for kernel_index in range(num_kernel):
        host_file.append('        krnl_streamWrite_'+ str(kernel_index+1) +'.setArg(0,buffer_in_'+ str(kernel_index+1) +');' + '\n')
        host_file.append('        krnl_streamWrite_'+ str(kernel_index+1) +'.setArg(1,input_size);' + '\n')
        host_file.append('        krnl_streamRead_'+ str(kernel_index+1) +'.setArg(0,buffer_out_'+ str(kernel_index+1) +');' + '\n')
        host_file.append('        krnl_streamRead_'+ str(kernel_index+1) +'.setArg(1,input_size);' + '\n')
    host_file.append('' + '\n')

    host_file.append('        //We then need to map our OpenCL buffers to get the pointers' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('        int *ptr_a_'+ str(kernel_index+1) +' = (int *) q.enqueueMapBuffer(buffer_in_'+ str(kernel_index+1) +', CL_TRUE, CL_MAP_WRITE, 0, sizeof(int)*dataSize);' + '\n')
    host_file.append('        for(int i = 0 ; i< dataSize; i++){' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('            ptr_a_'+ str(kernel_index+1) +'[i] = rand();' + '\n')
    host_file.append('        }' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('        int *ptr_sum_'+ str(kernel_index+1) +' = (int *) q.enqueueMapBuffer(buffer_out_'+ str(kernel_index+1) +', CL_TRUE, CL_MAP_READ, 0, sizeof(int)*dataSize);' + '\n')
    host_file.append('        // Data will be migrated to kernel space' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('        q.enqueueMigrateMemObjects({buffer_in_'+ str(kernel_index+1) +'},0/* 0 means from host*/);' + '\n')
    host_file.append('' + '\n')
    host_file.append('        timespec timer = tic();' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('        q.enqueueTask(krnl_streamWrite_'+ str(kernel_index+1) +');' + '\n')
        host_file.append('        q.enqueueTask(krnl_streamRead_'+ str(kernel_index+1) +');' + '\n')   
    host_file.append('        q.finish();' + '\n')
    host_file.append('        toc(&timer, "Execution time");' + '\n')
    host_file.append('' + '\n')
    for kernel_index in range(num_kernel):
        host_file.append('        q.enqueueUnmapMemObject(buffer_in_'+ str(kernel_index+1) +', ptr_a_'+ str(kernel_index+1) +');' + '\n')
        host_file.append('        q.enqueueUnmapMemObject(buffer_out_'+ str(kernel_index+1) +', ptr_sum_'+ str(kernel_index+1) +');' + '\n')
    host_file.append('' + '\n')
    host_file.append('        q.finish();' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('    return EXIT_SUCCESS;' + '\n')
    host_file.append('}' + '\n')

    with open(host_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(host_file)
