#!/usr/bin/python 

'''---------------------------------------
#       User Configuration
---------------------------------------'''
# uBench parameters configurations
KERNEL_FREQ = [150]
NUM_CONCURRENT_PORT = [4]
PORT_WIDTH = [128]
CONSECUTIVE_DATA_SIZE = {'START_SIZE':1, 'STOP_SIZE':1024} # in KB
ACCESS_TYPE = ['RD', 'WR']
MEMORY_TYPE = [{'BANK_TYPE':'DDR', 'PORT_NAMES':['HP0','HP1','HP2','HP3','HPC0','HPC1'], 'DEVICE_NAME':'xilinx_zcu104_base_202020_1'}]
