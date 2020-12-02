## Introduction

uBench is a set of HLS-based microbenchmarks to quantitatively evaluate the performance of the Xilinx Alveo FPGA memory systems under a comprehensive set of factors that affect the memory bandwidth, including 1) the number of concurrent memory access ports, 2) the data width of each port, 3) the maximum burst access length for each port, and 4) the size of consecutive data accesses. 

If you use uBench in your research, please cite our FPGA'2021 paper:
> Alec Lu, Zhenman Fang, Weihua Liu, Lesley Shannon. Demystifying the Memory System of Modern Datacenter FPGAs for Software Programmers through Microbenchmarking. 29th ACM/SIGDA International Symposium on Field-Programmable Gate Arrays (FPGA 2021). Virtual Conference, Mar 2021.

## Download uBench

        git clone https://github.com/SFU-HiAccel/uBench.git

## Environmental Setup

1. **Evaluated hardware platforms:**
    * **Host CPU:**
      * 64-bit Ubuntu 16.04.6 LTS
    * **Cloud FPGA:**
      * Xilinx Alveo U200 - DDR4-based FPGA
      * Xilinx Alveo U280 - HBM2-based FPGA

2. **Software tools:**
    * **HLS tool:**
      * Vitis 2019.2
      * Xilinx Runtime(XRT) 2019.2

## FPGA Memory System Microbenchmarking using uBench

* **Off-chip Memory <-> AXI Port Bandwidth**

* **AXIS port <-> AXIS port Streaming Bandwidth**

* **Latency**

## Case Study Benchmarking Algorithms: 

1. **K-Nearest Neighbors (KNN)**


2. **Sparse Matrix-Vector Multiplication (SpMV)**


## Contacts

Still have further questions about uBench? Please contact:

* **Alec Lu**, PhD Student

* HiAccel Lab & RCL Lab, Simon Fraser University (SFU)

* Email: alec_lu@sfu.ca 

* Website: http://www.sfu.ca/~fla30/
