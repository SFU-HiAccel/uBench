#!/usr/bin/python 

'''---------------------------------------
#       User Configuration
---------------------------------------'''
# uBench parameters configurations
KERNEL_FREQ = [300]
NUM_CONCURRENT_PORT = [4]
NUM_KERNEL = 4
PORT_WIDTH = [128, 256, 512, 1024]
CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':4096} # in KB
MEMORY_TYPE = {'BANK_TYPE':'DDR', 'BANK_FLAG':'0 | XCL_MEM_TOPOLOGY', 'BANK_NAME':'DDR[0]', 'DEVICE_NAME':'xilinx_u200_xdma_201830_2'}
