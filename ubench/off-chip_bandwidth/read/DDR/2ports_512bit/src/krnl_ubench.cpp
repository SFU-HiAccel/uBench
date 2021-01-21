#include "krnl_config.h"

extern "C" {
	void krnl_ubench(volatile INTERFACE_WIDTH* in0, volatile INTERFACE_WIDTH* in1, const int size) {
	#pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0   max_read_burst_length=16 
	#pragma HLS INTERFACE m_axi port=in1 offset=slave bundle=gmem1   max_read_burst_length=16 
	
	#pragma HLS INTERFACE s_axilite port=in0 bundle=control
	#pragma HLS INTERFACE s_axilite port=in1 bundle=control
	
	#pragma HLS INTERFACE s_axilite port=size bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	volatile INTERFACE_WIDTH temp_data_0;
	volatile INTERFACE_WIDTH temp_data_1;

	#pragma HLS DATAFLOW
		
	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
		#pragma HLS PIPELINE II=1
	            temp_data_0 = in0[j];
	        }
	    }

	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
		#pragma HLS PIPELINE II=1
	            temp_data_1 = in1[j];
	        }
	    }
		
	    return;   
	}
}

