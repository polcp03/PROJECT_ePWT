// can_frame.h - the one data type the modules share.
// can_rx produces frames, sd_log consumes them; neither knows about the other.
#pragma once
#include <stdint.h>

struct CanFrame {
  int64_t t_us;     // esp_timer time when the frame was read from the MCP2515
  uint32_t id;      // 11 or 29 bit identifier, flags stripped
  uint8_t ext;      // 1 = extended (29 bit) id
  uint8_t dlc;      // as received, 0..15; above 8 only 8 bytes exist (or the read was corrupted)
  uint8_t data[8];
};

// Bus health, updated by can_rx. Each field is written by one task only.
struct CanStats {
  uint32_t frames;         // frames read from the MCP2515 since boot
  uint32_t queue_drops;    // frames lost because the RAM queue was full (SD too slow)
  uint32_t hw_overflows;   // MCP2515 overflow events (frames lost before we could read them)
  uint32_t spi_errors;     // SPI reads that disagreed with each other (noise on the MCP2515 link)
  uint8_t rx_err;          // MCP2515 receive error counter
  uint8_t tx_err;          // MCP2515 transmit error counter
};
