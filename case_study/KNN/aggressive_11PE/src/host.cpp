#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <ctime>
#include <cmath>

// This extension file is required for stream APIs
#include "CL/cl_ext_xilinx.h"
#include "xcl2.hpp"

#define NUM_KERNEL 11
#define TOP 10
#define INPUT_DIM 2

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

bool verify(std::vector<float, aligned_allocator<float>> &sw_results,
            std::vector<float, aligned_allocator<float>> &hw_results,
            unsigned int size) 
{
    bool check = true;
    for (unsigned int i=0; i<size; ++i) {
        if (sw_results[i] != hw_results[i]) {
            std::cout << "Error: Result mismatch"
                      << std::endl;
            std::cout << "i = " << i
                      << " CPU result = " << sw_results[i]
                      << " FPGA result = " << hw_results[i]
                      << " Error delta = " << std::abs(sw_results[i]-hw_results[i])
                      << std::endl;
            check = false;
        }
    }
    return check;
}

void Generate_sw_verif_data(std::vector<float, aligned_allocator<float>> &query,
                            std::vector<float, aligned_allocator<float>> &searchSpace,
                            std::vector<float, aligned_allocator<float>> &kNearstNeighbors,
                            unsigned int num_of_points)
{
    // Generate random float data
    std::fill(query.begin(), query.end(), 0.0);    
    std::fill(searchSpace.begin(), searchSpace.end(), 0.0);
    std::fill(kNearstNeighbors.begin(), kNearstNeighbors.end(), 0.0);

    for (unsigned int i=0; i<INPUT_DIM; ++i){
        query[i] = static_cast <float>(rand()) / static_cast<float>(RAND_MAX);
    }
    for (unsigned int i=0; i<num_of_points*INPUT_DIM; ++i){
        searchSpace[i] = static_cast <float>(rand()) / static_cast<float>(RAND_MAX);
    }

    // Calculate distance result
    float delta_squared_sum=0.0;
    float delta=0.0;
    std::vector<float, aligned_allocator<float>> distance(num_of_points);
    for (unsigned int i=0; i<num_of_points; ++i){
        delta_squared_sum = 0.0;    
        for (unsigned int j=0; j<INPUT_DIM; ++j){
            delta = query[j] - searchSpace[i*INPUT_DIM+j];
            delta_squared_sum += delta * delta;
        }
        //distance[i] = std::sqrt(delta_squared_sum);
		distance[i] = delta_squared_sum;
    }

    // Sort distance
    std::sort(distance.begin(), distance.end());    
    for (int i(0); i<TOP; ++i){
        kNearstNeighbors[i] = distance[TOP-1-i];
    }

    return;
}

int main(int argc, char *argv[]) 
{
    std::srand(std::time(NULL));

    if (argc != 2) {
        printf("Usage: %s <XCLBIN> \n", argv[0]);
        return -1;
    }

    std::string binaryFile = argv[1];
    cl_int err;
    cl::CommandQueue q;
    std::string krnl_name = "krnl_partialKnn";
    std::vector<cl::Kernel> cmpt_krnl(NUM_KERNEL);
    cl::Kernel merge_krnl;
    cl::Context context;

    // OPENCL HOST CODE AREA START
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

            for (int i = 0; i < NUM_KERNEL; i++) {
                std::string cu_id = std::to_string(i + 1);
                std::string krnl_name_full =
                    krnl_name + ":{" + krnl_name + "_" + cu_id + "}";

                printf("Creating a kernel [%s] for CU(%d)\n",
                       krnl_name_full.c_str(),
                       i + 1);
                //Here Kernel object is created by specifying kernel name along with compute unit.
                //For such case, this kernel object can only access the specific Compute unit
                OCL_CHECK(err, cmpt_krnl[i] = cl::Kernel(program, krnl_name_full.c_str(), &err));
            }
            std::string krnl_name_full = "krnl_globalSort:{krnl_globalSort_1}";            
            OCL_CHECK(err, merge_krnl = cl::Kernel(program, krnl_name_full.c_str(), &err));

            valid_device++;
            break; // we break because we found a valid device
        }
    }
    if (valid_device == 0) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }

    unsigned int num_of_points = 16384 * 264; // 131072 bytes / 2 dimensions / 4 bytes *260
    //reducing the test data capacity to run faster in emulation mode
    if (xcl::is_emulation()) {
        num_of_points = 16384 * 264;
    }

    std::cout << "Number of search space Points = " << num_of_points << std::endl
              << "Numer of dimensions per point = " << INPUT_DIM << std::endl;

    std::vector<float, aligned_allocator<float>> query_data(INPUT_DIM);
    std::vector<float, aligned_allocator<float>> searchspace_data(num_of_points*INPUT_DIM);
    std::vector<float, aligned_allocator<float>> kNN_sw(TOP);
    std::vector<float, aligned_allocator<float>> kNN_hw(TOP);
    std::vector<int, aligned_allocator<int>> kNN_hw_id(TOP);

    // Create the test data
    Generate_sw_verif_data(query_data, searchspace_data, kNN_sw, num_of_points);
    // Initializing hw output vectors to zero
    std::fill(kNN_hw.begin(), kNN_hw.end(), 0.0);
    std::fill(kNN_hw_id.begin(), kNN_hw_id.end(), 0);

    //Partition input data for multiple kernels
    std::vector<float, aligned_allocator<float>> searchspace_data_part[NUM_KERNEL];
    int starting_idx = 0;
    int partition_size = num_of_points*INPUT_DIM/NUM_KERNEL;    
    for (int i = 0; i < NUM_KERNEL; ++i) {
        starting_idx = i*partition_size;
        searchspace_data_part[i].resize(partition_size);
        for (int j = 0; j < partition_size; ++j){
            searchspace_data_part[i][j] = searchspace_data[starting_idx+j];
        }     
    }

    std::vector<cl_mem_ext_ptr_t> query_data_BufExt(NUM_KERNEL);
    std::vector<cl_mem_ext_ptr_t> searchspace_data_BufExt(NUM_KERNEL);
    cl_mem_ext_ptr_t kNN_hw_BufExt;
    cl_mem_ext_ptr_t kNN_hw_id_BufExt;

    // For Allocating Buffer to specific Global Memory Bank, user has to use cl_mem_ext_ptr_t
    // and provide the Banks
    if (xcl::is_emulation()) {
	    for (int i = 0; i < NUM_KERNEL; i++) {
		    query_data_BufExt[i].obj = query_data.data();
		    query_data_BufExt[i].param = 0;
		    query_data_BufExt[i].flags = XCL_MEM_DDR_BANK1;
		    searchspace_data_BufExt[i].obj = searchspace_data_part[i].data();
		    searchspace_data_BufExt[i].param = 0;
		    searchspace_data_BufExt[i].flags = XCL_MEM_DDR_BANK1;
		}

		kNN_hw_BufExt.obj = kNN_hw.data();
        kNN_hw_BufExt.param = 0;
        kNN_hw_BufExt.flags = XCL_MEM_DDR_BANK1;  
        kNN_hw_id_BufExt.obj = kNN_hw_id.data();
        kNN_hw_id_BufExt.param = 0;
        kNN_hw_id_BufExt.flags = XCL_MEM_DDR_BANK1;          
    }
    else{
	    for (int i = 0; i < NUM_KERNEL; i++) {
		    query_data_BufExt[i].obj = query_data.data();
		    query_data_BufExt[i].param = 0;
		    query_data_BufExt[i].flags = XCL_MEM_DDR_BANK0;
		    searchspace_data_BufExt[i].obj = searchspace_data_part[i].data();
		    searchspace_data_BufExt[i].param = 0;
		    searchspace_data_BufExt[i].flags = XCL_MEM_DDR_BANK0;
		}

		kNN_hw_BufExt.obj = kNN_hw.data();
        kNN_hw_BufExt.param = 0;
        kNN_hw_BufExt.flags = XCL_MEM_DDR_BANK0; 
        kNN_hw_id_BufExt.obj = kNN_hw_id.data();
        kNN_hw_id_BufExt.param = 0;
        kNN_hw_id_BufExt.flags = XCL_MEM_DDR_BANK0;   
    }

    std::vector<cl::Buffer> buffer_query_data(NUM_KERNEL);
    std::vector<cl::Buffer> buffer_searchspace_data(NUM_KERNEL);
    cl::Buffer buffer_kNN_hw;
    cl::Buffer buffer_kNN_hw_id;

    // These commands will allocate memory on the FPGA. The cl::Buffer objects can
    // be used to reference the memory locations on the device.
    //Creating Buffers
    for (int i = 0; i < NUM_KERNEL; i++) {
        OCL_CHECK(err,
                    buffer_query_data[i] =
                        cl::Buffer(context,
                                    CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX |
                                        CL_MEM_USE_HOST_PTR,
                                    sizeof(float) * INPUT_DIM,
                                    &query_data_BufExt[i],
                                    &err));
        OCL_CHECK(err,
                    buffer_searchspace_data[i] =
                        cl::Buffer(context,
                                    CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX |
                                        CL_MEM_USE_HOST_PTR,
                                    sizeof(float) * num_of_points * INPUT_DIM / NUM_KERNEL,
                                    &searchspace_data_BufExt[i],
                                    &err));
    }
    OCL_CHECK(err,
            buffer_kNN_hw =
                cl::Buffer(context,
                            CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX |
                                CL_MEM_USE_HOST_PTR,
                            sizeof(float) * TOP,
                            &kNN_hw_BufExt,
                            &err));
    OCL_CHECK(err,
            buffer_kNN_hw_id =
                cl::Buffer(context,
                            CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX |
                                CL_MEM_USE_HOST_PTR,
                            sizeof(int) * TOP,
                            &kNN_hw_id_BufExt,
                            &err));

    // Copy input data to Device Global Memory
    for (int i = 0; i < NUM_KERNEL; i++) {
        OCL_CHECK(err,
                    err = q.enqueueMigrateMemObjects(
                        {buffer_query_data[i], buffer_searchspace_data[i]},
                        0 /* 0 means from host*/));
    }
    q.finish();

    // Start timer
    double kernel_time_in_sec = 0;
    std::chrono::duration<double> kernel_time(0);
    auto kernel_start = std::chrono::high_resolution_clock::now();

    //Setting the compute kernel arguments
    for (int i = 0; i < NUM_KERNEL; i++) {
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(0, buffer_query_data[i])); 
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(1, buffer_searchspace_data[i])); 
        //Invoking the compute kernels
        OCL_CHECK(err, err = q.enqueueTask(cmpt_krnl[i]));
    }
    int krnl_idx = NUM_KERNEL*2;
    OCL_CHECK(err, err = merge_krnl.setArg(krnl_idx, buffer_kNN_hw)); 
    OCL_CHECK(err, err = merge_krnl.setArg(krnl_idx+1, buffer_kNN_hw_id)); 
    OCL_CHECK(err, err = q.enqueueTask(merge_krnl));
    q.finish();

    // Stop timer
    auto kernel_end = std::chrono::high_resolution_clock::now();
    kernel_time = std::chrono::duration<double>(kernel_end - kernel_start);
    kernel_time_in_sec = kernel_time.count();
    std::cout << "Execution time = " << kernel_time_in_sec << std::endl;

    // Copy Result from Device Global Memory to Host Local Memory
    OCL_CHECK(err, err = q.enqueueMigrateMemObjects(
                   {buffer_kNN_hw, buffer_kNN_hw_id}, CL_MIGRATE_MEM_OBJECT_HOST));
    q.finish();

    bool match = true;
    match = verify(kNN_sw, kNN_hw, TOP);
    //OPENCL HOST CODE AREA ENDS

    std::cout << (match ? "TEST PASSED" : "TEST FAILED") << std::endl;
    return (match ? EXIT_SUCCESS : EXIT_FAILURE);
}
