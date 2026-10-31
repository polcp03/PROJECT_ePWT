// can_vesc - throwaway bring-up test. Not the logger.
// Goal: receive and decode the VESC status frames over the MCP2515.
// Normal mode, but never transmits: the MCP2515 only ACKs what it receives,
// otherwise the VESC would resend every frame forever.
//
// Wiring: same as can_loopback (HSPI, divider on SO) plus
// CAN-H -> VESC CAN-H, CAN-L -> VESC CAN-L, GND -> VESC GND. Nothing else.
//
// VESC status frames are extended IDs: (packet id << 8) | VESC ID.
// Packet ids and scaling from the VESC firmware (comm_can.c, FW 7.01).

#include <SPI.h>
#include <mcp_can.h>

const int8_t PIN_SCK = 14;
const int8_t PIN_MISO = 27;
const int8_t PIN_MOSI = 13;
const int8_t PIN_CS = 26;

const uint8_t PKT_STATUS_1 = 9;   // ERPM, motor current, duty
const uint8_t PKT_STATUS_2 = 14;  // amp-hours used / charged
const uint8_t PKT_STATUS_3 = 15;  // watt-hours used / charged
const uint8_t PKT_STATUS_4 = 16;  // FET temp, motor temp, battery current

SPIClass canSpi(HSPI);
MCP_CAN can(&canSpi, PIN_CS);

uint32_t framesThisSecond = 0;
unsigned long lastReport = 0;

int32_t be32(const byte *b) {
  return ((int32_t)b[0] << 24) | ((int32_t)b[1] << 16) | ((int32_t)b[2] << 8) | b[3];
}

int16_t be16(const byte *b) {
  return (int16_t)(((uint16_t)b[0] << 8) | b[1]);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  canSpi.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);

  if (can.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
    Serial.println("MCP2515 init FAILED - check SPI wiring, divider and 5 V supply");
    while (true) { delay(1000); }
  }

  can.setMode(MCP_NORMAL);
  Serial.println("MCP2515 ready - normal mode, 500 kbit/s, receive only");
}

void loop() {
  if (can.checkReceive() == CAN_MSGAVAIL) {
    unsigned long rawId = 0;
    byte len = 0;
    byte buf[8];

    if (can.readMsgBuf(&rawId, &len, buf) == CAN_OK) {
      framesThisSecond++;
      // The library flags extended frames by setting bit 31 of the id.
      unsigned long id = rawId & 0x1FFFFFFF;
      uint8_t packet = (id >> 8) & 0xFF;
      uint8_t vescId = id & 0xFF;

      if (packet == PKT_STATUS_1 && len == 8) {
        Serial.printf("[%u] STATUS_1  erpm %ld  I_motor %.1f A  duty %.3f\n",
                      vescId, (long)be32(&buf[0]), be16(&buf[4]) / 10.0,
                      be16(&buf[6]) / 1000.0);
      } else if (packet == PKT_STATUS_4 && len == 8) {
        Serial.printf("[%u] STATUS_4  T_fet %.1f C  T_motor %.1f C  I_batt %.1f A\n",
                      vescId, be16(&buf[0]) / 10.0, be16(&buf[2]) / 10.0,
                      be16(&buf[4]) / 10.0);
      } else if (packet != PKT_STATUS_2 && packet != PKT_STATUS_3) {
        Serial.printf("other ID 0x%08lX DLC %u\n", id, len);
      }
    }
  }

  // Once a second: frame rate and error counters, so silence and bus errors are visible.
  if (millis() - lastReport >= 1000) {
    lastReport = millis();
    Serial.printf("--- %lu frames/s  RX err %u  TX err %u ---\n",
                  (unsigned long)framesThisSecond, can.errorCountRX(), can.errorCountTX());
    framesThisSecond = 0;
  }
}
