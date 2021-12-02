
ndef = $(if $(value $(1)),,$(error $(1) must be set prior to running))

all: package/sd_card.img

app.exe: ./src/host.cpp
	$(call ndef,SDKTARGETSYSROOT)
	$(CXX) -Wall -g -std=c++11 ./src/host.cpp -o app.exe \
		-I/usr/include/xrt \
		-lOpenCL -lpthread -lrt -lstdc++

krnl_ubench.xo: ./src/krnl_ubench.cpp
	v++ -c -t ${TARGET} --config ./src/zcu104.cfg -k krnl_ubench -I./src ./src/krnl_ubench.cpp -o krnl_ubench.xo 

krnl_ubench.xclbin: ./krnl_ubench.xo
	v++ -l -t ${TARGET} --config ./src/zcu104.cfg ./krnl_ubench.xo -o krnl_ubench.xclbin

package/sd_card.img: app.exe emconfig.json krnl_ubench.xclbin xrt.ini run_app.sh
	$(call ndef,ROOTFS)
	v++ -p -t ${TARGET} --config ./src/zcu104.cfg ./krnl_ubench.xclbin \
		--package.out_dir package \
		--package.rootfs ${ROOTFS}/rootfs.ext4 \
		--package.sd_file krnl_ubench.xclbin \
		--package.sd_file ${ROOTFS}/Image \
		--package.sd_file xrt.ini \
		--package.sd_file emconfig.json \
		--package.sd_file app.exe \
		--package.sd_file run_app.sh

emconfig.json:
	emconfigutil --platform xilinx_zcu104_base_202020_1 --nd 1

clean:
	rm -rf krnl_ubench* app.exe *json *csv *log *summary _x package *.json .run .Xil .ipcache *.jou *.xclbin

# Unless specified, use the current directory name as the v++ build target
TARGET ?= hw 
