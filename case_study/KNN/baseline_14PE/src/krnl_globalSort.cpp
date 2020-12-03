#include "krnl_config.h"

extern "C" {

void seq_global_merge(float local_kNearstDist_partial[NUM_KERNEL][TOP],
						int local_kNearstId_partial[NUM_KERNEL][TOP], 
						float* dist, int* id)
{
#pragma HLS INLINE OFF
	int idx[NUM_KERNEL];
	#pragma HLS ARRAY_PARTITION variable=idx complete dim=0

	for (int i = 0; i < NUM_KERNEL; ++i){
	#pragma HLS UNROLL
		idx[i] = TOP-1; 
	}

	for (int i = TOP-1; i >= 0; --i){
		float min_value = MAX_FLT;
		int min_idx = -1;
		for (int j = 0; j < NUM_KERNEL; ++j){
		#pragma HLS PIPELINE II=1
			if (local_kNearstDist_partial[j][idx[j]] < min_value){
				min_value = local_kNearstDist_partial[j][idx[j]];
				min_idx = j;
			}
		}
		dist[i] = min_value;
		id[i] = local_kNearstId_partial[min_idx][idx[min_idx]];

		idx[min_idx] = idx[min_idx] - 1;
	}
}

void krnl_globalSort(hls::stream<pkt> &in1, // Internal Stream
		     hls::stream<pkt> &in2, // Internal Stream
		     hls::stream<pkt> &in3, // Internal Stream
		     hls::stream<pkt> &in4, // Internal Stream
			 hls::stream<pkt> &in5, // Internal Stream
		     hls::stream<pkt> &in6, // Internal Stream
		     hls::stream<pkt> &in7, // Internal Stream
		     hls::stream<pkt> &in8, // Internal Stream
		     hls::stream<pkt> &in9, // Internal Stream
		     hls::stream<pkt> &in10, // Internal Stream
		     hls::stream<pkt> &in11, // Internal Stream
			 hls::stream<pkt> &in12, // Internal Stream
		     hls::stream<pkt> &in13, // Internal Stream
		     hls::stream<pkt> &in14, // Internal Stream

			 hls::stream<pkt> &in1_id, // Internal Stream
		     hls::stream<pkt> &in2_id, // Internal Stream
		     hls::stream<pkt> &in3_id, // Internal Stream
		     hls::stream<pkt> &in4_id, // Internal Stream
			 hls::stream<pkt> &in5_id, // Internal Stream
		     hls::stream<pkt> &in6_id, // Internal Stream
		     hls::stream<pkt> &in7_id, // Internal Stream
		     hls::stream<pkt> &in8_id, // Internal Stream
		     hls::stream<pkt> &in9_id, // Internal Stream
		     hls::stream<pkt> &in10_id, // Internal Stream
		     hls::stream<pkt> &in11_id, // Internal Stream
			 hls::stream<pkt> &in12_id, // Internal Stream
		     hls::stream<pkt> &in13_id, // Internal Stream
		     hls::stream<pkt> &in14_id, // Internal Stream
		     float *kNearstDist, // Output Result
		     int *kNearstId // Output Result
) {

#pragma HLS INTERFACE axis port = in1
#pragma HLS INTERFACE axis port = in2
#pragma HLS INTERFACE axis port = in3
#pragma HLS INTERFACE axis port = in4
#pragma HLS INTERFACE axis port = in5
#pragma HLS INTERFACE axis port = in6
#pragma HLS INTERFACE axis port = in7
#pragma HLS INTERFACE axis port = in8
#pragma HLS INTERFACE axis port = in9
#pragma HLS INTERFACE axis port = in10
#pragma HLS INTERFACE axis port = in11
#pragma HLS INTERFACE axis port = in12
#pragma HLS INTERFACE axis port = in13
#pragma HLS INTERFACE axis port = in14
#pragma HLS INTERFACE axis port = in1_id
#pragma HLS INTERFACE axis port = in2_id
#pragma HLS INTERFACE axis port = in3_id
#pragma HLS INTERFACE axis port = in4_id
#pragma HLS INTERFACE axis port = in5_id
#pragma HLS INTERFACE axis port = in6_id
#pragma HLS INTERFACE axis port = in7_id
#pragma HLS INTERFACE axis port = in8_id
#pragma HLS INTERFACE axis port = in9_id
#pragma HLS INTERFACE axis port = in10_id
#pragma HLS INTERFACE axis port = in11_id
#pragma HLS INTERFACE axis port = in12_id
#pragma HLS INTERFACE axis port = in13_id
#pragma HLS INTERFACE axis port = in14_id
#pragma HLS INTERFACE m_axi port=kNearstDist offset=slave bundle=gmem0
#pragma HLS INTERFACE m_axi port=kNearstId offset=slave bundle=gmem0
#pragma HLS INTERFACE s_axilite port=kNearstDist bundle=control
#pragma HLS INTERFACE s_axilite port=kNearstId bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

	float local_kNearstDist_partial[NUM_KERNEL][TOP];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstDist_partial complete dim=0
	int local_kNearstId_partial[NUM_KERNEL][TOP];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstId_partial complete dim=0

	float local_kNearstDist[TOP];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstDist complete
	int local_kNearstId[TOP];
	#pragma HLS ARRAY_PARTITION variable=local_kNearstId complete

    for (unsigned int i=0; i<TOP; ++i){
	#pragma HLS PIPELINE II=1
    	pkt v1 = in1.read();
		uint32_t v1_data = v1.data;
		local_kNearstDist_partial[0][i] = *((float*)(&v1_data));
    	pkt v2 = in2.read();
		uint32_t v2_data = v2.data;
		local_kNearstDist_partial[1][i] = *((float*)(&v2_data));
    	pkt v3 = in3.read();
		uint32_t v3_data = v3.data;
		local_kNearstDist_partial[2][i] = *((float*)(&v3_data));
    	pkt v4 = in4.read();
		uint32_t v4_data = v4.data;
		local_kNearstDist_partial[3][i] = *((float*)(&v4_data));
    	pkt v5 = in5.read();
		uint32_t v5_data = v5.data;
		local_kNearstDist_partial[4][i] = *((float*)(&v5_data));
    	pkt v6 = in6.read();
		uint32_t v6_data = v6.data;
		local_kNearstDist_partial[5][i] = *((float*)(&v6_data));
    	pkt v7 = in7.read();
		uint32_t v7_data = v7.data;
		local_kNearstDist_partial[6][i] = *((float*)(&v7_data));
    	pkt v8 = in8.read();
		uint32_t v8_data = v8.data;
		local_kNearstDist_partial[7][i] = *((float*)(&v8_data));
		pkt v9 = in9.read();
		uint32_t v9_data = v9.data;
		local_kNearstDist_partial[8][i] = *((float*)(&v9_data));
    	pkt v10 = in10.read();
		uint32_t v10_data = v10.data;
		local_kNearstDist_partial[9][i] = *((float*)(&v10_data));
    	pkt v11 = in11.read();
		uint32_t v11_data = v11.data;
		local_kNearstDist_partial[10][i] = *((float*)(&v11_data));
    	pkt v12 = in12.read();
		uint32_t v12_data = v12.data;
		local_kNearstDist_partial[11][i] = *((float*)(&v12_data));
    	pkt v13 = in13.read();
		uint32_t v13_data = v13.data;
		local_kNearstDist_partial[12][i] = *((float*)(&v13_data));
    	pkt v14 = in14.read();
		uint32_t v14_data = v14.data;
		local_kNearstDist_partial[13][i] = *((float*)(&v14_data));

    	pkt v1_id = in1_id.read();
		uint32_t v1_data_id = v1_id.data;
		local_kNearstId_partial[0][i] = *((int*)(&v1_data_id));
    	pkt v2_id = in2_id.read();
		uint32_t v2_data_id = v2_id.data;
		local_kNearstId_partial[1][i] = *((int*)(&v2_data_id));
    	pkt v3_id = in3_id.read();
		uint32_t v3_data_id = v3_id.data;
		local_kNearstId_partial[2][i] = *((int*)(&v3_data_id));
    	pkt v4_id = in4_id.read();
		uint32_t v4_data_id = v4_id.data;
		local_kNearstId_partial[3][i] = *((int*)(&v4_data_id));
    	pkt v5_id = in5_id.read();
		uint32_t v5_data_id = v5_id.data;
		local_kNearstId_partial[4][i] = *((int*)(&v5_data_id));
    	pkt v6_id = in6_id.read();
		uint32_t v6_data_id = v6_id.data;
		local_kNearstId_partial[5][i] = *((int*)(&v6_data_id));
    	pkt v7_id = in7_id.read();
		uint32_t v7_data_id = v7_id.data;
		local_kNearstId_partial[6][i] = *((int*)(&v7_data_id));
    	pkt v8_id = in8_id.read();
		uint32_t v8_data_id = v8_id.data;
		local_kNearstId_partial[7][i] = *((int*)(&v8_data_id));
		pkt v9_id = in9_id.read();
		uint32_t v9_data_id = v9_id.data;
		local_kNearstId_partial[8][i] = *((int*)(&v9_data_id));
    	pkt v10_id = in10_id.read();
		uint32_t v10_data_id = v10_id.data;
		local_kNearstId_partial[9][i] = *((int*)(&v10_data_id));
    	pkt v11_id = in11_id.read();
		uint32_t v11_data_id = v11_id.data;
		local_kNearstId_partial[10][i] = *((int*)(&v11_data_id));
    	pkt v12_id = in12_id.read();
		uint32_t v12_data_id = v12_id.data;
		local_kNearstId_partial[11][i] = *((int*)(&v12_data_id));
    	pkt v13_id = in13_id.read();
		uint32_t v13_data_id = v13_id.data;
		local_kNearstId_partial[12][i] = *((int*)(&v13_data_id));
    	pkt v14_id = in14_id.read();
		uint32_t v14_data_id = v14_id.data;
		local_kNearstId_partial[13][i] = *((int*)(&v14_data_id));
    }

	seq_global_merge(local_kNearstDist_partial, local_kNearstId_partial, local_kNearstDist, local_kNearstId); 

	for (int i = 0; i < TOP; ++i){
	#pragma HLS PIPELINE II=1
		kNearstDist[i] = local_kNearstDist[i];
		kNearstId[i] = local_kNearstId[i];
	}

	return;
}

}
