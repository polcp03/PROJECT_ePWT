// can_loopback - throwaway hardware bring-up test. Not the logger.
// Goal: prove the ESP32 <-> MCP2515 SPI link works, with nothing on CAN-H/CAN-L.
// In loopback mode the MCP2515 receives its own frames internally: no bus, no VESC.
//
// The MCP2515 runs on its own SPI bus so it cannot fight the SD card on VSPI.
// Wiring (HSPI): SCK 14, MOSI 13, MISO 27 (through a 1k / 2k divider), CS 26.
// Module VCC on VIN (5 V), GND on GND. Its SO pin is 5 V, hence the divider.

#include <SPI.h>
#include <mcp_can.h>

const int8_t PIN_SCK = 14;
const int8_t PIN_MISO = 27;
const int8_t PIN_MOSI = 13;
const int8_t PIN_CS = 26;

SPIClass canSpi(HSPI);
MCP_CAN can(&canSpi, PIN_CS);

uint32_t sent = 0;
uint32_t received = 0;
uint32_t mismatched = 0;
unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Start the bus on our pins first; the library's own begin() then leaves it alone.
  canSpi.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);

  // MCP_8MHZ = the module's crystal. 500 kbit/s = what the VESC will use later.
  if (can.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
    Serial.println("MCP2515 init FAILED - check SPI wiring, divider and 5 V supply");
    while (true) { delay(1000); }
  }

  can.setMode(MCP_LOOPBACK);
  Serial.println("MCP2515 ready - loopback mode, 500 kbit/s");
}

void loop() {
  if (millis() - lastSend >= 500) {
    lastSend = millis();
    byte data[4] = {
      (byte)(sent >> 24), (byte)(sent >> 16), (byte)(sent >> 8), (byte)sent
    };
    if (can.sendMsgBuf(0x123, 0, sizeof(data), data) == CAN_OK) {
      sent++;
    } else {
      Serial.println("send FAILED");
    }
  }

  if (can.checkReceive() == CAN_MSGAVAIL) {
    unsigned long id = 0;
    byte len = 0;
    byte buf[8];
    if (can.readMsgBuf(&id, &len, buf) == CAN_OK) {
      uint32_t counter = ((uint32_t)buf[0] << 24) | ((uint32_t)buf[1] << 16) |
                         ((uint32_t)buf[2] << 8) | buf[3];
      received++;
      if (id != 0x123 || len != 4 || counter != received - 1) {
        mismatched++;
      }
      Serial.printf("RX ID 0x%03lX counter %lu | sent %lu received %lu bad %lu\n",
                    id, (unsigned long)counter, (unsigned long)sent,
                    (unsigned long)received, (unsigned long)mismatched);
    }
  }
}
