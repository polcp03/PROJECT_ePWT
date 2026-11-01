// wheel_rx - owns the wheel speed sensor (3144 Hall on the front wheel, 10 magnets).
// An interrupt stamps the time of every magnet into a RAM queue. Nothing else:
// speed, filtering and the per-gap calibration happen on the PC, from the raw times.
//
// Wiring: 3144 VCC on 5 V, GND on GND, OUT on GPIO 34, 10 kOhm OUT -> 3V3.
#pragma once
#include <stdint.h>

// Pulse counters since boot. Written only by the interrupt.
struct WheelStats {
  uint32_t pulses;       // magnets accepted into the queue
  uint32_t rejected;     // edges closer than 1 ms to the previous one: noise, not a magnet
  uint32_t queue_drops;  // pulses lost because the RAM queue was full
};

void wheel_rx_begin();
bool wheel_rx_pop(int64_t &t_us);  // esp_timer time of one magnet; false when the queue is empty
WheelStats wheel_rx_stats();
