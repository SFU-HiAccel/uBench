#include <algorithm>
#include <iostream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <ctime>

// This extension file is required for stream APIs
#include "CL/cl_ext_xilinx.h"
#include "xcl2.hpp"
#include "krnl_config.h"

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
#define MAX_DDR_BANKCOUNT 4 
const int ddr_bank[MAX_DDR_BANKCOUNT] = {
    XCL_MEM_DDR_BANK0, 
    XCL_MEM_DDR_BANK1, 
    XCL_MEM_DDR_BANK2, 
    XCL_MEM_DDR_BANK3};
// Function for verifying results
bool verify(std::vector<float, aligned_allocator<float>> &sw_out,
            std::vector<float, aligned_allocator<float>> &hw_out,
            unsigned int size) 
{
    bool check = true;
    int num_err = 0;
    for (unsigned int i=0; i<size; ++i) {
        if (sw_out[i] != hw_out[i]) {
            check = false;
            if (num_err < 10){
                std::cout << "Error: Result mismatch"
                          << std::endl;
                std::cout << "i = " << i
                          << " CPU result = " << sw_out[i] 
                          << " FPGA result = " << hw_out[i] 
                          << " Error delta = " << std::abs(sw_out[i]-hw_out[i])
                          << std::endl;
                num_err++;
            }else{
                break;
            }
        }
    }
    return check;
}

void Generate_sw_verif_data(std::vector<float, aligned_allocator<float>> &nzval_data, 
                            std::vector<int, aligned_allocator<int>> &cols_data, 
                            std::vector<float, aligned_allocator<float>> &vec_data, 
                            std::vector<float, aligned_allocator<float>> &sw_out, 
                            int num_row, int num_col){
    // Generate random float data
    std::fill(nzval_data.begin(), nzval_data.end(), 0.0);    
    std::fill(cols_data.begin(), cols_data.end(), 0);
    std::fill(vec_data.begin(), vec_data.end(), 0.0);
    std::fill(sw_out.begin(), sw_out.end(), 0.0);

    unsigned int data_size = num_row * num_col;
    unsigned int min = 0;
    unsigned int max = num_row-1;

    for (unsigned int i=0; i<data_size; ++i){
        nzval_data[i] = static_cast <float>(rand()) / static_cast<float>(RAND_MAX);
    }
    for (unsigned int i=0; i<data_size; ++i){
        cols_data[i] = min + (rand() % static_cast<int>(max - min + 1));
    }
    for (unsigned int i=0; i<num_row; ++i){
        vec_data[i] = static_cast <float>(rand()) / static_cast<float>(RAND_MAX);
    }

    for (int i=0; i<num_row; i++) {
        for (int j=0; j<num_col; j++){
            sw_out[i] += nzval_data[i*num_col + j] * vec_data[cols_data[i*num_col + j]];
        }
    }

    return;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <XCLBIN> \n", argv[0]);
        return -1;
    }

    std::srand(std::time(NULL));

    std::string binaryFile = argv[1];
    cl_int err;
    cl::CommandQueue q;
    std::string krnl_name = "krnl_partialspmv";
    std::vector<cl::Kernel> cmpt_krnl(NUM_KERNEL);
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

            valid_device++;
            break; // we break because we found a valid device
        }
    }
    if (valid_device == 0) {
        std::cout << "Failed to program any device found, exit!\n";
        exit(EXIT_FAILURE);
    }
    
    int num_row = N;
    int num_col = L;
    if (xcl::is_emulation()) {
        num_row = N; //1024;
        num_col = L; //1024;
    }
    int dataSize = num_row * num_col;
    
    std::vector<float, aligned_allocator<float>> nzval_data(num_row*num_col);
    std::vector<float, aligned_allocator<float>> nzval_data_part[NUM_KERNEL];
    std::vector<int, aligned_allocator<int>> cols_data(num_row*num_col);
    std::vector<int, aligned_allocator<int>> cols_data_part[NUM_KERNEL];
    std::vector<float, aligned_allocator<float>> vec_data(num_row);
    std::vector<float, aligned_allocator<float>> vec_data_part[NUM_KERNEL];
    std::vector<float, aligned_allocator<float>> sw_out(num_row);
    std::vector<float, aligned_allocator<float>> hw_out(num_row);
    std::vector<float, aligned_allocator<float>> hw_out_part[NUM_KERNEL];

    // Create the test data
    Generate_sw_verif_data(nzval_data, cols_data, vec_data, sw_out, num_row, num_col);
    // Partition the full matrix into separate submatrices
    int starting_idx = 0;
    int part_size = dataSize/NUM_KERNEL;
    for (int i = 0; i < NUM_KERNEL; ++i) {
        starting_idx = i*part_size;
        nzval_data_part[i].resize(part_size);
        for (int j = 0; j < part_size; ++j){
            nzval_data_part[i][j] = nzval_data[starting_idx+j];
        }
        cols_data_part[i].resize(part_size);
        for (int j = 0; j < part_size; ++j){
            cols_data_part[i][j] = cols_data[starting_idx+j];
        }
        vec_data_part[i].resize(num_row);
        for (int j = 0; j < num_row; ++j){
            vec_data_part[i][j] = vec_data[j];
        }
        hw_out_part[i].resize(num_row/NUM_KERNEL);
        for (int j = 0; j < num_row/NUM_KERNEL; ++j){
            hw_out_part[i][j] = 0.0;
        }
    }
    // Initializing hw output vectors to zero
    std::fill(hw_out.begin(), hw_out.end(), 0.0);

    std::vector<cl_mem_ext_ptr_t> nzvalBufExt(NUM_KERNEL);
    std::vector<cl_mem_ext_ptr_t> colsBufExt(NUM_KERNEL);
    std::vector<cl_mem_ext_ptr_t> vecBufExt(NUM_KERNEL);
    std::vector<cl_mem_ext_ptr_t> outBufExt(NUM_KERNEL);

    // For Allocating Buffer to specific Global Memory Bank, user has to use cl_mem_ext_ptr_t
    // and provide the Banks
    if (xcl::is_emulation()) {
    	printf("Emulation Mode \n");
        for (int i = 0; i < NUM_KERNEL; i++) {
            nzvalBufExt[i].obj = nzval_data_part[i].data();
            nzvalBufExt[i].param = 0;
            nzvalBufExt[i].flags = ddr_bank[1];
            colsBufExt[i].obj = cols_data_part[i].data();
            colsBufExt[i].param = 0;
            colsBufExt[i].flags = ddr_bank[1];
            vecBufExt[i].obj = vec_data_part[i].data();
            vecBufExt[i].param = 0;
            vecBufExt[i].flags = ddr_bank[1];
            outBufExt[i].obj = hw_out_part[i].data();
            outBufExt[i].param = 0;
            outBufExt[i].flags = ddr_bank[1];           
        }
    }
    else{
        int num_PE_per_bank[] = {7, 7, 7, 7};
        for (int i = 0; i < NUM_KERNEL; i++) {
            nzvalBufExt[i].obj = nzval_data_part[i].data();
            nzvalBufExt[i].param = 0;
            nzvalBufExt[i].flags = ddr_bank[0];
            colsBufExt[i].obj = cols_data_part[i].data();
            colsBufExt[i].param = 0;
            colsBufExt[i].flags = ddr_bank[0];
            vecBufExt[i].obj = vec_data_part[i].data();
            vecBufExt[i].param = 0;
            vecBufExt[i].flags = ddr_bank[0];
            outBufExt[i].obj = hw_out_part[i].data();
            outBufExt[i].param = 0;
            outBufExt[i].flags = ddr_bank[0];
        }
        int PE_idx = 0;
        for (int i=0; i < 4; ++i){
            for (int j=0; j<num_PE_per_bank[i]; ++j){
                nzvalBufExt[PE_idx].flags = ddr_bank[i];
                colsBufExt[PE_idx].flags = ddr_bank[i];
                vecBufExt[PE_idx].flags = ddr_bank[i];
                outBufExt[PE_idx].flags = ddr_bank[i];
                PE_idx++;
            }
        }
        nzvalBufExt[28].flags = ddr_bank[1];
        colsBufExt[28].flags = ddr_bank[0];
        vecBufExt[28].flags = ddr_bank[0];
        outBufExt[28].flags = ddr_bank[0];

        nzvalBufExt[29].flags = ddr_bank[2];
        colsBufExt[29].flags = ddr_bank[3];
        vecBufExt[29].flags = ddr_bank[3];
        outBufExt[29].flags = ddr_bank[3];
    }

    std::vector<cl::Buffer> buffer_nzval(NUM_KERNEL);
    std::vector<cl::Buffer> buffer_cols(NUM_KERNEL);
    std::vector<cl::Buffer> buffer_vec(NUM_KERNEL);
    std::vector<cl::Buffer> buffer_out(NUM_KERNEL);

    // These commands will allocate memory on the FPGA. The cl::Buffer objects can
    // be used to reference the memory locations on the device.
    //Creating Buffers
    for (int i = 0; i < NUM_KERNEL; i++) {
        OCL_CHECK(err, buffer_nzval[i] =
                                cl::Buffer(context,
                                CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX | CL_MEM_USE_HOST_PTR,
                                sizeof(float) * part_size,
                                &nzvalBufExt[i],
                                &err));
        OCL_CHECK(err, buffer_cols[i] =
                                cl::Buffer(context,
                                CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX | CL_MEM_USE_HOST_PTR,
                                sizeof(int) * part_size,
                                &colsBufExt[i],
                                &err));
        OCL_CHECK(err, buffer_vec[i] =
                                cl::Buffer(context,
                                CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX | CL_MEM_USE_HOST_PTR,
                                sizeof(float) * num_row,
                                &vecBufExt[i],
                                &err));
        OCL_CHECK(err, buffer_out[i] =
                                cl::Buffer(context,
                                CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX | CL_MEM_USE_HOST_PTR,
                                sizeof(float) * num_row / NUM_KERNEL,
                                &outBufExt[i],
                                &err));                                     
    }                        

    // Copy input data to Device Global Memory
    for (int i = 0; i < NUM_KERNEL; i++) {
        OCL_CHECK(err,
                  err = q.enqueueMigrateMemObjects(
                      {buffer_nzval[i], buffer_cols[i], buffer_vec[i]},
                      0 /* 0 means from host*/));
    }
    q.finish();

    // Start timer
    double kernel_time_in_sec = 0, result = 0;
    std::chrono::duration<double> kernel_time(0);
    auto kernel_start = std::chrono::high_resolution_clock::now();
    
    for (int i=0; i<NUM_KERNEL; ++i){
        //Setting the compute kernel arguments
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(0, buffer_nzval[i]));
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(1, buffer_cols[i]));
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(2, buffer_vec[i]));
        OCL_CHECK(err, err = cmpt_krnl[i].setArg(3, buffer_out[i]));
        //Invoking the compute kernels
        OCL_CHECK(err, err = q.enqueueTask(cmpt_krnl[i]));
    }
    q.finish();

    // Stop timer
    auto kernel_end = std::chrono::high_resolution_clock::now();
    kernel_time = std::chrono::duration<double>(kernel_end - kernel_start);
    kernel_time_in_sec = kernel_time.count();
    std::cout << "Execution time = " << kernel_time_in_sec << std::endl;

    // Copy Result from Device Global Memory to Host Local Memory
    for (int i=0; i<NUM_KERNEL; ++i){
        OCL_CHECK(err, err = q.enqueueMigrateMemObjects(
                    {buffer_out[i]}, 
                    CL_MIGRATE_MEM_OBJECT_HOST));
    }
    q.finish();

    // Merge 'out' data
    for (int i=0; i<NUM_KERNEL; ++i){
        int start_idx = i * num_row / NUM_KERNEL;
        for (int j=0; j<num_row/NUM_KERNEL; ++j){
            hw_out[start_idx+j] = hw_out_part[i][j];
        }
    }    

    bool match = true;
    match = verify(sw_out, hw_out, num_row);
    //OPENCL HOST CODE AREA ENDS

    std::cout << (match ? "TEST PASSED" : "TEST FAILED") << std::endl;
    return (match ? EXIT_SUCCESS : EXIT_FAILURE);
}
