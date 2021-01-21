#include "krnl_config.h"

extern "C" {
	void krnl_ubench(volatile INTERFACE_WIDTH* out0, const int size) {
	#pragma HLS INTERFACE m_axi port=out0 offset=slave bundle=gmem0 max_write_burst_length=16
	#pragma HLS INTERFACE s_axilite port=out0 bundle=control
	
	#pragma HLS INTERFACE s_axilite port=size bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	volatile INTERFACE_WIDTH temp_data_0 = 100;
		
	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
            #pragma HLS PIPELINE II=1
	            out0[j] = temp_data_0;
	        }
	    }
		
	    return;   
	}
}

