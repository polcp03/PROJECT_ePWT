// can_rx - owns the MCP2515. Reads every frame on the bus into a RAM queue.
// Runs as its own task on core 0, so a slow SD write on core 1 cannot make it miss frames.
// Never transmits: the MCP2515 only ACKs.
#pragma once
#include "can_frame.h"

bool can_rx_begin();                 // false if the MCP2515 does not answer over SPI
bool can_rx_pop(CanFrame &frame);    // non-blocking; false when the queue is empty
CanStats can_rx_stats();
