## Off-chip Memory Bandwidth
   This microbenchmark measures the off-chip memory access bandwidth under different combinations of four parameters, including 1) the accelerator frequency of microbenchmark design 2) the number of concurrent memory access ports, 3) the data port width, and 4) the size of consecutive data accesses. 
   
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

3. **Consecutive Data Access Size**
    **FPGA Kernel Configuration (config.py)**
    ```python
    CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in KB
    ```
    
4. **Memory Access Type**
    **FPGA Kernel Configuration (config.py)**
    ```python
   ACCESS_TYPE = ['RD', 'WR']
    ```

5. **Memory Port Connectivity**
    **FPGA Kernel Configuration (config.py)**
    ```python
   MEMORY_TYPE = [{'BANK_TYPE':'DDR', 'PORT_NAMES':['HP0','HP1','HP2','HP3','HPC0','HPC1'], 'DEVICE_NAME':'xilinx_zcu104_base_202020_1'}]
    ```

6. **Accelerator Design Frequency**
    **FPGA Kernel Configuration (config.py)**
    ```python
    KERNEL_FREQ = [150]
    ```
