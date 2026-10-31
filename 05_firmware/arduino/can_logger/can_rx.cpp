#include "can_rx.h"
#include <Arduino.h>
#include <SPI.h>
#include <mcp_can.h>

// HSPI, separate from the SD card on VSPI. MISO goes through the 1k / 2k divider.
static const int8_t PIN_SCK = 14;
static const int8_t PIN_MISO = 27;
static const int8_t PIN_MOSI = 13;
static const int8_t PIN_CS = 26;

// 4 MHz instead of the library's 10 MHz: the divider and breadboard wires round off
// the MISO edges, and at 10 MHz bits flipped. 300 frames/s needs well under 1 MHz.
static const SPISettings SPI_CFG(4000000, MSBFIRST, SPI_MODE0);

// 1024 frames = about 3 s of VESC traffic at 300 frames/s before the SD must catch up.
static const int QUEUE_LEN = 1024;
static const int64_t STATS_PERIOD_US = 10000;

// MCP2515 SPI instructions and registers (datasheet DS20001801, section 12)
static const uint8_t INS_READ = 0x03;
static const uint8_t INS_BIT_MODIFY = 0x05;
static const uint8_t INS_READ_STATUS = 0xA0;
static const uint8_t INS_READ_RXB0 = 0x90;  // reading from RXB0SIDH clears RX0IF on CS high
static const uint8_t INS_READ_RXB1 = 0x94;
static const uint8_t REG_TEC = 0x1C;
static const uint8_t REG_REC = 0x1D;
static const uint8_t REG_EFLG = 0x2D;

static SPIClass canSpi(HSPI);
static MCP_CAN can(&canSpi, PIN_CS);  // only used to configure the chip at boot
static QueueHandle_t queue;
static volatile CanStats stats;

static uint8_t readRegister(uint8_t addr) {
  canSpi.beginTransaction(SPI_CFG);
  digitalWrite(PIN_CS, LOW);
  canSpi.transfer(INS_READ);
  canSpi.transfer(addr);
  uint8_t v = canSpi.transfer(0);
  digitalWrite(PIN_CS, HIGH);
  canSpi.endTransaction();
  return v;
}

// Clears the overflow bits 7:6 of EFLG, which otherwise stay set forever.
static void clearOverflowFlags() {
  canSpi.beginTransaction(SPI_CFG);
  digitalWrite(PIN_CS, LOW);
  canSpi.transfer(INS_BIT_MODIFY);
  canSpi.transfer(REG_EFLG);
  canSpi.transfer(0xC0);
  canSpi.transfer(0x00);
  digitalWrite(PIN_CS, HIGH);
  canSpi.endTransaction();
}

static uint8_t readStatus() {
  canSpi.beginTransaction(SPI_CFG);
  digitalWrite(PIN_CS, LOW);
  canSpi.transfer(INS_READ_STATUS);
  uint8_t s = canSpi.transfer(0);
  digitalWrite(PIN_CS, HIGH);
  canSpi.endTransaction();
  return s;
}

// Reads one receive buffer in a single SPI transaction: SIDH SIDL EID8 EID0 DLC D0..D7.
// Written here instead of using the library because the library trusts the DLC:
// a corrupted DLC of 9..15 made it copy past its 8-byte buffer and crash the ESP32.
static void readBuffer(uint8_t instruction, CanFrame &f) {
  uint8_t r[13];
  canSpi.beginTransaction(SPI_CFG);
  digitalWrite(PIN_CS, LOW);
  canSpi.transfer(instruction);
  for (uint8_t i = 0; i < sizeof(r); i++) {
    r[i] = canSpi.transfer(0);
  }
  digitalWrite(PIN_CS, HIGH);
  canSpi.endTransaction();

  uint32_t sid = ((uint32_t)r[0] << 3) | (r[1] >> 5);
  f.ext = (r[1] & 0x08) ? 1 : 0;
  f.id = f.ext ? (sid << 18) | ((uint32_t)(r[1] & 0x03) << 16) | ((uint32_t)r[2] << 8) | r[3]
               : sid;
  f.dlc = r[4] & 0x0F;  // kept as read, so a corrupted value stays visible in the log
  uint8_t n = f.dlc > 8 ? 8 : f.dlc;
  memset(f.data, 0, sizeof(f.data));
  memcpy(f.data, &r[5], n);
}

static void push(CanFrame &f) {
  f.t_us = esp_timer_get_time();
  stats.frames = stats.frames + 1;
  if (xQueueSend(queue, &f, 0) != pdTRUE) {
    stats.queue_drops = stats.queue_drops + 1;
  }
}

// Busy-polls on purpose: the VESC sends its status frames back to back,
// so both MCP2515 receive buffers fill in about 0.5 ms. A 1 ms sleep would lose frames.
// The only SPI user of the MCP2515 is this task.
static void rxTask(void *) {
  int64_t lastStats = 0;
  while (true) {
    uint8_t status = readStatus();
    CanFrame f;
    if (status & 0x01) {  // RX0IF
      readBuffer(INS_READ_RXB0, f);
      push(f);
    }
    if (status & 0x02) {  // RX1IF
      readBuffer(INS_READ_RXB1, f);
      push(f);
    }

    int64_t now = esp_timer_get_time();
    if (now - lastStats >= STATS_PERIOD_US) {
      lastStats = now;
      if (readRegister(REG_EFLG) & 0xC0) {  // RX1OVR | RX0OVR
        stats.hw_overflows = stats.hw_overflows + 1;
        clearOverflowFlags();
      }
      stats.rx_err = readRegister(REG_REC);
      stats.tx_err = readRegister(REG_TEC);
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
