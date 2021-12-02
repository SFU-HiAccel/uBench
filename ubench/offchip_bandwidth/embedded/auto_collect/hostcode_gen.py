#!/usr/bin/python 
import os
import re
import math 

def generateHostCode(access_type, num_concurrent_port, port_width, consecutive_data_start_size, consecutive_data_stop_size):
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
    host_file.append('    cl::CommandQueue q(context, device, CL_QUEUE_PROFILING_ENABLE);' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Load xclbin' + '\n')
    host_file.append('    std::cout << "Loading: '" << xclbinFilename << "'\\n";' + '\n')
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
    host_file.append('    cl::Kernel krnl_ubench(program,"krnl_ubench");' + '\n')
    host_file.append('' + '\n')
    host_file.append('    int dataSize(0);' + '\n')
    host_file.append('        for (int payload(' + str(consecutive_data_start_size*1024/4) + '); payload <= ' + str(consecutive_data_stop_size*1024/4) + '; payload*=2){' + '\n')
    host_file.append('            dataSize = payload;' + '\n')
    host_file.append('            // These commands will alddlocate memory on the Device. The cl::Buffer objects can' + '\n')
    host_file.append('            // be used to reference the memory locations on the device.' + '\n')

    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            host_file.append('        cl::Buffer buffer_' + str(port_index) + '(context, CL_MEM_READ_ONLY, sizeof(int)*dataSize);' + '\n')
        elif (access_type == 'WR'):
            host_file.append('        cl::Buffer buffer_' + str(port_index) + '(context, CL_MEM_WRITE_ONLY, sizeof(int)*dataSize);' + '\n')
        else:
            print('hostcode_gen: Invalid access type.')

    host_file.append('        cl::Buffer buffer_sum(context, CL_MEM_WRITE_ONLY, sizeof(int)*10);' + '\n')
    host_file.append('' + '\n')
    host_file.append('        //set the kernel Arguments' + '\n')
    host_file.append('        int input_size = dataSize / WIDTH_FACTOR;' + '\n')

    for port_index in range(num_concurrent_port):
        host_file.append('        krnl_ubench.setArg(' + str(port_index) + ', buffer_' + str(port_index) + ');' + '\n')
    host_file.append('        krnl_ubench.setArg(' + str(num_concurrent_port) + ', input_size);' + '\n')
    host_file.append('        krnl_ubench.setArg(' + str(num_concurrent_port+1) + ', buffer_sum);' + '\n')
    host_file.append('' + '\n')
    host_file.append('        //We then need to map our OpenCL buffers to get the pointers' + '\n')

    if (access_type == 'RD'):
        for port_index in range(num_concurrent_port):
            host_file.append('        int *ptr_' + str(port_index) + ' = (int *) q.enqueueMapBuffer (buffer_' + str(port_index) + ', CL_TRUE, CL_MAP_WRITE, 0, sizeof(int)*dataSize);' + '\n')
        host_file.append('        int *ptr_sum = (int *) q.enqueueMapBuffer (buffer_sum , CL_TRUE , CL_MAP_READ, 0, sizeof(int)*10);' + '\n')
        host_file.append('        for(int i = 0 ; i< dataSize; i++){' + '\n')
        for port_index in range(num_concurrent_port):
            host_file.append('            ptr_' + str(port_index) + '[i] = rand();' + '\n')
        host_file.append('        }' + '\n')
        for port_index in range(num_concurrent_port):
            host_file.append('        q.enqueueMigrateMemObjects({buffer_' + str(port_index) + '}, 0/* 0 means from host*/);' + '\n')
    elif (access_type == 'WR'):
        for port_index in range(num_concurrent_port):
            host_file.append('        int *ptr_' + str(port_index) + ' = (int *) q.enqueueMapBuffer (buffer_' + str(port_index) + ', CL_TRUE, CL_MAP_READ, 0, sizeof(int)*dataSize);' + '\n')
        host_file.append('        int *ptr_sum = (int *) q.enqueueMapBuffer (buffer_sum , CL_TRUE , CL_MAP_READ, 0, sizeof(int)*10);' + '\n')
    else:
        print('hostcode_gen: Invalid access type.')

    host_file.append('' + '\n')
    host_file.append('        timespec timer = tic();' + '\n')
    host_file.append('        q.enqueueTask(krnl_ubench);' + '\n')
    host_file.append('        q.finish();' + '\n')
    host_file.append('        toc(&timer, "Execution time");' + '\n')
    host_file.append('' + '\n')
    for port_index in range(num_concurrent_port):
        host_file.append('        q.enqueueUnmapMemObject(buffer_' + str(port_index) + ', ptr_' + str(port_index) + ');' + '\n')
    host_file.append('        q.enqueueUnmapMemObject(buffer_sum , ptr_sum);' + '\n')
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
