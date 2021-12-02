#!/usr/bin/python
import os
import re
import math

def generateConnectivity(kernel_freq, device_name, access_type, num_concurrent_port, port_names):
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
    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            connectivity_file.append('sp=krnl_ubench_1.in' + str(port_index) + ':' + port_names[port_index] + '\n')
        elif (access_type == 'WR'):
            connectivity_file.append('sp=krnl_ubench_1.out' + str(port_index) + ':' + port_names[port_index] + '\n')
        else:
            print('Invalid access type.')

    connectivity_file.append('[profile]' + '\n')
    connectivity_file.append('data=all:all:all' + '\n')

    with open(connectivity_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(connectivity_file)

