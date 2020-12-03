#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <ctime>
#include <cmath>

#include "CL/cl_ext_xilinx.h"
#include "xcl2.hpp"

#include "krnl_config.h"

#define NUM_KERNEL_PAIRS 1

//HBM Banks requirements
#define MAX_HBM_BANKCOUNT 32
#define BANK_NAME(n) n | XCL_MEM_TOPOLOGY
const int bank[MAX_HBM_BANKCOUNT] = {
    BANK_NAME(0),  BANK_NAME(1),  BANK_NAME(2),  BANK_NAME(3),  BANK_NAME(4),
    BANK_NAME(5),  BANK_NAME(6),  BANK_NAME(7),  BANK_NAME(8),  BANK_NAME(9),
    BANK_NAME(10), BANK_NAME(11), BANK_NAME(12), BANK_NAME(13), BANK_NAME(14),
    BANK_NAME(15), BANK_NAME(16), BANK_NAME(17), BANK_NAME(18), BANK_NAME(19),
    BANK_NAME(20), BANK_NAME(21), BANK_NAME(22), BANK_NAME(23), BANK_NAME(24),
    BANK_NAME(25), BANK_NAME(26), BANK_NAME(27), BANK_NAME(28), BANK_NAME(29),
    BANK_NAME(30), BANK_NAME(31)};

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <XCLBIN> \n", argv[0]);
        return -1;
    }

    std::string binaryFile = argv[1];
    cl_int err;
    cl::CommandQueue q;
    std::string krnl_write_name = "krnl_streamWrite";
    std::string krnl_read_name = "krnl_streamRead";
    std::vector<cl::Kernel> write_krnl(NUM_KERNEL_PAIRS);
    std::vector<cl::Kernel> read_krnl(NUM_KERNEL_PAIRS);
    cl::Context context;

    // The get_xil_devices will return vector of Xilinx Devices
    auto devices = xcl::get_xil_devices();

    // read_binary_file() command will find the OpenCL binary file created using the
    // V++ compiler load into OpenCL Binary and return pointer to file buffer.
    auto fileBuf = xcl::read_binary_file(binaryFile);

    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    int valid_device = 0;
    for (unsigned int i = 0; i < devices.size(); i++) {
        auto device = devices[i];
        // Creating Context and Command Queue for selected Device
        OCL_CHECK(err, context = cl::Context({device}, NULL, NULL, NULL, &err));
        OCL_CHECK(err,
                  q = cl::CommandQueue(context,
                                       {device},
                                       CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE |
                                           CL_QUEUE_PROFILING_ENABLE,
                                       &err));

        std::cout << "Trying to program device[" << i
                  << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
        cl::Program program(context, {device}, bins, NULL, &err);
        if (err != CL_SUCCESS) {
            std::cout << "Failed to program device[" << i
                      << "] with xclbin file!\n";
        } else {
            std::cout << "Device[" << i << "]: program successful!\n";
            // Creating Kernel object using Compute unit names

            for (int i = 0; i < NUM_KERNEL_PAIRS; i++) {
                std::string cu_id = std::to_string(i + 1);
                
                std::string krnl_write_name_full =
                    krnl_write_name + ":{" + krnl_write_name + "_" + cu_id + "}";
                std::string krnl_read_name_full =
                    krnl_read_name + ":{" + krnl_read_name + "_" + cu_id + "}";                    

                printf("Creating a kernel [%s] for CU(%d)\n",
                       krnl_write_name.c_str(),
                       i + 1);
                printf("Creating a kernel [%s] for CU(%d)\n",
                       krnl_read_name.c_str(),
                       i + 1);                       
                //Here Kernel object is created by specifying kernel name along with compute unit.
                //For such case, this kernel object can only access the specific Compute unit
                OCL_CHECK(err, write_krnl[i] = cl::Kernel(program, krnl_write_name_full.c_str(), &err));
                OCL_CHECK(err, read_krnl[i] = cl::Kernel(program, krnl_read_name_full.c_str(), &err));
            }

            valid_device++;
            break; // we break because we found a valid device
        }
    }
    if (valid_device == 0) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    // Setting random seed
    std::srand(std::time(NULL));

    // Specify default payload size
    int dataSize(0);
    for (int payload(256); payload <= 262144*4; payload*=2){
        dataSize = payload;
        if (xcl::is_emulation()) {
            dataSize = 256; //1KB
        }

        // Allocate host buffer
        std::vector<int, aligned_allocator<int>> read_source(dataSize);
        std::generate(read_source.begin(), read_source.end(), std::rand);
        std::vector<int, aligned_allocator<int>> write_source(dataSize);
        std::generate(write_source.begin(), write_source.end(), std::rand);
        
        std::vector<cl_mem_ext_ptr_t> source_in_ext(NUM_KERNEL_PAIRS);
        std::vector<cl::Buffer> source_in_buffer(NUM_KERNEL_PAIRS);
        std::vector<cl_mem_ext_ptr_t> source_out_ext(NUM_KERNEL_PAIRS);
        std::vector<cl::Buffer> source_out_buffer(NUM_KERNEL_PAIRS);        
        
        // For Allocating Buffer to specific Global Memory Bank, user has to use cl_mem_ext_ptr_t
        // and provide the Banks
        if (xcl::is_emulation()) {
       	    for (int i = 0; i < NUM_KERNEL_PAIRS; i++) {
                source_in_ext[i].obj = read_source.data();
                source_in_ext[i].param = 0;
                source_in_ext[i].flags = XCL_MEM_DDR_BANK1;
                source_out_ext[i].obj = write_source.data();
                source_out_ext[i].param = 0;
                source_out_ext[i].flags = XCL_MEM_DDR_BANK1;
            }
        }
        else{
       	    for (int i = 0; i < NUM_KERNEL_PAIRS; i++) {
                source_in_ext[i].obj = read_source.data();
                source_in_ext[i].param = 0;
                source_in_ext[i].flags = XCL_MEM_DDR_BANK0;
                source_out_ext[i].obj = write_source.data();
                source_out_ext[i].param = 0;
                source_out_ext[i].flags = XCL_MEM_DDR_BANK1;
            }
        }

        // These commands will allocate memory on the FPGA. The cl::Buffer objects can
        // be used to reference the memory locations on the device.
        //Creating Buffers
		for (int i = 0; i < NUM_KERNEL_PAIRS; i++) {
		    OCL_CHECK(err,
		                source_in_buffer[i] =
		                    cl::Buffer(context,
		                                CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX |
		                                    CL_MEM_USE_HOST_PTR,
		                                sizeof(int) * dataSize,
		                                &source_in_ext[i],
		                                &err));
		    // Copy input data to Device Global Memory
		    OCL_CHECK(err,
		                err = q.enqueueMigrateMemObjects(
		                    {source_in_buffer[i]},
		                    0 /* 0 means from host*/));
		    OCL_CHECK(err,
		                source_out_buffer[i] =
		                    cl::Buffer(context,
		                                CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX |
		                                    CL_MEM_USE_HOST_PTR,
		                                sizeof(int) * dataSize,
		                                &source_out_ext[i],
		                                &err));
		}
        q.finish();

        // Start timer
        double kernel_time_in_sec = 0;
        std::chrono::duration<double> kernel_time(0);
        auto kernel_start = std::chrono::high_resolution_clock::now();

        //Setting the compute kernel arguments
        dataSize = dataSize / WIDTH_FACTOR;
		for (int i = 0; i < NUM_KERNEL_PAIRS; i++) {
		    //Write Kernel
            OCL_CHECK(err, err = write_krnl[i].setArg(0, source_in_buffer[i])); 
		    OCL_CHECK(err, err = write_krnl[i].setArg(1, dataSize)); 
		    //Invoking the compute kernels
		    OCL_CHECK(err, err = q.enqueueTask(write_krnl[i]));
            //Read Kernel
		    OCL_CHECK(err, err = read_krnl[i].setArg(0, source_out_buffer[i])); 
		    OCL_CHECK(err, err = read_krnl[i].setArg(1, dataSize));   
            //Invoking the compute kernels
            OCL_CHECK(err, err = q.enqueueTask(read_krnl[i]));
		}
        q.finish();

        // Stop timer
        auto kernel_end = std::chrono::high_resolution_clock::now();
        kernel_time = std::chrono::duration<double>(kernel_end - kernel_start);
        kernel_time_in_sec = kernel_time.count();
        std::cout << "Execution time = " << kernel_time_in_sec << std::endl;
		double bw_result = payload * 4 * 0.000010000 / kernel_time_in_sec * 2;
        std::cout << "Payload Size: " << i*4/(1024.0*1024.0) << "MB - Bandwidth = " << bw_result << "GB/s"<< std::endl;
    }

    // Exit program
    return EXIT_SUCCESS;
}
