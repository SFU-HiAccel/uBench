#include "krnl_config.h"

extern "C" {

#define INPUT_DIM 2
#define SP_LEN 256
#define DIS_LEN 128

const int NUM_OF_TILES = 32774/NUM_KERNEL;

void load(int flag, int tile_idx, INTERFACE_WIDTH* local_SP, volatile INTERFACE_WIDTH* searchSpace)
{
#pragma HLS INLINE OFF
	if (flag){
		for (int i(0); i<SP_LEN; ++i){
		#pragma HLS PIPELINE II=1
			local_SP[i] = searchSpace[tile_idx*SP_LEN+i];
		}
	}
}

void compute(int flag, float* local_Query, INTERFACE_WIDTH* local_SP, float* local_distance)
{
#pragma HLS INLINE OFF
	if (flag){
		for (int ii = 0; ii < SP_LEN; ii+=2) {
		#pragma HLS PIPELINE II=1
			float delta_squared_sum = 0.0;	
			for (int kk = 0; kk < INPUT_DIM; ++kk){
			#pragma HLS UNROLL				
				uint32_t sp_dim_item = local_SP[ii+kk].range(31, 0);
				float sp_dim_item_value = *((float*)(&sp_dim_item));
				float delta = sp_dim_item_value - local_Query[kk];
				delta_squared_sum += delta * delta;
			}
			local_distance[ii/2] = delta_squared_sum;
		}
	}
}

void swap(float* a, float* b, int* x, int* y)
{
	float tmp_1;
	int tmp_2;

	tmp_1 = *a;
	*a = *b;
	*b = tmp_1;

	tmp_2 = *x;
	*x = *y;
	*y = tmp_2;
}

void sort(int flag, int start_id, float* local_distance, float* local_kNearstDist, int* local_kNearstId)
{
#pragma HLS INLINE OFF
	if (flag){
		for (int i = 0; i < DIS_LEN; ++i) {
		#pragma HLS PIPELINE II=1
			local_kNearstDist[0] = local_distance[i];
			local_kNearstId[0] = start_id + i;
			//compare and swap odd
			for(int ii=1; ii<TOP+1; ii+=2){
			#pragma HLS UNROLL
			#pragma HLS DEPENDENCE variable="local_kNearstDist" inter false
			#pragma HLS DEPENDENCE variable="local_kNearstId" inter false
				if(local_kNearstDist[ii] < local_kNearstDist[ii+1]){
					swap(&local_kNearstDist[ii], &local_kNearstDist[ii+1], &local_kNearstId[ii], &local_kNearstId[ii+1]);
			    }
			}
			//compare and swap even
			for(int ii=1; ii<TOP+1; ii+=2){
			#pragma HLS UNROLL
			#pragma HLS DEPENDENCE variable="local_kNearstDist" inter false
			#pragma HLS DEPENDENCE variable="local_kNearstId" inter false
				if(local_kNearstDist[ii] > local_kNearstDist[ii-1]){
					swap(&local_kNearstDist[ii], &local_kNearstDist[ii-1], &local_kNearstId[ii], &local_kNearstId[ii-1]);
				}
			}
		}
	}
	else{
		for (int i=0; i<TOP+2; ++i){
		#pragma HLS UNROLL
			local_kNearstDist[i] = MAX_FLT;
			local_kNearstId[i] = -1;
		}
	}
}

void krnl_partialKnn(
	volatile float* inputQuery,     // input query
	volatile INTERFACE_WIDTH* searchSpace,    // search space
	hls::stream<pkt> &kNearstDist,			     // output distance array
	hls::stream<pkt> &kNearstId			     // output id array
){
	#pragma HLS INTERFACE m_axi port=inputQuery offset=slave bundle=gmem1
	#pragma HLS INTERFACE m_axi port=searchSpace offset=slave bundle=gmem1
	#pragma HLS INTERFACE s_axilite port=inputQuery bundle=control
	#pragma HLS INTERFACE s_axilite port=searchSpace bundle=control
	#pragma HLS INTERFACE axis port=kNearstDist
	#pragma HLS INTERFACE axis port=kNearstId
	#pragma HLS INTERFACE s_axilite port=return bundle=control

	float local_Query[INPUT_DIM];
	#pragma HLS ARRAY_PARTITION variable=local_Query complete dim=1

	INTERFACE_WIDTH local_SP_0[SP_LEN];
	#pragma HLS RESOURCE variable=local_SP_0 core=XPM_MEMORY uram
	INTERFACE_WIDTH local_SP_1[SP_LEN];
	#pragma HLS RESOURCE variable=local_SP_1 core=XPM_MEMORY uram

	float local_distance_0[DIS_LEN];
    #pragma HLS RESOURCE variable=local_distance_0 core=XPM_MEMORY uram
	float local_distance_1[DIS_LEN];
    #pragma HLS RESOURCE variable=local_distance_1 core=XPM_MEMORY uram

	float local_kNearstDist[TOP+2];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstDist complete
	int local_kNearstId[TOP+2];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstId complete	    

	for (int i = 0; i < INPUT_DIM; ++i){
		local_Query[i] = inputQuery[i];
	}

	for (int it_idx = 0; it_idx < NUM_ITERATIONS; ++it_idx){
		for(int i = 0; i < NUM_OF_TILES+2; ++i){
		    int load_img_flag = i >= 0 && i < NUM_OF_TILES;
		    int compute_flag = i >= 1 && i < NUM_OF_TILES + 1;
		    int sort_flag = i >= 2 && i < NUM_OF_TILES + 2;

		    if (i % 2 == 0) {
		    	load(load_img_flag, i, local_SP_0, searchSpace);
				compute(compute_flag, local_Query, local_SP_1, local_distance_1);
				sort(sort_flag, (i-2)*DIS_LEN, local_distance_0, local_kNearstDist, local_kNearstId);
		    }
		    else {
		    	load(load_img_flag, i, local_SP_1, searchSpace);
				compute(compute_flag, local_Query, local_SP_0, local_distance_0);
				sort(sort_flag, (i-2)*DIS_LEN, local_distance_1, local_kNearstDist, local_kNearstId);
		    }
		}
	}

	for (int i = 1; i < TOP+1; ++i){
	#pragma HLS PIPELINE II=1
		pkt v;
		v.data = local_kNearstDist[i];
		kNearstDist.write(v);
		pkt v_id;
		v_id.data = local_kNearstId[i];
		kNearstId.write(v_id);
	}

	return;
}

}

