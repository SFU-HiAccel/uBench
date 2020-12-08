## Off-chip Memory Bandwidth
   This microbenchmark measures the off-chip memory access bandwidth under different combinations of four parameters, including 1) the number of concurrent memory access ports, 2) the data port width, 3) the maximum burst access length for each port, and 4) the size of consecutive data accesses. For read/write and DDR/HBM, we provide an example microbenchmark with 1) two concurrent memory ports, 2) each port has a width of 512-bit, 3) the burst access length for the AXI port is the Vivado HLS default 16, and 4) the size of consecutive data accesses vary from 1KB to 1MB. 
   
1. **Number of Concurrent Memory Ports**
    To change the number of concurrent memory ports, follow the instruction below to update the host and FPGA kernel code.     
    **FPGA Kernel Code (krnl_ubench.cpp)**
    1. Update the number of AXI ports:
      ```c++
      4        void krnl_ubench(volatile INTERFACE_WIDTH* in0, volatile INTERFACE_WIDTH* in1, const int size) {
      5        #pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0   max_read_burst_length=16 
      6        #pragma HLS INTERFACE m_axi port=in1 offset=slave bundle=gmem1   max_read_burst_length=16 
      8        #pragma HLS INTERFACE s_axilite port=in0 bundle=control
      9        #pragma HLS INTERFACE s_axilite port=in1 bundle=control       
      ```
    2. Update the number of temporary variables:
      ```c++
      14        volatile INTERFACE_WIDTH temp_data_0;
      15        volatile INTERFACE_WIDTH temp_data_1;
      ```
    3. Update the number of concurrently reading/writing loops:
      ```c++
      19        for (int i = 0; i < NUM_ITERATIONS; i++) {...}
      26        for (int i = 0; i < NUM_ITERATIONS; i++) {...}
      ```
    **Host Code (host.cpp)**
    1. Update the number of AXI ports:
      ```c++
      16 #define NUM_PORT 2
      ```
    
2. **Memory Port Width**
    To change the memory port width, update the port width define in the header file (**krnl_ubench.h**).
      ```c++
      4 const int DWIDTH = 512;
      ```

3. **Burst Access Length for Memory Ports**
    To change the burst access length for memory Ports, update the the max_read_burst_length or max_write_burst_length parameter in the kernel code (**krnl_ubench.cpp**).
      ```c++
      4        void krnl_ubench(volatile INTERFACE_WIDTH* in0, volatile INTERFACE_WIDTH* in1, const int size) {
      5        #pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0   max_read_burst_length=16 
      6        #pragma HLS INTERFACE m_axi port=in1 offset=slave bundle=gmem1   max_read_burst_length=16 
      ```

4. **Consecutive Data Access Size**
    To change the consecutive data access size, update the 'payload' variable in the host code (**host.cpp**). Currently, 'payload' varies from 256 (1KB) to 262144 (1MB), since the data type is 32bit (4B) integer. 
      ```c++
    100        for (int payload(256); payload <= 262144; payload*=2){
    ```
