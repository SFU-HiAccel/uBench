#include "krnl_config.h"

extern "C" {
	void krnl_streamRead(int* out0, const int size, hls::stream<pkt> &kin1, hls::stream<pkt> &kin2) {
	#pragma HLS INTERFACE m_axi port=out0 offset=slave bundle=gmem0
	#pragma HLS INTERFACE s_axilite port=out0 bundle=control

    #pragma HLS INTERFACE axis port = kin1
    #pragma HLS INTERFACE axis port = kin2
    
	#pragma HLS INTERFACE s_axilite port=size bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	volatile INTERFACE_WIDTH temp_data_1 = 100;
	volatile INTERFACE_WIDTH temp_data_2 = 100;

	#pragma HLS DATAFLOW        
        
	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
            #pragma HLS PIPELINE II=1
                pkt v1 = kin1.read();
                temp_data_1 = v1.data;
	        }
	    }

	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
            #pragma HLS PIPELINE II=1
                pkt v2 = kin2.read();
                temp_data_2 = v2.data;             
	        }
	    }
        
	    return;   
	}
}

