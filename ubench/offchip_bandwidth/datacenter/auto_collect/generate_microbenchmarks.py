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
            for max_burst_length in MAX_BURST_LENGTH:
                for access_type in ACCESS_TYPE:
                    for memory_type in MEMORY_TYPE:
                        # create microbenchmark directory
                        benchmarkDesignName = access_type + '_' + \
                                              memory_type['BANK_TYPE'] + '_' + str(kernel_freq) + 'MHz_' + \
                                              str(num_concurrent_port) + 'port_' + str(port_width) + 'bit_' + \
                                              str(max_burst_length) + 'max_burst_length'
                        benchmarkDesignDir = os.path.join(uBenchDesignDir, benchmarkDesignName)
                        os.mkdir(benchmarkDesignDir)
                        os.chdir(benchmarkDesignDir)
                        
                        # create makefile
                        generateMakefile(kernel_freq)

                        # create connectivity config
                        generateConnectivity(access_type, \
                                             num_concurrent_port, \
                                             memory_type['BANK_NAME'])
                        # create host code
                        srcDesignDir = os.path.join(benchmarkDesignDir, 'src')
                        os.mkdir(srcDesignDir)
                        os.chdir(srcDesignDir)
                        generateHostCode(access_type, \
                                         num_concurrent_port, \
                                         port_width, \
                                         CONSECUTIVE_DATA_SIZE['START_SIZE'], CONSECUTIVE_DATA_SIZE['STOP_SIZE'], \
                                         memory_type['BANK_FLAG'])
                    
                        # create kernel code
                        generateKernelCode(access_type, \
                                           num_concurrent_port, \
                                           port_width, \
                                           max_burst_length)

                        runall_script.append('cd ' + benchmarkDesignDir + ';' + '\n')
                        runall_script.append('make check TARGET=hw DEVICE=' + memory_type['DEVICE_NAME'] + ';' + '\n\n')

                        os.chdir(baseDir)

# create run-all script 
os.chdir(uBenchDesignDir)
with open(runall_script_name, 'w') as f:
    # go to start of file
    f.seek(0)
    # actually write the lines
    f.writelines(runall_script)


'''for choice in singlePE_template_config:
    os.mkdir(tmpDesignDir)
    os.chdir(tmpDesignDir)

    bw_utilization = Interpolate_Bandwidth (memory_type, choice['port_width'], choice['buf_size'])
    
    Generate_SinglePE_Design(N, D, Dist, K, choice['port_width'], choice['buf_size'], memory_type)
    Run_HLS_Synthesis(FPGA_part_name)
    d = Parse_Utilization('knn.prj/solution0/syn/report/krnl_partialKnn_csynth.rpt')
    design_choice_perf = '{:>10}, {:>4}, {:>4}, {:>4}, {:>10}, {:>10}, {:>10}, {:>7}, {:>7}, {:>7}, {:>7}, {:>7}'\
                         .format(N, D, Dist, K, choice['port_width'], choice['buf_size'], \
                                 bw_utilization, \
                                 d['BRAM'], d['DSP'], d['FF'], d['LUT'], d['URAM'])
    singlePEs_evaluation_file.append(design_choice_perf + "\n")

    os.chdir(baseDir)'''

print "Microbenchmark Generation Done!"
