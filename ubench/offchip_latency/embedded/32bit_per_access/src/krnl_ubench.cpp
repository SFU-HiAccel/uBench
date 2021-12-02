#include "krnl_config.h"

extern "C" {
	void krnl_ubench(
	        volatile INTERFACE_WIDTH* in0, 
	        int* in0_index,
		const int size,
		int* sum
	){
	#pragma HLS INTERFACE m_axi port=in0 bundle=gmem0 num_read_outstanding=1 max_read_burst_length=2
	#pragma HLS INTERFACE s_axilite port=in0 bundle=control
	#pragma HLS INTERFACE m_axi port=in0_index bundle=gmem1
	#pragma HLS INTERFACE s_axilite port=in0_index bundle=control

	#pragma HLS INTERFACE s_axilite port=size bundle=control
	
	#pragma HLS INTERFACE m_axi port=sum bundle=gmem2
	#pragma HLS INTERFACE s_axilite port=sum bundle=control	
	#pragma HLS INTERFACE s_axilite port=return bundle=control
	    
	ap_uint<DWIDTH> temp_data_0;
	int temp_sum = 0;

	int local_in0_index[262144];

	for (int i = 0; i < size; ++i){
	    local_in0_index[i] = in0_index[i];
	}

	for (int i = 0; i < NUM_ITERATION; ++i){
	    for(int j = 0; j < size; ++j){
	    	temp_data_0 = in0[local_in0_index[j]];
	    	ap_int<32> temp_int = temp_data_0.range(31,0);
		temp_sum += temp_int;
	    }
	}
	
	sum[0] = temp_sum;

	    return;
	}
}

