#!/usr/bin/python
import os
import re
import math

def generateConnectivity(kernel_freq, device_name, num_kernel, num_concurrent_port):
    connectivity_file_name = 'zcu104.cfg'
    connectivity_file = []

    connectivity_file.append('platform=' + device_name + '\n')
    connectivity_file.append('debug=1' + '\n')
    connectivity_file.append('save-temps=1' + '\n')
    connectivity_file.append('' + '\n')
    connectivity_file.append('[clock]' + '\n')
    connectivity_file.append('defaultFreqHz=' + str(kernel_freq) + '000000' + '\n')
    connectivity_file.append('' + '\n')
    connectivity_file.append('[connectivity]' + '\n')

    for kernel_index in range(num_kernel):
        for port_index in range(num_concurrent_port):
            connectivity_file.append('stream_connect=krnl_streamWrite_' + str(kernel_index+1) + '_1'  + '.kout' + str(port_index+1) + ':'\
                                                    'krnl_streamRead_' + str(kernel_index+1) + '_1'  + '.kin' + str(port_index+1) + '\n')
        connectivity_file.append('' + '\n')

    connectivity_file.append('[profile]' + '\n')
    connectivity_file.append('data=all:all:all' + '\n')

    with open(connectivity_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(connectivity_file)

