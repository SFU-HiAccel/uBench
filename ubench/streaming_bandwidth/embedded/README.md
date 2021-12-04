## Streaming Bandwidth

   This microbenchmark measures the accelerator-to-accelerator bandwidth under different combinations of four parameters, including 1) the accelerator frequency of microbenchmark design 2) the number of parallel streaming ports, 3) the data port width, and 4) the size of streaming data.
   
   Here we provide python scripts to automate the generation and synthesizing the microbenchmarks based on users' configurations of these four parameters. Here is a detailed guide on these configuration parameters through **(config.py)**. The generated designs are placed in ./uBenchDesignDir, and can use **(runAll.sh)** to automatically run though all the microbenchmark designs.
   
1. **Number of Parallel Streaming Ports**     
    **FPGA Kernel Configuration (config.py)**
    ```python
    NUM_CONCURRENT_PORT = [4]
    ```
    
2. **Memory Port Width**
    **FPGA Kernel Configuration (config.py)**
    ```python
    PORT_WIDTH = [128, 256, 512, 1024]
    ```
    
3. **Streaming Data Size**
    **FPGA Kernel Configuration (config.py)**
    ```python
    CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in units of 10MB
    ```

4. **Accelerator Design Frequency**
    **FPGA Kernel Configuration (config.py)**
    ```python
    KERNEL_FREQ = [150]
    ```
