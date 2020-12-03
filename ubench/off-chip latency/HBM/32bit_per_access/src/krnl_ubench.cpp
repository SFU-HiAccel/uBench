#include "krnl_config.h"

extern "C" {
	void krnl_ubench(volatile INTERFACE_WIDTH* in0, int* in0_index, const int size) {
	#pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0 max_read_burst_length=16 num_read_outstanding=16
	#pragma HLS INTERFACE s_axilite port=in0 bundle=control
	#pragma HLS INTERFACE m_axi port=in0_index offset=slave bundle=gmem1 
	#pragma HLS INTERFACE s_axilite port=in0_index bundle=control

	#pragma HLS INTERFACE s_axilite port=size bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	int local_in0_index[524288];// max 2MB data indexing for 32-bitwidth port
	volatile INTERFACE_WIDTH temp_data_0;

		for (int i = 0; i < size; i++) {
		#pragma HLS PIPELINE II=1
			local_in0_index[i] = in0_index[i];
		}

	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
	            temp_data_0 = in0[local_in0_index[j]];
	        }
	    }

	    return;   
	}
}

