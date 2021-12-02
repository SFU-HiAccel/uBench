#!/usr/bin/python 

'''---------------------------------------
#       User Configuration
---------------------------------------'''
# uBench parameters configurations
KERNEL_FREQ = [300]
NUM_CONCURRENT_PORT = [4]
PORT_WIDTH = [128]
MAX_BURST_LENGTH = [16, 32, 64, 128, 256]
CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in KB
ACCESS_TYPE = ['RD', 'WR']
MEMORY_TYPE = [{'BANK_TYPE':'DDR', 'BANK_FLAG':'0 | XCL_MEM_TOPOLOGY', 'BANK_NAME':'DDR[0]', 'DEVICE_NAME':'xilinx_u200_xdma_201830_2'}, \
               {'BANK_TYPE':'HBM', 'BANK_FLAG':'0 | XCL_MEM_TOPOLOGY', 'BANK_NAME':'HBM[0]', 'DEVICE_NAME':'xilinx_u280_xdma_201920_3'}]
