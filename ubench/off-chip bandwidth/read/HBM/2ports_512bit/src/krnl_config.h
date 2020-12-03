#include "ap_int.h"
#include <inttypes.h>

const int DWIDTH = 512;
#define INTERFACE_WIDTH ap_uint<DWIDTH>
const int WIDTH_FACTOR = DWIDTH/32;
const int NUM_ITERATIONS = 10000;
