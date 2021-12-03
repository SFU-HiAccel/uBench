#!/usr/bin/python
import os
import re
import math

def generateConnectivity(num_kernel, num_concurrent_port, bank_name):
    connectivity_file_name = 'ubench.ini'
    connectivity_file = []

    connectivity_file.append('[connectivity]' + '\n')

    for kernel_index in range(num_kernel):
        connectivity_file.append('slr=krnl_streamWrite_' + str(kernel_index+1) + ':SLR0' + '\n')
        connectivity_file.append('sp=krnl_streamWrite_' + str(kernel_index+1) + '.in0:' + bank_name + '\n')
        connectivity_file.append('slr=krnl_streamRead_' + str(kernel_index+1) + ':SLR0' + '\n')
        connectivity_file.append('sp=krnl_streamRead_' + str(kernel_index+1) + '.out0:' + bank_name + '\n')
        for port_index in range(num_concurrent_port):
            connectivity_file.append('stream_connect=krnl_streamWrite_' + str(kernel_index+1) + '.kout' + str(port_index+1) + ':'\
                                                    'krnl_streamRead_' + str(kernel_index+1) + '.kin' + str(port_index+1) + '\n')
        connectivity_file.append('' + '\n')

    connectivity_file.append('nk=krnl_streamWrite:' + str(num_kernel)  + '\n')
    connectivity_file.append('nk=krnl_streamRead:' + str(num_kernel)  + '\n')

    with open(connectivity_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(connectivity_file)

