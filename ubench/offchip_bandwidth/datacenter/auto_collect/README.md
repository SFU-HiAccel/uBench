## Off-chip Memory Bandwidth
   This microbenchmark measures the off-chip memory access bandwidth under different combinations of four parameters, including 1) the accelerator frequency of microbenchmark design 2) the number of concurrent memory access ports, 3) the data port width, 4) the maximum burst access length for each port, and 5) the size of consecutive data accesses. For read/write and DDR/HBM, we provide an example microbenchmark with 1) 300MHz design frequency, 2) two concurrent memory ports, 3) each port has a width of 512-bit, 4) the burst access length for the AXI port is the Vivado HLS default 16, and 5) the size of consecutive data accesses vary from 1KB to 1MB. 
   
1. **Number of Concurrent Memory Ports**
    To change the number of concurrent memory ports, follow the instruction below to update the host and FPGA kernel code.     
    **FPGA Kernel Code (krnl_ubench.cpp)**
    1. Update the number of AXI ports:
      ```c++
      void krnl_ubench(volatile INTERFACE_WIDTH* in0, volatile INTERFACE_WIDTH* in1, const int size) {
      #pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0   max_read_burst_length=16 
      #pragma HLS INTERFACE m_axi port=in1 offset=slave bundle=gmem1   max_read_burst_length=16 
      #pragma HLS INTERFACE s_axilite port=in0 bundle=control
      #pragma HLS INTERFACE s_axilite port=in1 bundle=control
      ...
      ```
    2. Update the number of temporary variables:
      ```c++
      volatile INTERFACE_WIDTH temp_data_0;
      volatile INTERFACE_WIDTH temp_data_1;
      ```
    3. Update the number of concurrently reading/writing loops:
      ```c++
      for (int i = 0; i < NUM_ITERATIONS; i++) {...}
      for (int i = 0; i < NUM_ITERATIONS; i++) {...}
      ```
    **Host Code (host.cpp)**
    1. Update the number of AXI ports:
      ```c++
      #define NUM_KERNEL 1
      #define NUM_PORT 2
      ```
    
2. **Memory Port Width**
    To change the memory port width, update the port width define in the header file (**krnl_ubench.h**).
      ```c++
      const int DWIDTH = 512;
      ```

3. **Burst Access Length for Memory Ports**
    To change the burst access length for memory Ports, update the the max_read_burst_length or max_write_burst_length parameter in the kernel code (**krnl_ubench.cpp**).
      ```c++
      void krnl_ubench(volatile INTERFACE_WIDTH* in0, volatile INTERFACE_WIDTH* in1, const int size) {
      #pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0   max_read_burst_length=16 
      #pragma HLS INTERFACE m_axi port=in1 offset=slave bundle=gmem1   max_read_burst_length=16 
      ...
      ```

4. **Consecutive Data Access Size**
    To change the consecutive data access size, update the 'payload' variable in the host code (**host.cpp**). Currently, 'payload' varies from 256 (1KB) to 262144 (1MB), since the data type is 32bit (4B) integer. 
      ```c++
      for (int payload(256); payload <= 262144; payload*=2){
      ```

5. **DDR/HBM Connectivity & Kernel Placement**
    To specifiy the off-chip memory type and kernel placement, update the buffer allocation flag in the host code (**host.cpp**) and the connectivity file (**ubench.ini**)
    **Host Code (host.cpp)**
      ```c++
      for (int i = 0; i < NUM_KERNEL*NUM_PORT; i++) {
          source_in_ext[i].obj = read_source.data();
          source_in_ext[i].param = 0;
          source_in_ext[i].flags = XCL_MEM_DDR_BANK1;
      }
      ```
    **Connectivity File (ubench.ini)**
       For more details on the Vitis compiler options and specifiers, please refer to this document: https://www.xilinx.com/support/documentation/sw_manuals/xilinx2020_1/ug1393-vitis-application-acceleration.pdf
      ```ini
      [connectivity]
      slr=krnl_ubench_1:SLR1
      sp=krnl_ubench_1.in0:DDR[1]
      sp=krnl_ubench_1.in1:DDR[1]
      nk=krnl_ubench:1
      ```

6. **Accelerator Design Frequency**
   To specifiy the design frequency of the accelerator, update the  in the makefile (**Makefile**) and the 
   ```
   # Kernel compiler global settings
   CLFLAGS += -t $(TARGET) --platform $(DEVICE) --save-temps --kernel_frequency 300
   ```
