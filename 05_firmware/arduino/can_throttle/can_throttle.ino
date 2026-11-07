// can_throttle - throwaway bring-up test. Not the VCU.
// Goal: the ESP32 reads the throttle grip and commands the VESC's motor current over CAN.
//
// Contract (signed by Pol, 2026-11-05):
//   in   throttle on GPIO 35, mV (grip powered from 3V3, measured 804 rest / 2600 full)
//   out  CAN_PACKET_SET_CURRENT to VESC id 15, every 10 ms (REQ-VCU-01)
//   map  <= 900 mV -> 0 A, >= 2550 mV -> 10 A, linear between. CAP 10 A for this test
//   fail < 600 or > 2800 mV -> 0 A, latched. The VESC's own CAN timeout (100 ms) covers a
//        dead ESP32 or a cut CAN cable.
//   arm  sends 0 A until the VESC is answering AND the grip has read "rest" for 0.5 s,
//        at power-up and after every CAN loss.
//
// Fixes after the first unplug test (2026-11-05):
//   1. VESC data older than 100 ms is shown as "--", never as the last good value.
//   2. CAN loss (VESC silent > 100 ms, or a send fails) -> back to WAIT_REST, and the
//      MCP2515 is reset so its queued (stale, non-zero) current frames are thrown away.
//
// Timeout measurement: type "silence" + Enter. The ESP32 stops sending, keeps listening,
// and prints how many ms after its last frame the VESC's motor current reached ~0 A.
//
// Wiring: as can_vesc (HSPI, SO divider) + CAN-H/CAN-L to the VESC. Throttle as throttle_cal.

#include <SPI.h>
#include <mcp_can.h>

// ---- pins ----
const int8_t PIN_SCK = 14, PIN_MISO = 27, PIN_MOSI = 13, PIN_CS = 26;
const int PIN_THROTTLE = 35;

// ---- contract numbers ----
const int32_t MV_ZERO  = 900;    // at or below: 0 %
const int32_t MV_FULL  = 2550;   // at or above: 100 %
const int32_t MV_FAULT_LOW  = 600;
const int32_t MV_FAULT_HIGH = 2800;
const int32_t MA_CAP   = 10000;  // 10 A, this test only
const uint32_t SEND_MS = 10;
const uint32_t ARM_MS  = 500;
const uint32_t VESC_STALE_MS = 100;  // STATUS_1 arrives every ~21 ms; 100 ms = ~5 missing
const uint32_t RESET_MIN_MS = 500;   // do not reset the MCP2515 more often than this

// ---- silence test ----
const float    ZERO_A = 0.5f;        // "current is zero" threshold, A
const uint32_t SILENCE_MAX_MS = 1000;

// ---- VESC CAN ----
const uint8_t VESC_ID = 15;
const uint8_t PKT_SET_CURRENT = 1;
const uint8_t PKT_STATUS_1 = 9;   // ERPM, motor current, duty

SPIClass canSpi(HSPI);
MCP_CAN can(&canSpi, PIN_CS);

enum State { WAIT_REST, ARMED, FAULT, SILENCE };
const char *stateName[] = {"WAIT_REST", "ARMED", "FAULT", "SILENCE"};

// What we last heard from the VESC, and when.
struct VescStatus {
  float amps = 0;
  long erpm = 0;
  uint32_t atMs = 0;
  bool everSeen = false;
};
VescStatus vesc;

bool vescFresh() {
  return vesc.everSeen && (millis() - vesc.atMs) <= VESC_STALE_MS;
}

// Averaged, calibrated reading of the grip in mV.
int32_t readThrottleMv() {
  uint32_t sum = 0;
  for (int i = 0; i < 32; i++) sum += analogReadMilliVolts(PIN_THROTTLE);
  return (int32_t)(sum / 32);
}

// Pure logic, no hardware: mV -> mA request. Returns -1 when out of the window.
int32_t throttleToMa(int32_t mv) {
  if (mv < MV_FAULT_LOW || mv > MV_FAULT_HIGH) return -1;
  if (mv <= MV_ZERO) return 0;
  if (mv >= MV_FULL) return MA_CAP;
  // int64 so (mv - MV_ZERO) * MA_CAP cannot overflow (1650 * 10000 fits, but a later cap may not).
  return (int32_t)((int64_t)(mv - MV_ZERO) * MA_CAP / (MV_FULL - MV_ZERO));
}

bool canInit() {
  // begin() sends the MCP2515 a RESET over SPI: this also empties its 3 TX buffers.
  if (can.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ) != CAN_OK) return false;
  can.setMode(MCP_NORMAL);
  return true;
}

// VESC frames: extended id = (packet << 8) | vesc id, payload big-endian.
bool sendSetCurrent(int32_t ma) {
  byte buf[4] = {(byte)(ma >> 24), (byte)(ma >> 16), (byte)(ma >> 8), (byte)ma};
  uint32_t id = ((uint32_t)PKT_SET_CURRENT << 8) | VESC_ID;
  return can.sendMsgBuf(id, 1, 4, buf) == CAN_OK;
}

int32_t be32(const byte *b) {
  return ((int32_t)b[0] << 24) | ((int32_t)b[1] << 16) | ((int32_t)b[2] << 8) | b[3];
}
int16_t be16(const byte *b) { return (int16_t)(((uint16_t)b[0] << 8) | b[1]); }

void readVesc() {
  while (can.checkReceive() == CAN_MSGAVAIL) {
    unsigned long rawId; byte len; byte buf[8];
    if (can.readMsgBuf(&rawId, &len, buf) != CAN_OK) break;
    unsigned long id = rawId & 0x1FFFFFFF;
    if (((id >> 8) & 0xFF) == PKT_STATUS_1 && (id & 0xFF) == VESC_ID && len == 8) {
      vesc.erpm = be32(&buf[0]);
      vesc.amps = be16(&buf[4]) / 10.0f;
      vesc.atMs = millis();
      vesc.everSeen = true;
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_THROTTLE, ADC_11db);

  canSpi.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
  if (!canInit()) {
    Serial.println("MCP2515 init FAILED - check SPI wiring, divider and 5 V supply");
    while (true) delay(1000);
  }
  Serial.println("can_throttle: cap 10 A. Release the grip to arm. Type 'silence' to measure the VESC timeout.");
}

void loop() {
  static State state = WAIT_REST;
  // lastSend starts at "now" (set on the first loop), so the 10 ms schedule does not
  // burst to catch up with the time spent in setup().
  static uint32_t lastSend = millis(), lastPrint = 0, restSince = 0, lastReset = 0;
  static uint32_t sent = 0, sendFail = 0, canLosses = 0;
  static uint32_t silenceStart = 0, lastFrameMs = 0;
  static int32_t mv = 0, reqMa = 0;

  readVesc();

  // Serial commands.
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "silence" && state == ARMED && vescFresh()) {
      state = SILENCE;
      silenceStart = millis();
      Serial.printf("-- silence: last frame at %lu ms, VESC was at %.1f A, %ld erpm --\n",
                    (unsigned long)lastFrameMs, vesc.amps, vesc.erpm);
    } else if (cmd == "silence") {
      Serial.println("-- silence needs ARMED, VESC answering and the motor spinning --");
    }
  }

  // ---- silence test: send nothing, watch the VESC's current fall ----
  if (state == SILENCE) {
    static uint32_t lastSeenAt = 0;
    if (vesc.atMs != lastSeenAt) {          // a new STATUS_1 arrived
      lastSeenAt = vesc.atMs;
      if (fabsf(vesc.amps) < ZERO_A) {
        Serial.printf("-- VESC current %.1f A after %lu ms without frames (erpm %ld: coasting) --\n",
                      vesc.amps, (unsigned long)(vesc.atMs - lastFrameMs), vesc.erpm);
        Serial.println("-- back to WAIT_REST: release the grip to re-arm --");
        state = WAIT_REST; restSince = 0;
      }
    }
    if (state == SILENCE && millis() - silenceStart > SILENCE_MAX_MS) {
      Serial.printf("-- FAIL: VESC still at %.1f A after %lu ms without frames --\n",
                    vesc.amps, (unsigned long)(millis() - lastFrameMs));
      state = WAIT_REST; restSince = 0;
    }
    lastSend = millis();                     // so normal sending resumes on schedule
  }

  // ---- normal 10 ms cycle ----
  // Unsigned subtraction: correct across the millis() wrap.
  if (state != SILENCE && millis() - lastSend >= SEND_MS) {
    lastSend += SEND_MS;
    mv = readThrottleMv();
    int32_t ma = throttleToMa(mv);

    switch (state) {
      case WAIT_REST:
        if (ma == 0 && vescFresh()) {
          if (restSince == 0) restSince = millis();
          if (millis() - restSince >= ARM_MS) state = ARMED;
        } else {
          restSince = 0;
        }
        reqMa = 0;
        break;
      case ARMED:
        if (ma < 0) { state = FAULT; reqMa = 0; }
        else reqMa = ma;
        break;
      case FAULT:   // stays here until reset: a fault is looked at, not ignored
      case SILENCE:
        reqMa = 0;
        break;
    }

    bool ok = sendSetCurrent(reqMa);
    if (ok) { sent++; lastFrameMs = millis(); } else sendFail++;

    // CAN loss: the VESC went quiet, or the TX buffers are full of frames nobody ACKs.
    if (state == ARMED && (!ok || !vescFresh())) {
      state = WAIT_REST; restSince = 0; reqMa = 0;
      canLosses++;
    }
    // Throw away queued frames: they may hold an old non-zero current. Rate-limited,
    // because while the cable is out every send fails.
    if (!ok && millis() - lastReset >= RESET_MIN_MS) {
      lastReset = millis();
      canInit();
    }
  }

  if (millis() - lastPrint >= 200) {
    lastPrint = millis();
    if (vescFresh())
      Serial.printf("%4ld mV | %-9s | ask %5.2f A | VESC ok %5.1f A %6ld erpm | sent %lu fail %lu losses %lu | TXerr %u\n",
                    (long)mv, stateName[state], reqMa / 1000.0f, vesc.amps, vesc.erpm,
                    (unsigned long)sent, (unsigned long)sendFail, (unsigned long)canLosses,
                    can.errorCountTX());
    else
      Serial.printf("%4ld mV | %-9s | ask %5.2f A | VESC --  (silent)         | sent %lu fail %lu losses %lu | TXerr %u\n",
                    (long)mv, stateName[state], reqMa / 1000.0f,
                    (unsigned long)sent, (unsigned long)sendFail, (unsigned long)canLosses,
                    can.errorCountTX());
  }
}
