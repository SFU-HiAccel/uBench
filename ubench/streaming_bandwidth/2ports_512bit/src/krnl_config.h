#include "ap_int.h"
#include <inttypes.h>

#include "ap_axi_sdata.h"
#include "hls_stream.h"

const int DWIDTH = 512;
#define INTERFACE_WIDTH ap_uint<DWIDTH>
typedef ap_axiu<DWIDTH, 0, 0, 0> pkt;
const int WIDTH_FACTOR = DWIDTH/32;
const int NUM_ITERATIONS = 10000;
