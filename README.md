## Introduction

uBench is a set of HLS-based microbenchmarks to quantitatively evaluate the performance of the Xilinx Alveo FPGA memory systems under a comprehensive set of factors that affect the memory bandwidth, including 1) the clock frequency of the accelerator design, 2) the number of concurrent memory access ports, 3) the data width of each port, 4) the maximum burst access length for each port, and 5) the size of consecutive data accesses. 

If you use uBench in your research, please cite our paper(s):
> Alec Lu, Zhenman Fang, Weihua Liu, Lesley Shannon. Demystifying the Memory System of Modern Datacenter FPGAs for Software Programmers through Microbenchmarking. 29th ACM/SIGDA International Symposium on Field-Programmable Gate Arrays (FPGA 2021). Virtual Conference, Mar 2021.

## Download uBench

        git clone https://github.com/SFU-HiAccel/uBench.git

## Environmental Setup

1. **Evaluated hardware platforms:**
    * **Host CPU:**
      * 64-bit Ubuntu 18.04.2 LTS
    * **Cloud FPGA:**
      * Xilinx Alveo U200 - DDR4-based FPGA
      * Xilinx Alveo U280 - HBM2-based FPGA
    * **Embedded FPGA:**
      * Xilinx Zynq UltraScale+ MPSoC ZCU104 - DDR4-based FPGA

2. **Software tools:**
    * **HLS tool:**
      * Vitis 2020.2
      * Xilinx Runtime(XRT) 2020.2

## FPGA Memory System Microbenchmarking using uBench

Currently, uBench includes the following three types of microbenchmarks.

* **Off-chip Memory Bandwidth**

    This microbenchmark measures the off-chip memory access bandwidth under different combinations of five parameters, including 1) the clock frequency of the accelerator design, 2) the number of concurrent memory access ports, 3) the data port width, 4) the maximum burst access length for each port, and 5) the size of consecutive data accesses. 
    
    For read/write and DDR/HBM, we provide example microbenchmarks with 1) 300MHz accelerator frequency, 2) two concurrent memeory ports, 3) each port has a width of 512-bit, 4) the burst access length for the AXI port is the Vivado HLS default 16, and 5) the size of consecutive data accesses vary from 1KB to 1MB. [Here](https://github.com/SFU-HiAccel/uBench/tree/2020.2/ubench/offchip_bandwidth/datacenter) is a detailed guide on the code changes required to **manually** vary these parameters.
    
    We also provide python scripts to **automate** the generation and synthesizing the microbenchmarks based on users' configurations of these five parameters. [Here](https://github.com/SFU-HiAccel/uBench/tree/2020.2/ubench/offchip_bandwidth/datacenter/auto_collect) is a detailed guide on these configuration parameters.

* **Streaming Bandwidth**

    This microbenchmark measures the accelerator-to-accelerator streaming bandwidth under different combinations of three parameters, including 1) the clock frequency of the accelerator design, 2) the number of parallel streaming data ports, 3) the data port width, and 4) the amount of streaming data. 
    
    The example microbenchmark we provide runs at 1) 300MHz, has 2) two parallel streaming ports between a pair of read-write kernels, 3) each streaming port is 512-bit wide, and 4) the amount of streaming data size varies from ~10MB to ~10GB. [Here](https://github.com/SFU-HiAccel/uBench/tree/2020.2/ubench/streaming_bandwidth/datacenter) is a detailed guide on the code changes required to **manually** vary these parameters.
    
    We also provide python scripts to **automate** the generation and synthesizing the microbenchmarks based on users' configurations of these four parameters. [Here](https://github.com/SFU-HiAccel/uBench/tree/2020.2/ubench/streaming_bandwidth/datacenter/auto_collect) is a detailed guide on these configuration parameters.

* **off-chip Memory Latency**

    This microbenchmark measures the off-chip memory random-access latency under different 1) the data port width and 2) the size of the randomly accessed data arrary. The example microbenchmark we provide randomly accesses data array sizes from 64B to 1MB, at a 32bit data per access. [Here](https://github.com/SFU-HiAccel/uBench/tree/main/ubench/off-chip_latency) is a detailed guide on the code changes required to vary these parameters.

## Case Study Benchmarking Algorithms: 

1. **K-Nearest Neighbors (KNN)**
The KNN algorithm is widely used in many computational demanding applications including image classification, similarity search, and big-data query search. For this case study, we apply a series of HLS optimization techniques and demonstrate the pratical usage of our memory system insights when designing HLS-based KNN accelerator using the software code from the Rodinia benchmark suite - https://github.com/yuhc/gpu-rodinia.git. Here we include the four designs with the configurations enlisted in Table 2, and discussed in Section 5 of our paper. For a more generalized KNN accelerator design, please refer to our CHIP-KNN project available at: https://github.com/SFU-HiAccel/CHIP-KNN.git 

2. **Sparse Matrix-Vector Multiplication (SpMV)**
The SpMV algorithm is widely used in computational demanding applications like graph processing and machine learning. For this case study, we apply a series of HLS optimization techniques and demonstrate the pratical usage of our memory system insights when designing HLS-based SpMV accelerator using the software code from the MachSuite benchmark suite - https://github.com/breagen/MachSuite.git. Here we include the four designs with the configurations enlisted in Table 4, and discussed in Section 6 of our paper.

## Contacts

Still have further questions about uBench? Please contact:

* **Alec Lu**, PhD Student

* HiAccel Lab & RCL Lab, Simon Fraser University (SFU)

* Email: alec_lu@sfu.ca 

* Website: http://www.sfu.ca/~fla30/
