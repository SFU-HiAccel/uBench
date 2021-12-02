#!/usr/bin/python
import os
import re
import math

def generateConnectivity(access_type, num_concurrent_port, bank_name):
    connectivity_file_name = 'ubench.ini'
    connectivity_file = []

    connectivity_file.append('[connectivity]' + '\n')
    connectivity_file.append('slr=krnl_ubench_1:SLR0' + '\n')

    for port_index in range(num_concurrent_port):
        if (access_type == 'RD'):
            connectivity_file.append('sp=krnl_ubench_1.in' + str(port_index) + ':' + bank_name + '\n')
        elif (access_type == 'WR'):
            connectivity_file.append('sp=krnl_ubench_1.out' + str(port_index) + ':' + bank_name + '\n')
        else:
            print('Invalid access type.')

    connectivity_file.append('nk=krnl_ubench:1' + '\n')

    with open(connectivity_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(connectivity_file)

