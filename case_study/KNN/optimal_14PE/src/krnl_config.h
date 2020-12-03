#include "ap_int.h"
#include <inttypes.h>
#include <math.h>

#include "ap_axi_sdata.h"
#include "hls_stream.h"

const int DWIDTH = 64;
#define INTERFACE_WIDTH ap_uint<DWIDTH>
typedef ap_axiu<32, 0, 0, 0> pkt;

const int NUM_KERNEL=14;
#define MAX_FLT 3.402823e+38f
#define TOP 10
#define NUM_ITERATIONS 5000