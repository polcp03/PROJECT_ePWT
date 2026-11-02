#include "wheel_rx.h"
#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

static const uint8_t PIN_HALL = 34;  // input only, no internal pull-up: external 10 kOhm
// Shortest accepted time between magnets. 1 ms = 97 mm of travel in 1 ms = 350 km/h,
// so it never hides a real magnet; it stops a noise burst from flooding the queue.
// On 2026-11-01 a badly fitted sensor gave ~600 000 false edges in 17 minutes.
static const int64_t MIN_GAP_US = 1000;
static const int QUEUE_LEN = 64;  // 64 magnets = 6 wheel turns; the loop drains it every ms

static QueueHandle_t queue;
static volatile WheelStats stats = {};
static volatile int64_t lastAccepted = 0;

// Falling edge = a magnet arrives in front of the sensor (3144 output pulled low).
static void IRAM_ATTR onFalling() {
  int64_t now = esp_timer_get_time();
  if (now - lastAccepted < MIN_GAP_US) {
    stats.rejected++;
    return;
  }
  lastAccepted = now;
  BaseType_t woken = pdFALSE;
  if (xQueueSendFromISR(queue, &now, &woken) == pdTRUE) {
    stats.pulses++;
  } else {
    stats.queue_drops++;
  }
  if (woken) portYIELD_FROM_ISR();
}

void wheel_rx_begin() {
  queue = xQueueCreate(QUEUE_LEN, sizeof(int64_t));
  pinMode(PIN_HALL, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL), onFalling, FALLING);
}

bool wheel_rx_pop(int64_t &t_us) {
  return xQueueReceive(queue, &t_us, 0) == pdTRUE;
}

WheelStats wheel_rx_stats() {
  WheelStats s;
  s.pulses = stats.pulses;
  s.rejected = stats.rejected;
  s.queue_drops = stats.queue_drops;
  return s;
}
