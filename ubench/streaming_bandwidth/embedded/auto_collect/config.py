#!/usr/bin/python 

'''---------------------------------------
#       User Configuration
---------------------------------------'''
# uBench parameters configurations
KERNEL_FREQ = [150]
NUM_CONCURRENT_PORT = [4]
NUM_KERNEL = 4
PORT_WIDTH = [128, 256, 512, 1024]
CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in 10MB
MEMORY_TYPE = {'BANK_TYPE':'DDR', 'DEVICE_NAME':'xilinx_zcu104_base_202020_1'}
