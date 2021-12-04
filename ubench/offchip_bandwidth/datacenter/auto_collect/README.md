## Off-chip Memory Bandwidth
   This microbenchmark measures the off-chip memory access bandwidth under different combinations of four parameters, including 1) the accelerator frequency of microbenchmark design 2) the number of concurrent memory access ports, 3) the data port width, 4) the maximum burst access length for each port, and 5) the size of consecutive data accesses. 
   
   Here we provide python scripts to automate the generation and synthesizing the microbenchmarks based on users' configurations of these five parameters. Here is a detailed guide on these configuration parameters through **(config.py)**. The generated designs are placed in ./uBenchDesignDir, and can use **(runAll.sh)** to automatically run though all the microbenchmark designs.
   
1. **Number of Concurrent Memory Ports**     
    **FPGA Kernel Configuration (config.py)**
    ```python
    NUM_CONCURRENT_PORT = [4]
    ```
    
2. **Memory Port Width**
    **FPGA Kernel Configuration (config.py)**
    ```python
    PORT_WIDTH = [128]
    ```

3. **Burst Access Length for Memory Ports**
    **FPGA Kernel Configuration (config.py)**
    ```python
    MAX_BURST_LENGTH = [16, 32, 64, 128, 256]
    ```

4. **Consecutive Data Access Size**
    **FPGA Kernel Configuration (config.py)**
    ```python
    CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in KB
    ```
    
5. **Memory Access Type**
    **FPGA Kernel Configuration (config.py)**
    ```python
   ACCESS_TYPE = ['RD', 'WR']
    ```

6. **DDR/HBM Connectivity**
    **FPGA Kernel Configuration (config.py)**
    ```python
   MEMORY_TYPE = [{'BANK_TYPE':'DDR', 'BANK_FLAG':'0 | XCL_MEM_TOPOLOGY', 'BANK_NAME':'DDR[0]', 'DEVICE_NAME':'xilinx_u200_xdma_201830_2'}, \
                  {'BANK_TYPE':'HBM', 'BANK_FLAG':'0 | XCL_MEM_TOPOLOGY', 'BANK_NAME':'HBM[0]', 'DEVICE_NAME':'xilinx_u280_xdma_201920_3'}]
    ```

7. **Accelerator Design Frequency**
    **FPGA Kernel Configuration (config.py)**
    ```python
    KERNEL_FREQ = [300]
    ```
