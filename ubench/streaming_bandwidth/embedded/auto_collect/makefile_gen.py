#!/usr/bin/python
import os
import re
import math

def generateMakefile(num_kernel):
    make_file_name = 'Makefile'
    make_file = []

    make_file.append('ndef = $(if $(value $(1)),,$(error $(1) must be set prior to running))' + '\n')
    make_file.append('' + '\n')
    make_file.append('all: package/sd_card.img' + '\n')
    make_file.append('' + '\n')
    make_file.append('app.exe: ./src/host.cpp' + '\n')
    make_file.append('\t' + '$(call ndef,SDKTARGETSYSROOT)' + '\n')
    make_file.append('\t' + '$(CXX) -Wall -g -std=c++11 ./src/host.cpp -o app.exe \\' + '\n')
    make_file.append('\t' + '-I/usr/include/xrt \\' + '\n')
    make_file.append('\t' + '-lOpenCL -lpthread -lrt -lstdc++' + '\n')
    make_file.append('' + '\n')
    for kernel_index in range(num_kernel):
        make_file.append('krnl_streamWrite_' + str(kernel_index+1) + '.xo: ./src/krnl_streamWrite_' + str(kernel_index+1) + '.cpp' + '\n')
        make_file.append('\t' + 'v++ -c -t ${TARGET} --config ./zcu104.cfg -k krnl_streamWrite_'+ str(kernel_index+1) +' -I./../include -I./src ./src/krnl_streamWrite_'+ str(kernel_index+1) +'.cpp -o krnl_streamWrite_'+ str(kernel_index+1) +'.xo' + '\n')
        make_file.append('' + '\n')
        make_file.append('krnl_streamRead_' + str(kernel_index+1) + '.xo: ./src/krnl_streamRead_' + str(kernel_index+1) + '.cpp' + '\n')
        make_file.append('\t' + 'v++ -c -t ${TARGET} --config ./zcu104.cfg -k krnl_streamRead_'+ str(kernel_index+1) +' -I./../include -I./src ./src/krnl_streamRead_'+ str(kernel_index+1) +'.cpp -o krnl_streamRead_'+ str(kernel_index+1) +'.xo' + '\n')
        make_file.append('' + '\n')
    tmp_str = ''
    for kernel_index in range(num_kernel):
        tmp_str += './krnl_streamWrite_' + str(kernel_index+1) + '.xo ' + './krnl_streamRead_' + str(kernel_index+1) + '.xo '
    make_file.append('krnl_ubench.xclbin: ' + tmp_str + '\n')
    make_file.append('\t' + 'v++ -l -t ${TARGET} --config ./zcu104.cfg ' + tmp_str  + '-o krnl_ubench.xclbin' + '\n')
    make_file.append('' + '\n')
    make_file.append('package/sd_card.img: app.exe emconfig.json krnl_ubench.xclbin ./../../common/xrt.ini ./../../common/run_app.sh' + '\n')
    make_file.append('\t' + '$(call ndef,ROOTFS)' + '\n')
    make_file.append('\t' + 'v++ -p -t ${TARGET} --config ./zcu104.cfg ./krnl_ubench.xclbin \\' + '\n')
    make_file.append('\t' + '--package.out_dir package \\' + '\n')
    make_file.append('\t' + '--package.rootfs ${ROOTFS}/rootfs.ext4 \\' + '\n')
    make_file.append('\t' + '--package.sd_file krnl_ubench.xclbin \\' + '\n')
    make_file.append('\t' + '--package.sd_file ${ROOTFS}/Image \\' + '\n')
    make_file.append('\t' + '--package.sd_file ./../../common/xrt.ini \\' + '\n')
    make_file.append('\t' + '--package.sd_file emconfig.json \\' + '\n')
    make_file.append('\t' + '--package.sd_file app.exe \\' + '\n')
    make_file.append('\t' + '--package.sd_file ./../../common/run_app.sh' + '\n')
    make_file.append('' + '\n')
    make_file.append('emconfig.json:' + '\n')
    make_file.append('\t' + 'emconfigutil --platform xilinx_zcu104_base_202020_1 --nd 1' + '\n')
    make_file.append('' + '\n')
    make_file.append('clean:' + '\n')
    make_file.append('\t' + 'rm -rf krnl_ubench* app.exe *json *csv *log *summary _x package *.json .run .Xil .ipcache *.jou *.xclbin' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Unless specified, use the current directory name as the v++ build target' + '\n')
    make_file.append('TARGET ?= hw' + '\n')

    with open(make_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(make_file)
