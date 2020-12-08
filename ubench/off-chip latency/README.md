## Off-chip Memory Latency

   This microbenchmark measures the off-chip memory random-access latency under different 1) the data port width and 2) the size of the randomly accessed data arrary. The example microbenchmark we provide randomly accesses data array sizes from 64B to 1MB, at a 32bit data per access.

1. **Memory Port Width**
    To change the memory port width, update the port width define in the header file (**krnl_ubench.h**).
      ```c++
      const int DWIDTH = 32;
      ```

2. **Random Access Data Array**
    To change the random access data array size, update the 'payload' variable in the host code (**host.cpp**). Currently, 'payload' varies from 256 (1KB) to 262144 (1MB), since the data type is 32bit (4B) integer.
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
      ```ini
      [connectivity]
      slr=krnl_ubench_1:SLR0
      sp=krnl_ubench_1.in0:DDR[0]
      sp=krnl_ubench_1.in0_index:DDR[0]
      nk=krnl_ubench:1
      ```
