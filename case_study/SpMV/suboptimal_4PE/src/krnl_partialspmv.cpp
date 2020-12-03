#include "krnl_config.h"

extern "C" {

void ellpack (TYPE* nzval, int* cols, TYPE* vec, TYPE* out)
{
#pragma HLS INLINE off
    for (int i=0; i<ROWS_PER_TILE/UNROLL_FACTOR; i++) {
    #pragma HLS PIPELINE
		out[i] = 0.0;
    }
    ellpack_2 : for (int j=0; j<L; j++) {
    #pragma HLS PIPELINE
    	ellpack_1 : for (int i=0; i<ROWS_PER_TILE/UNROLL_FACTOR; i++) {
		#pragma HLS UNROLL
            out[i] = out[i] + nzval[j + i*L] * vec[cols[j + i*L]];
        }
    }
}

void buffer_compute (TYPE local_nzval[][L*ROWS_PER_TILE/UNROLL_FACTOR], int local_cols[][L*ROWS_PER_TILE/UNROLL_FACTOR], 
		    TYPE local_vec[][N], TYPE local_out[][ROWS_PER_TILE/UNROLL_FACTOR], int flag, TYPE* out) {
#pragma HLS INLINE off
	if (flag) {
		for (int j=0; j<UNROLL_FACTOR; j++) {
    	#pragma HLS UNROLL
			ellpack(local_nzval[j], local_cols[j], local_vec[j], local_out[j]);
    	}
    	for (int i=0; i<UNROLL_FACTOR; i++) {
			for (int j=0; j<ROWS_PER_TILE/UNROLL_FACTOR; j++) {
			#pragma HLS PIPELINE II=1
				out[i*ROWS_PER_TILE/UNROLL_FACTOR+j] = local_out[i][j];
			}
    	}
  	}
}

void load_nzval (volatile INTERFACE_WIDTH_256* nzval, TYPE local_nzval[][L*ROWS_PER_TILE/UNROLL_FACTOR], int flag) {
#pragma HLS INLINE off
	if (flag) {
		const int tile_length = L*ROWS_PER_TILE/W_FACTOR_256;
		for (int i=0; i<tile_length; ++i){
		#pragma HLS PIPELINE II=1
			int row = i / (tile_length/UNROLL_FACTOR);
			int col = i % (tile_length/UNROLL_FACTOR);
			INTERFACE_WIDTH_256 temp_data = nzval[i];
			for (int k=0; k<W_FACTOR_256; ++k){
			#pragma HLS UNROLL
				unsigned int range_idx = k * 32;
				uint32_t tmp_int = temp_data.range(range_idx+31, range_idx);
				float tmp_float = *((float*)(&tmp_int));
				local_nzval[row][col*W_FACTOR_256+k] = tmp_float;
			}
		}
  	}
}

void load_cols (volatile INTERFACE_WIDTH_256* cols, int local_cols[][L*ROWS_PER_TILE/UNROLL_FACTOR], int flag) {
#pragma HLS INLINE off
  	if (flag) {
		const int tile_length = L*ROWS_PER_TILE/W_FACTOR_256;
		for (int i=0; i<tile_length; ++i){
		#pragma HLS PIPELINE II=1
			int row = i / (tile_length/UNROLL_FACTOR);
			int col = i % (tile_length/UNROLL_FACTOR);
			INTERFACE_WIDTH_256 temp_data = cols[i];
			for (int k=0; k<W_FACTOR_256; ++k){
			#pragma HLS UNROLL
				unsigned int range_idx = k * 32;
				uint32_t tmp = temp_data.range(range_idx+31, range_idx);
				int tmp_int = *((int*)(&tmp));
				local_cols[row][col*W_FACTOR_256+k] = tmp_int;
			}
		}
  	}
}

void buffer_load(volatile INTERFACE_WIDTH_256* nzval, TYPE local_nzval[][L*ROWS_PER_TILE/UNROLL_FACTOR], 
				 volatile INTERFACE_WIDTH_256* cols, int local_cols[][L*ROWS_PER_TILE/UNROLL_FACTOR], int flag){
#pragma HLS INLINE off
#pragma HLS DATAFLOW
	load_nzval(nzval, local_nzval, flag);
	load_cols(cols, local_cols, flag);
}

void krnl_partialspmv(volatile INTERFACE_WIDTH_256* nzval, 
					  volatile INTERFACE_WIDTH_256* cols, 
					  INTERFACE_WIDTH_512* vec, INTERFACE_WIDTH_512* out) {
#pragma HLS INTERFACE m_axi port=nzval offset=slave bundle=gmem0 max_read_burst_length=16
#pragma HLS INTERFACE m_axi port=cols  offset=slave bundle=gmem1 max_read_burst_length=16
#pragma HLS INTERFACE m_axi port=vec   offset=slave bundle=gmem2 max_read_burst_length=256 max_write_burst_length=256
#pragma HLS INTERFACE m_axi port=out   offset=slave bundle=gmem2 max_read_burst_length=256 max_write_burst_length=256
#pragma HLS INTERFACE s_axilite port=nzval bundle=control
#pragma HLS INTERFACE s_axilite port=cols bundle=control
#pragma HLS INTERFACE s_axilite port=vec bundle=control
#pragma HLS INTERFACE s_axilite port=out bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

	TYPE local_nzval_x[UNROLL_FACTOR][L*ROWS_PER_TILE/UNROLL_FACTOR];
#pragma HLS ARRAY_PARTITION variable=local_nzval_x dim=1 complete
#pragma HLS ARRAY_PARTITION variable=local_nzval_x dim=2 cyclic factor=W_FACTOR_256
#pragma HLS RESOURCE variable=local_nzval_x core=XPM_MEMORY uram
	TYPE local_nzval_y[UNROLL_FACTOR][L*ROWS_PER_TILE/UNROLL_FACTOR];
#pragma HLS ARRAY_PARTITION variable=local_nzval_y dim=1 complete
#pragma HLS ARRAY_PARTITION variable=local_nzval_y dim=2 cyclic factor=W_FACTOR_256
#pragma HLS RESOURCE variable=local_nzval_y core=XPM_MEMORY uram

	int local_cols_x[UNROLL_FACTOR][L*ROWS_PER_TILE/UNROLL_FACTOR];
#pragma HLS ARRAY_PARTITION variable=local_cols_x dim=1 complete
#pragma HLS ARRAY_PARTITION variable=local_cols_x dim=2 cyclic factor=W_FACTOR_256
	int local_cols_y[UNROLL_FACTOR][L*ROWS_PER_TILE/UNROLL_FACTOR];
#pragma HLS ARRAY_PARTITION variable=local_cols_y dim=1 complete
#pragma HLS ARRAY_PARTITION variable=local_cols_y dim=2 cyclic factor=W_FACTOR_256

	//read 'vec' from DRAM
	TYPE temp_vec[N];
#pragma HLS ARRAY_PARTITION variable=temp_vec cyclic factor=W_FACTOR_512
	for (int i=0; i<N/W_FACTOR_512; ++i){
	#pragma HLS PIPELINE II=1
		INTERFACE_WIDTH_512 temp_data = vec[i];
		for (int j=0; j<W_FACTOR_512; ++j){
		#pragma HLS UNROLL
			unsigned int range_idx = j * 32;
			uint32_t tmp_int = temp_data.range(range_idx + 31, range_idx);
			float tmp_float = *((float*)(&tmp_int));
			temp_vec[i*W_FACTOR_512+j] = tmp_float;
		}
	}
	TYPE local_vec[UNROLL_FACTOR][N];
#pragma HLS ARRAY_PARTITION variable=local_vec dim=1 complete
	for(int i=0; i<N; i++) {
    #pragma HLS PIPELINE II=1
	    for(int j=0; j<UNROLL_FACTOR; j++) {
	    #pragma HLS UNROLL
	        local_vec[j][i] = temp_vec[i];
	    }
	} 

	TYPE local_out[UNROLL_FACTOR][ROWS_PER_TILE/UNROLL_FACTOR];
#pragma HLS ARRAY_PARTITION variable=local_out dim=0 complete
	TYPE all_out[N_OUT];
#pragma HLS ARRAY_PARTITION variable=all_out cyclic factor=W_FACTOR_512

	int load_flag, compute_flag;
	for (int it=0; it<NUM_ITERATIONS; ++it){
		for (int i=0; i<NUM_TILES+1; i++) {
			load_flag = i >= 0 && i < NUM_TILES;
			compute_flag = i > 0 && i <= NUM_TILES;
			if (i % 2 == 0) {
				buffer_load(nzval + i*ROWS_PER_TILE*L/W_FACTOR_256, local_nzval_x, cols + i*ROWS_PER_TILE*L/W_FACTOR_256, local_cols_x, load_flag);
				buffer_compute(local_nzval_y, local_cols_y, local_vec, local_out, compute_flag, all_out + (i-1)*ROWS_PER_TILE);
			}
			else {
				buffer_load(nzval + i*ROWS_PER_TILE*L/W_FACTOR_256, local_nzval_y, cols + i*ROWS_PER_TILE*L/W_FACTOR_256, local_cols_y, load_flag);
				buffer_compute(local_nzval_x, local_cols_x, local_vec, local_out, compute_flag, all_out + (i-1)*ROWS_PER_TILE);
			}
		}
	}

	//write 'out' to DRAM
	for (int i=0; i<N_OUT/W_FACTOR_512; ++i){
	#pragma HLS PIPELINE II=1
		for (int j=0; j<W_FACTOR_512; ++j){
		#pragma HLS UNROLL
			unsigned int range_idx = j * 32;
			float tmp_flt = all_out[i*W_FACTOR_512+j];
			out[i].range(range_idx+31, range_idx) = *((uint32_t *)(&tmp_flt));
		}
	}

	return;
}

}