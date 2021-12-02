#!/usr/bin/python 
import os
import re
import math 
import subprocess
import shutil
from config import *
from makefile_gen import generateMakefile
from connectivity_gen import generateConnectivity
from hostcode_gen import generateHostCode
from kernelcode_gen import generateKernelCode

baseDir = os.getcwd()
uBenchDesignDirName = 'uBenchDesignDir'
uBenchDesignDir = os.path.join(baseDir, uBenchDesignDirName)
os.mkdir(uBenchDesignDir)

runall_script_name = 'runAll.sh'
runall_script = []
runall_script.append('#!/bin/bash' + '\n\n')

for kernel_freq in KERNEL_FREQ:
    for num_concurrent_port in NUM_CONCURRENT_PORT:
        for port_width in PORT_WIDTH:
            for access_type in ACCESS_TYPE:
                for memory_type in MEMORY_TYPE:
                    # create microbenchmark directory
                    benchmarkDesignName = access_type + '_' + \
                                          str(kernel_freq) + 'MHz_' + \
                                          str(num_concurrent_port) + 'port_' + \
                                          str(port_width) + 'bit'
                    benchmarkDesignDir = os.path.join(uBenchDesignDir, benchmarkDesignName)
                    os.mkdir(benchmarkDesignDir)
                    os.chdir(benchmarkDesignDir)
                    
                    # create makefile
                    generateMakefile()

                    # create connectivity config
                    generateConnectivity(kernel_freq, \
                                         memory_type['DEVICE_NAME'], \
                                         access_type, \
                                         num_concurrent_port, \
                                         memory_type['PORT_NAMES'])
                    # create host code
                    srcDesignDir = os.path.join(benchmarkDesignDir, 'src')
                    os.mkdir(srcDesignDir)
                    os.chdir(srcDesignDir)
                    generateHostCode(access_type, \
                                     num_concurrent_port, \
                                     port_width, \
                                     CONSECUTIVE_DATA_SIZE['START_SIZE'], CONSECUTIVE_DATA_SIZE['STOP_SIZE'])
                
                    # create kernel code
                    generateKernelCode(access_type, \
                                       num_concurrent_port, \
                                       port_width)

                    runall_script.append('cd ' + benchmarkDesignDir + ';' + '\n')
                    runall_script.append('make;' + '\n\n')

                    os.chdir(baseDir)

# create run-all script 
os.chdir(uBenchDesignDir)
with open(runall_script_name, 'w') as f:
    # go to start of file
    f.seek(0)
    # actually write the lines
    f.writelines(runall_script)

print "Microbenchmark Generation Done!"
