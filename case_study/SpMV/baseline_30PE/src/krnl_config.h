#include "ap_int.h" 
#include "ap_axi_sdata.h" 
#include "hls_stream.h" 
#include <inttypes.h> 
#include <stdlib.h> 

const int DWIDTH_256 = 32; 
#define INTERFACE_WIDTH_256 ap_uint<DWIDTH_256>
const int W_FACTOR_256 = DWIDTH_256/32;
const int DWIDTH_512 = 32; 
#define INTERFACE_WIDTH_512 ap_uint<DWIDTH_512>
const int W_FACTOR_512 = DWIDTH_512/32;

#define TYPE float
const int NUM_ITERATIONS = 5000;

#define NUM_KERNEL (30) 

#define N (8400)
#define L (1024)

#define N_OUT (N/NUM_KERNEL)
#define ROWS_PER_TILE (8)
#define NUM_TILES (N_OUT/ROWS_PER_TILE)
#define UNROLL_FACTOR (1)