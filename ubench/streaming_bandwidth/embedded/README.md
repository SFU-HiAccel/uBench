## Streaming Bandwidth

   This microbenchmark measures the accelerator-to-accelerator streaming bandwidth under different combinations of three parameters, including 1) the number of parallel streaming data ports, 2) the data port width, and 3) the amount of streaming data. The example microbenchmark we provide has 1) two parallel streaming ports between a pair of read-write kernels, 2) each streaming port is 512-bit wide, and 3) the amount of streaming data size varies from ~10MB to ~10GB.
    
1. **Number of Parallel Accelerator-to-Accelerator Streaming Ports**
    To change the number of concurrent memory ports, follow the instruction below to update the FPGA kernel code and connectivity file.
    **FPGA Kernel Code (krnl_streamRead.cpp & krnl_streamWrite.cpp)**
    1. Update the number of AXIS ports:
      ```c++
      void krnl_streamRead(int* out0, const int size, hls::stream<pkt> &kin1, hls::stream<pkt> &kin2) {
      ...
      #pragma HLS INTERFACE axis port = kin1
      #pragma HLS INTERFACE axis port = kin2
      
      void krnl_streamWrite(int* in0, const int size, hls::stream<pkt> &kout1, hls::stream<pkt> &kout2) {
      ...
      #pragma HLS INTERFACE axis port = kout1
      #pragma HLS INTERFACE axis port = kout2
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
    **Connectivity File (uBench.ini)**
    1. Update the connectivity file:
      ```ini
      stream_connect=krnl_streamWrite_1.kout1:krnl_streamRead_1.kin1
      stream_connect=krnl_streamWrite_1.kout2:krnl_streamRead_1.kin2      
      ```    
    
2. **Memory Port Width**
    To change the memory port width, update the port width define in the header file (**krnl_ubench.h**).
      ```c++
      const int DWIDTH = 512;
      ```

3. **Consecutive Data Access Size**
    To change the consecutive data access size, update the 'payload' variable in the host code (**host.cpp**). Currently, 'payload' varies from 256 (1KB) to 262144 (1MB), since the data type is 32bit (4B) integer. Combined with NUM_ITERATIONS = 10,000, the streaming data size varies from ~10MB to ~10GB.
      ```c++
      for (int payload(256); payload <= 262144; payload*=2){
      ```
