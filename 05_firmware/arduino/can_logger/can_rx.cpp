#include "can_rx.h"
#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>

// HSPI, separate from the SD card on VSPI. MISO goes through the 1k / 2k divider.
static const int8_t PIN_SCK = 14;
static const int8_t PIN_MISO = 27;
static const int8_t PIN_MOSI = 13;
static const int8_t PIN_CS = 26;

// 1024 frames = about 5 s of VESC traffic at 200 frames/s before the SD must catch up.
static const int QUEUE_LEN = 1024;
static const int64_t STATS_PERIOD_US = 10000;

static SPIClass canSpi(HSPI);
static MCP_CAN can(&canSpi, PIN_CS);
static QueueHandle_t queue;
static volatile CanStats stats;

// The library reads the error flags but cannot clear them, so the overflow
// bits would stay set forever. SPI BIT MODIFY (0x05) on EFLG (0x2D), bits 7:6.
static void clearOverflowFlags() {
  canSpi.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0));
  digitalWrite(PIN_CS, LOW);
  canSpi.transfer(0x05);
  canSpi.transfer(0x2D);
  canSpi.transfer(0xC0);
  canSpi.transfer(0x00);
  digitalWrite(PIN_CS, HIGH);
  canSpi.endTransaction();
}

// Busy-polls on purpose: the VESC sends its status frames back to back,
// so both MCP2515 receive buffers fill in about 0.5 ms. A 1 ms sleep would lose frames.
// The only SPI user of the MCP2515 is this task.
static void rxTask(void *) {
  int64_t lastStats = 0;
  while (true) {
    if (can.checkReceive() == CAN_MSGAVAIL) {
      CanFrame f;
      unsigned long rawId = 0;
      byte ext = 0;
      if (can.readMsgBuf(&rawId, &ext, &f.dlc, f.data) == CAN_OK) {
        f.t_us = esp_timer_get_time();
        f.id = rawId & 0x1FFFFFFF;
        f.ext = ext;
        stats.frames = stats.frames + 1;
        if (xQueueSend(queue, &f, 0) != pdTRUE) {
          stats.queue_drops = stats.queue_drops + 1;
        }
      }
    }

    int64_t now = esp_timer_get_time();
    if (now - lastStats >= STATS_PERIOD_US) {
      lastStats = now;
      if (can.getError() & (MCP_EFLG_RX0OVR | MCP_EFLG_RX1OVR)) {
        stats.hw_overflows = stats.hw_overflows + 1;
        clearOverflowFlags();
      }
      stats.rx_err = can.errorCountRX();
      stats.tx_err = can.errorCountTX();
    }
  }
}

bool can_rx_begin() {
  canSpi.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
  if (can.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
    return false;
  }
  can.setMode(MCP_NORMAL);

  queue = xQueueCreate(QUEUE_LEN, sizeof(CanFrame));
  if (queue == nullptr) {
    return false;
  }
  // Core 0 runs nothing else here (no WiFi), so the busy loop may starve its idle task.
  disableCore0WDT();
  xTaskCreatePinnedToCore(rxTask, "can_rx", 4096, nullptr, 5, nullptr, 0);
  return true;
}

bool can_rx_pop(CanFrame &frame) {
  return xQueueReceive(queue, &frame, 0) == pdTRUE;
}

CanStats can_rx_stats() {
  CanStats s;
  s.frames = stats.frames;
  s.queue_drops = stats.queue_drops;
  s.hw_overflows = stats.hw_overflows;
  s.rx_err = stats.rx_err;
  s.tx_err = stats.tx_err;
  return s;
}
