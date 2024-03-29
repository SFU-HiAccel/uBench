#!/usr/bin/python 
import os
import re
import math 

def generateHostCode(num_kernel, num_concurrent_port, port_width, consecutive_data_start_size, consecutive_data_stop_size, bank_flag):
    host_file_name = 'host.cpp'
    host_file = []

    host_file.append('#include <algorithm>' + '\n')
    host_file.append('#include <iostream>' + '\n')
    host_file.append('#include <stdint.h>' + '\n')
    host_file.append('#include <stdlib.h>' + '\n')
    host_file.append('#include <string.h>' + '\n')
    host_file.append('#include <vector>' + '\n')
    host_file.append('#include <ctime>' + '\n')
    host_file.append('#include <cmath>' + '\n')
    host_file.append('' + '\n')
    host_file.append('#include "CL/cl_ext_xilinx.h"' + '\n')
    host_file.append('#include "xcl2.hpp"' + '\n')
    host_file.append('' + '\n')
    host_file.append('#define NUM_KERNEL (' + str(num_kernel) + ')' + '\n')
    host_file.append('#define NUM_PORT (' + str(num_concurrent_port) + ')' + '\n')
    host_file.append('' + '\n')
    host_file.append('int main(int argc, char *argv[]) {' + '\n')
    host_file.append('    if (argc != 2) {' + '\n')
    host_file.append('        printf("Usage: %s <XCLBIN> \\n", argv[0]);' + '\n')
    host_file.append('        return -1;' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('' + '\n')
    host_file.append('    std::string binaryFile = argv[1];' + '\n')
    host_file.append('    cl_int err;' + '\n')
    host_file.append('    cl::CommandQueue q;' + '\n')
    host_file.append('    std::string krnl_write_name = "krnl_streamWrite";' + '\n')
    host_file.append('    std::vector<cl::Kernel> write_krnl(NUM_KERNEL);' + '\n')
    host_file.append('    std::string krnl_read_name = "krnl_streamRead";' + '\n')
    host_file.append('    std::vector<cl::Kernel> read_krnl(NUM_KERNEL);' + '\n')
    host_file.append('    cl::Context context;' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // The get_xil_devices will return vector of Xilinx Devices' + '\n')
    host_file.append('    auto devices = xcl::get_xil_devices();' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // read_binary_file() command will find the OpenCL binary file created using the' + '\n')
    host_file.append('    // V++ compiler load into OpenCL Binary and return pointer to file buffer.' + '\n')
    host_file.append('    auto fileBuf = xcl::read_binary_file(binaryFile);' + '\n')
    host_file.append('' + '\n')
    host_file.append('    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};' + '\n')
    host_file.append('    int valid_device = 0;' + '\n')
    host_file.append('    for (unsigned int i = 0; i < devices.size(); i++) {' + '\n')
    host_file.append('        auto device = devices[i];' + '\n')
    host_file.append('        // Creating Context and Command Queue for selected Device' + '\n')
    host_file.append('        OCL_CHECK(err, context = cl::Context({device}, NULL, NULL, NULL, &err));' + '\n')
    host_file.append('        OCL_CHECK(err,' + '\n')
    host_file.append('                  q = cl::CommandQueue(context,' + '\n')
    host_file.append('                                       {device},' + '\n')
    host_file.append('                                       CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE |' + '\n')
    host_file.append('                                           CL_QUEUE_PROFILING_ENABLE,' + '\n')
    host_file.append('                                       &err));' + '\n')
    host_file.append('' + '\n')
    host_file.append('        std::cout << "Trying to program device[" << i' + '\n')
    host_file.append('                  << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;' + '\n')
    host_file.append('        cl::Program program(context, {device}, bins, NULL, &err);' + '\n')
    host_file.append('        if (err != CL_SUCCESS) {' + '\n')
    host_file.append('            std::cout << "Failed to program device[" << i' + '\n')
    host_file.append('                      << "] with xclbin file!\\n";' + '\n')
    host_file.append('        } else {' + '\n')
    host_file.append('            std::cout << "Device[" << i << "]: program successful!\\n";' + '\n')
    host_file.append('            // Creating Kernel object using Compute unit names' + '\n')
    host_file.append('' + '\n')
    host_file.append('            for (int i = 0; i < NUM_KERNEL; i++) {' + '\n')
    host_file.append('                std::string cu_id = std::to_string(i + 1);' + '\n')
    host_file.append('                std::string krnl_write_name_full =' + '\n')
    host_file.append('                    krnl_write_name + ":{" + krnl_write_name + "_" + cu_id + "}";' + '\n')
    host_file.append('                std::string krnl_read_name_full =' + '\n')
    host_file.append('                    krnl_read_name + ":{" + krnl_read_name + "_" + cu_id + "}";' + '\n')
    host_file.append('' + '\n')
    host_file.append('                printf("Creating a kernel [%s] for CU(%d)\\n",' + '\n')
    host_file.append('                       krnl_write_name_full.c_str(),' + '\n')
    host_file.append('                       i + 1);' + '\n')
    host_file.append('                printf("Creating a kernel [%s] for CU(%d)\\n",' + '\n')
    host_file.append('                       krnl_read_name_full.c_str(),' + '\n')
    host_file.append('                       i + 1);' + '\n')
    host_file.append('                //Here Kernel object is created by specifying kernel name along with compute unit.' + '\n')
    host_file.append('                //For such case, this kernel object can only access the specific Compute unit' + '\n')
    host_file.append('                OCL_CHECK(err, write_krnl[i] = cl::Kernel(program, krnl_write_name_full.c_str(), &err));' + '\n')
    host_file.append('                OCL_CHECK(err, read_krnl[i] = cl::Kernel(program, krnl_read_name_full.c_str(), &err));' + '\n')
    host_file.append('            }' + '\n')
    host_file.append('' + '\n')
    host_file.append('            valid_device++;' + '\n')
    host_file.append('            break; // we break because we found a valid device' + '\n')
    host_file.append('        }' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('    if (valid_device == 0) {' + '\n')
    host_file.append('        std::cout << "Failed to program any device found, exit!\\n";' + '\n')
    host_file.append('        exit(EXIT_FAILURE);' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Setting random seed' + '\n')
    host_file.append('    std::srand(std::time(NULL));' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Specify default payload size' + '\n')
    host_file.append('    int dataSize(0);' + '\n')
    host_file.append('    for (int payload(' + str(consecutive_data_start_size*1024/4) + '); payload <= ' + str(consecutive_data_stop_size*1024/4) + '; payload*=2){' + '\n')
    host_file.append('        dataSize = payload;' + '\n')
    host_file.append('        if (xcl::is_emulation()) {' + '\n')
    host_file.append('            dataSize = 256; //1KB' + '\n')
    host_file.append('        }' + '\n')
    host_file.append('' + '\n')
    host_file.append('        // Allocate host buffer' + '\n')
    host_file.append('        std::vector<int, aligned_allocator<int>> read_source(dataSize);' + '\n')
    host_file.append('        std::generate(read_source.begin(), read_source.end(), std::rand);' + '\n')
    host_file.append('        std::vector<int, aligned_allocator<int>> write_source(dataSize);' + '\n')
    host_file.append('        std::generate(write_source.begin(), write_source.end(), std::rand);' + '\n')
    host_file.append('' + '\n')
    host_file.append('        std::vector<cl_mem_ext_ptr_t> source_in0_ext(NUM_KERNEL);' + '\n')
    host_file.append('        std::vector<cl::Buffer> source_in0_buffer(NUM_KERNEL);' + '\n')
    host_file.append('        std::vector<cl_mem_ext_ptr_t> source_out0_ext(NUM_KERNEL);' + '\n')
    host_file.append('        std::vector<cl::Buffer> source_out0_buffer(NUM_KERNEL);' + '\n')
    host_file.append('' + '\n')
    host_file.append('    	// For Allocating Buffer to specific Global Memory Bank, user has to use cl_mem_ext_ptr_t' + '\n')
    host_file.append('            // and provide the Banks' + '\n')
    host_file.append('        if (xcl::is_emulation()) {' + '\n')
    host_file.append('              for (int i = 0; i < NUM_KERNEL; i++) {' + '\n')
    host_file.append('    		source_in0_ext[i].obj = read_source.data();' + '\n')
    host_file.append('    		source_in0_ext[i].param = 0;' + '\n')
    host_file.append('    		source_in0_ext[i].flags = ' + bank_flag + ';' + '\n')
    host_file.append('    		source_out0_ext[i].obj = write_source.data();' + '\n')
    host_file.append('    		source_out0_ext[i].param = 0;' + '\n')
    host_file.append('    		source_out0_ext[i].flags = ' + bank_flag + ';' + '\n')
    host_file.append('    	    }' + '\n')
    host_file.append('    	}' + '\n')
    host_file.append('        else{' + '\n')
    host_file.append('              for (int i = 0; i < NUM_KERNEL; i++) {' + '\n')
    host_file.append('    	        source_in0_ext[i].obj = read_source.data();' + '\n')
    host_file.append('    	        source_in0_ext[i].param = 0;' + '\n')
    host_file.append('    	        source_in0_ext[i].flags = ' + bank_flag + ';' + '\n')
    host_file.append('    		source_out0_ext[i].obj = write_source.data();' + '\n')
    host_file.append('    		source_out0_ext[i].param = 0;' + '\n')
    host_file.append('    		source_out0_ext[i].flags = ' + bank_flag + ';' + '\n')
    host_file.append('    	    }' + '\n')
    host_file.append('        }' + '\n')
    host_file.append('' + '\n')
    host_file.append('        // These commands will allocate memory on the FPGA. The cl::Buffer objects can' + '\n')
    host_file.append('        // be used to reference the memory locations on the device.' + '\n')
    host_file.append('        //Creating Buffers' + '\n')
    host_file.append('        for (int i = 0; i < NUM_KERNEL; i++) {' + '\n')
    host_file.append('		    OCL_CHECK(err,' + '\n')
    host_file.append('		                source_in0_buffer[i] =' + '\n')
    host_file.append('		                    cl::Buffer(context,' + '\n')
    host_file.append('		                                CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX |' + '\n')
    host_file.append('		                                    CL_MEM_USE_HOST_PTR,' + '\n')
    host_file.append('		                                sizeof(int) * dataSize,' + '\n')
    host_file.append('		                                &source_in0_ext[i],' + '\n')
    host_file.append('		                                &err));' + '\n')
    host_file.append('		    // Copy input data to Device Global Memory' + '\n')
    host_file.append('		    OCL_CHECK(err,' + '\n')
    host_file.append('		                err = q.enqueueMigrateMemObjects(' + '\n')
    host_file.append('		                    {source_in0_buffer[i]},' + '\n')
    host_file.append('		                    0 /* 0 means from host*/));' + '\n')
    host_file.append('            OCL_CHECK(err,' + '\n')
    host_file.append('                        source_out0_buffer[i] =' + '\n')
    host_file.append('                            cl::Buffer(context,' + '\n')
    host_file.append('                                        CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX |' + '\n')
    host_file.append('                                            CL_MEM_USE_HOST_PTR,' + '\n')
    host_file.append('                                        sizeof(int) * dataSize,' + '\n')
    host_file.append('                                        &source_out0_ext[i],' + '\n')
    host_file.append('                                        &err));' + '\n')    
    host_file.append('		}' + '\n')
    host_file.append('        q.finish();' + '\n')
    host_file.append('' + '\n')
    host_file.append('        // Start timer' + '\n')
    host_file.append('        double kernel_time_in_sec = 0;' + '\n')
    host_file.append('        std::chrono::duration<double> kernel_time(0);' + '\n')
    host_file.append('        auto kernel_start = std::chrono::high_resolution_clock::now();' + '\n')
    host_file.append('' + '\n')
    host_file.append('        //Setting the compute kernel arguments' + '\n')
    host_file.append('        dataSize = dataSize / (' + str(port_width) + '/32);' + '\n')
    host_file.append('		int i, j = 0;' + '\n')
    host_file.append('		for (i = 0; i < NUM_KERNEL; i++) {' + '\n')
    host_file.append('            //Write Kernel' + '\n')
    host_file.append('            OCL_CHECK(err, err = write_krnl[i].setArg(0, source_in0_buffer[i]));' + '\n')
    host_file.append('            OCL_CHECK(err, err = write_krnl[i].setArg(1, dataSize));' + '\n')
    host_file.append('            //Invoking the compute kernels' + '\n')
    host_file.append('            OCL_CHECK(err, err = q.enqueueTask(write_krnl[i]));' + '\n')
    host_file.append('            //Read Kernel' + '\n')
    host_file.append('            OCL_CHECK(err, err = read_krnl[i].setArg(0, source_out0_buffer[i]));' + '\n')
    host_file.append('            OCL_CHECK(err, err = read_krnl[i].setArg(1, dataSize));' + '\n')
    host_file.append('            //Invoking the compute kernels' + '\n')
    host_file.append('            OCL_CHECK(err, err = q.enqueueTask(read_krnl[i]));' + '\n')    
    host_file.append('		}' + '\n')
    host_file.append('        q.finish();' + '\n')
    host_file.append('' + '\n')
    host_file.append('        // Stop timer' + '\n')
    host_file.append('        auto kernel_end = std::chrono::high_resolution_clock::now();' + '\n')
    host_file.append('        kernel_time = std::chrono::duration<double>(kernel_end - kernel_start);' + '\n')
    host_file.append('        kernel_time_in_sec = kernel_time.count();' + '\n')
    host_file.append('	      double bw_result = payload * 4 * 0.000010000 / kernel_time_in_sec * NUM_KERNEL * NUM_PORT;' + '\n')
    host_file.append('        std::cout << bw_result << std::endl;' + '\n')
    host_file.append('    }' + '\n')
    host_file.append('' + '\n')
    host_file.append('    // Exit program' + '\n')
    host_file.append('    return EXIT_SUCCESS;' + '\n')
    host_file.append('}' + '\n')

    with open(host_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(host_file)
