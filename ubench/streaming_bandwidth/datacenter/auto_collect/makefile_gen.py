#!/usr/bin/python
import os
import re
import math

def generateMakefile(kernel_freq):
    make_file_name = 'Makefile'
    make_file = []

    make_file.append('.PHONY: help' + '\n')
    make_file.append('' + '\n')
    make_file.append('help::' + '\n')
    make_file.append('	$(ECHO) "Makefile Usage:"' + '\n')
    make_file.append('	$(ECHO) "  make all TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> SYSROOT=<sysroot_path>"' + '\n')
    make_file.append('	$(ECHO) "      Command to generate the design for specified Target and Shell."' + '\n')
    make_file.append('	$(ECHO) "      By default, HOST_ARCH=x86. HOST_ARCH and SYSROOT is required for SoC shells"' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('	$(ECHO) "  make clean "' + '\n')
    make_file.append('	$(ECHO) "      Command to remove the generated non-hardware files."' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('	$(ECHO) "  make cleanall"' + '\n')
    make_file.append('	$(ECHO) "      Command to remove all the generated files."' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('	$(ECHO) "  make sd_card TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> SYSROOT=<sysroot_path>"' + '\n')
    make_file.append('	$(ECHO) "      Command to prepare sd_card files."' + '\n')
    make_file.append('	$(ECHO) "      By default, HOST_ARCH=x86. HOST_ARCH and SYSROOT is required for SoC shells"' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('	$(ECHO) "  make check TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> SYSROOT=<sysroot_path>"' + '\n')
    make_file.append('	$(ECHO) "      Command to run application in emulation."' + '\n')
    make_file.append('	$(ECHO) "      By default, HOST_ARCH=x86. HOST_ARCH and SYSROOT is required for SoC shells"' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('	$(ECHO) "  make build TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> SYSROOT=<sysroot_path>"' + '\n')
    make_file.append('	$(ECHO) "      Command to build xclbin application."' + '\n')
    make_file.append('	$(ECHO) "      By default, HOST_ARCH=x86. HOST_ARCH and SYSROOT is required for SoC shells"' + '\n')
    make_file.append('	$(ECHO) ""' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Points to top directory of Git repository' + '\n')
    make_file.append('COMMON_REPO = ../../../../../../' + '\n')
    make_file.append('PWD = $(shell readlink -f .)' + '\n')
    make_file.append('ABS_COMMON_REPO = $(shell readlink -f $(COMMON_REPO))' + '\n')
    make_file.append('' + '\n')
    make_file.append('TARGET := hw' + '\n')
    make_file.append('HOST_ARCH := x86' + '\n')
    make_file.append('SYSROOT := ' + '\n')
    make_file.append('' + '\n')
    make_file.append('include $(ABS_COMMON_REPO)/common/utils.mk' + '\n')
    make_file.append('' + '\n')
    make_file.append('XSA := $(call device2xsa, $(DEVICE))' + '\n')
    make_file.append('TEMP_DIR := ./_x.$(TARGET).$(XSA)' + '\n')
    make_file.append('BUILD_DIR := ./build_dir.$(TARGET).$(XSA)' + '\n')
    make_file.append('' + '\n')
    make_file.append('VPP := v++' + '\n')
    make_file.append('SDCARD := sd_card' + '\n')
    make_file.append('' + '\n')
    make_file.append('#Include Libraries' + '\n')
    make_file.append('include $(ABS_COMMON_REPO)/common/includes/opencl/opencl.mk' + '\n')
    make_file.append('include $(ABS_COMMON_REPO)/common/includes/xcl2/xcl2.mk' + '\n')
    make_file.append('CXXFLAGS += $(xcl2_CXXFLAGS)' + '\n')
    make_file.append('LDFLAGS += $(xcl2_LDFLAGS)' + '\n')
    make_file.append('HOST_SRCS += $(xcl2_SRCS)' + '\n')
    make_file.append('CXXFLAGS += -pthread' + '\n')
    make_file.append('CXXFLAGS += $(opencl_CXXFLAGS) -Wall -O0 -g -std=c++11' + '\n')
    make_file.append('LDFLAGS += $(opencl_LDFLAGS)' + '\n')
    make_file.append('' + '\n')
    make_file.append('HOST_SRCS += src/host.cpp src/krnl_config.h' + '\n')
    make_file.append('# Host compiler global settings' + '\n')
    make_file.append('CXXFLAGS += -fmessage-length=0' + '\n')
    make_file.append('LDFLAGS += -lrt -lstdc++ ' + '\n')
    make_file.append('' + '\n')
    make_file.append('ifneq ($(HOST_ARCH), x86)' + '\n')
    make_file.append('	LDFLAGS += --sysroot=$(SYSROOT)' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Kernel compiler global settings' + '\n')
    make_file.append('CLFLAGS += -t $(TARGET) --platform $(DEVICE) --save-temps --kernel_frequency ' + str(kernel_freq) + '\n')
    make_file.append('ifneq ($(TARGET), hw)' + '\n')
    make_file.append('	CLFLAGS += -g' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Kernel linker flags' + '\n')
    make_file.append('LDCLFLAGS += --config ./ubench.ini' + '\n')
    make_file.append('' + '\n')
    make_file.append('EXECUTABLE = ubench' + '\n')
    make_file.append('CMD_ARGS = $(BUILD_DIR)/ubench.xclbin' + '\n')
    make_file.append('EMCONFIG_DIR = $(TEMP_DIR)' + '\n')
    make_file.append('EMU_DIR = $(SDCARD)/data/emulation' + '\n')
    make_file.append('' + '\n')
    make_file.append('BINARY_CONTAINERS += $(BUILD_DIR)/ubench.xclbin' + '\n')
    make_file.append('BINARY_CONTAINER_ubench_OBJS += $(TEMP_DIR)/krnl_streamWrite.xo' + '\n')
    make_file.append('BINARY_CONTAINER_ubench_OBJS += $(TEMP_DIR)/krnl_streamRead.xo' + '\n')
    make_file.append('' + '\n')
    make_file.append('CP = cp -rf' + '\n')
    make_file.append('' + '\n')
    make_file.append('.PHONY: all clean cleanall docs emconfig' + '\n')
    make_file.append('all: check-devices $(EXECUTABLE) $(BINARY_CONTAINERS) emconfig sd_card' + '\n')
    make_file.append('' + '\n')
    make_file.append('.PHONY: exe' + '\n')
    make_file.append('exe: $(EXECUTABLE)' + '\n')
    make_file.append('' + '\n')
    make_file.append('.PHONY: build' + '\n')
    make_file.append('build: $(BINARY_CONTAINERS)' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Building kernel' + '\n')
    make_file.append('$(TEMP_DIR)/krnl_streamWrite.xo: src/krnl_streamWrite.cpp' + '\n')
    make_file.append('	mkdir -p $(TEMP_DIR)' + '\n')
    make_file.append('	$(VPP) $(CLFLAGS) --temp_dir $(TEMP_DIR) -c -k krnl_streamWrite -I\'$(<D)\' -o\'$@\' \'$<\'' + '\n')
    make_file.append('$(TEMP_DIR)/krnl_streamRead.xo: src/krnl_streamRead.cpp' + '\n')
    make_file.append('	mkdir -p $(TEMP_DIR)' + '\n')
    make_file.append('	$(VPP) $(CLFLAGS) --temp_dir $(TEMP_DIR) -c -k krnl_streamRead -I\'$(<D)\' -o\'$@\' \'$<\'' + '\n')
    make_file.append('$(BUILD_DIR)/ubench.xclbin: $(BINARY_CONTAINER_ubench_OBJS)' + '\n')
    make_file.append('	mkdir -p $(BUILD_DIR)' + '\n')
    make_file.append('	$(VPP) $(CLFLAGS) --temp_dir $(BUILD_DIR) -l $(LDCLFLAGS) -o\'$@\' $(+)' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Building Host' + '\n')
    make_file.append('$(EXECUTABLE): check-xrt $(HOST_SRCS) $(HOST_HDRS)' + '\n')
    make_file.append('	$(CXX) $(CXXFLAGS) $(HOST_SRCS) $(HOST_HDRS) -o \'$@\' $(LDFLAGS)' + '\n')
    make_file.append('' + '\n')
    make_file.append('emconfig:$(EMCONFIG_DIR)/emconfig.json' + '\n')
    make_file.append('$(EMCONFIG_DIR)/emconfig.json:' + '\n')
    make_file.append('	emconfigutil --platform $(DEVICE) --od $(EMCONFIG_DIR)' + '\n')
    make_file.append('' + '\n')
    make_file.append('check: all' + '\n')
    make_file.append('ifeq ($(findstring samsung, $(DEVICE)), samsung)' + '\n')
    make_file.append('$(error This example is not supported for $(DEVICE))' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('ifeq ($(findstring zc, $(DEVICE)), zc)' + '\n')
    make_file.append('$(error This example is not supported for $(DEVICE))' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('' + '\n')
    make_file.append('ifeq ($(TARGET),$(filter $(TARGET),sw_emu hw_emu))' + '\n')
    make_file.append('ifeq ($(HOST_ARCH), x86)' + '\n')
    make_file.append('	$(CP) $(EMCONFIG_DIR)/emconfig.json .' + '\n')
    make_file.append('	XCL_EMULATION_MODE=$(TARGET) ./$(EXECUTABLE) $(BUILD_DIR)/ubench.xclbin' + '\n')
    make_file.append('else' + '\n')
    make_file.append('	mkdir -p $(EMU_DIR)' + '\n')
    make_file.append('	$(CP) $(XILINX_VITIS)/data/emulation/unified $(EMU_DIR)' + '\n')
    make_file.append('	mkfatimg $(SDCARD) $(SDCARD).img 500000' + '\n')
    make_file.append('	launch_emulator -no-reboot -runtime ocl -t $(TARGET) -sd-card-image $(SDCARD).img -device-family $(DEV_FAM)' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('else' + '\n')
    make_file.append('ifeq ($(HOST_ARCH), x86)' + '\n')
    make_file.append('	./$(EXECUTABLE) $(BUILD_DIR)/ubench.xclbin' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('ifeq ($(HOST_ARCH), x86)' + '\n')
    make_file.append('	perf_analyze profile -i profile_summary.csv -f html' + '\n')
    make_file.append('endif' + '\n')
    make_file.append('' + '\n')
    make_file.append('# Cleaning stuff' + '\n')
    make_file.append('clean:' + '\n')
    make_file.append('	-$(RMDIR) $(EXECUTABLE) $(XCLBIN)/{*sw_emu*,*hw_emu*} ' + '\n')
    make_file.append('	-$(RMDIR) profile_* TempConfig system_estimate.xtxt *.rpt *.csv ' + '\n')
    make_file.append('	-$(RMDIR) src/*.ll *v++* .Xil emconfig.json dltmp* xmltmp* *.log *.jou *.wcfg *.wdb' + '\n')
    make_file.append('' + '\n')
    make_file.append('cleanall: clean' + '\n')
    make_file.append('	-$(RMDIR) build_dir* sd_card*' + '\n')
    make_file.append('	-$(RMDIR) _x.* *xclbin.run_summary qemu-memory-_* emulation/ _vimage/ pl* start_simulation.sh *.xclbin' + '\n')

    with open(make_file_name, 'w') as f:
        # go to start of file
        f.seek(0)
        # actually write the lines
        f.writelines(make_file)
