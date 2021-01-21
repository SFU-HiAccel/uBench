#include "krnl_config.h"

extern "C" {
	void krnl_streamWrite(int* in0, const int size, hls::stream<pkt> &kout1, hls::stream<pkt> &kout2) {
	#pragma HLS INTERFACE m_axi port=in0 offset=slave bundle=gmem0 
	#pragma HLS INTERFACE s_axilite port=in0 bundle=control

    #pragma HLS INTERFACE axis port = kout1
    #pragma HLS INTERFACE axis port = kout2
    
	#pragma HLS INTERFACE s_axilite port=size bundle=control
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	volatile INTERFACE_WIDTH temp_data_1 = 100;
	volatile INTERFACE_WIDTH temp_data_2 = 100;

	#pragma HLS DATAFLOW
        
	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
            #pragma HLS PIPELINE II=1
                pkt v1;
                v1.data = temp_data_1;
                kout1.write(v1);
	        }
	    }
        
	    for (int i = 0; i < NUM_ITERATIONS; i++) {
	        for (int j = 0; j < size; j++) {
            #pragma HLS PIPELINE II=1       
                pkt v2;
                v2.data = temp_data_2;
                kout2.write(v2);
	        }
	    }        

	    return;   
	}
}

