// can_logger - records every CAN frame on the bus to the microSD.
// Press BOOT to start a recording, press again to stop. Each recording is a new file.
//
// Modules, one job each:
//   can_rx   reads the MCP2515 into a RAM queue (own task, core 0)
//   sd_log   writes frames to a CSV file on the microSD
//   control  button and LED
//   this file  the state machine that connects them; knows nothing about SPI or files
//
// Serial (921600): "start", "stop", "ls", "cat log_001.csv". Lets the logs come off the
// card without a card reader.

#include "can_rx.h"
#include "sd_log.h"
#include "control.h"

enum class State { Idle, Recording, Error };

static State state = State::Idle;
static unsigned long lastSecond = 0;
static bool sdReady = false;

// Why the chip restarted. BROWNOUT = supply dipped below ~2.4 V on 3V3;
// PANIC = firmware crash; TASK_WDT / INT_WDT = something hung; POWERON = power was cut.
static const char *resetReasonName(esp_reset_reason_t r) {
  switch (r) {
    case ESP_RST_POWERON:   return "POWERON";
    case ESP_RST_EXT:       return "EXT_PIN";
    case ESP_RST_SW:        return "SOFTWARE";
    case ESP_RST_PANIC:     return "PANIC";
    case ESP_RST_INT_WDT:   return "INT_WDT";
    case ESP_RST_TASK_WDT:  return "TASK_WDT";
    case ESP_RST_WDT:       return "OTHER_WDT";
    case ESP_RST_DEEPSLEEP: return "DEEPSLEEP";
    case ESP_RST_BROWNOUT:  return "BROWNOUT";
    case ESP_RST_SDIO:      return "SDIO";
    default:                return "UNKNOWN";
  }
}

static void startRecording() {
  // Retry the card each time: it may have been inserted after boot.
  if (!sdReady) {
    sdReady = sd_log_begin();
  }
  if (!sdReady || !sd_log_open()) {
    sdReady = false;
    state = State::Error;
    Serial.println("SD not available - check the card");
    return;
  }
  state = State::Recording;
  lastSecond = millis();
  Serial.printf("recording to %s\n", sd_log_name());
}

static void stopRecording() {
  sd_log_close();
  state = State::Idle;
  Serial.printf("stopped, %s closed\n", sd_log_name());
}

static void handleSerial() {
  if (!Serial.available()) {
    return;
  }
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd == "start" && state != State::Recording) {
    startRecording();
  } else if (cmd == "stop" && state == State::Recording) {
    stopRecording();
  } else if (cmd == "ls" && state != State::Recording) {
    sd_log_list(Serial);
  } else if (cmd.startsWith("cat ") && state != State::Recording) {
    sd_log_dump(cmd.substring(4).c_str(), Serial);
  } else if (cmd.length() > 0) {
    Serial.println("commands: start, stop, ls, cat <file> (ls/cat only while stopped)");
  }
}

void setup() {
  Serial.begin(921600);
  control_begin();

  if (!can_rx_begin()) {
    Serial.println("MCP2515 init FAILED - check SPI wiring, divider and 5 V supply");
    while (true) { control_led(LedMode::Error); }
  }
  sdReady = sd_log_begin();
  const char *reason = resetReasonName(esp_reset_reason());
  if (sdReady) {
    sd_log_boot(reason);
  }
  Serial.printf("can_logger ready - last reset: %s - SD %s - press BOOT to record\n", reason,
                sdReady ? "OK" : "MISSING");
}

void loop() {
  if (control_pressed()) {
    if (state == State::Recording) {
      stopRecording();
    } else {
      startRecording();
    }
  }
  handleSerial();

  // Always drain the queue; while not recording the frames are simply dropped.
  CanFrame f;
  while (can_rx_pop(f)) {
    if (state == State::Recording && !sd_log_frame(f)) {
      sd_log_close();
      sdReady = false;
      state = State::Error;
      Serial.println("SD write FAILED - recording stopped");
    }
  }

  // Once a second: health line in the file and on serial, then flush.
  // A power cut loses at most this last second.
  if (state == State::Recording && millis() - lastSecond >= 1000) {
    lastSecond += 1000;
    CanStats s = can_rx_stats();
    sd_log_stats(s, esp_timer_get_time());
    sd_log_flush();
    Serial.printf("%s  frames %lu  queue drops %lu  hw overflows %lu  RX err %u  TX err %u"
                  "  SPI err %lu\n",
                  sd_log_name(), (unsigned long)s.frames, (unsigned long)s.queue_drops,
                  (unsigned long)s.hw_overflows, s.rx_err, s.tx_err,
                  (unsigned long)s.spi_errors);
  }

  control_led(state == State::Recording ? LedMode::Recording
              : state == State::Error   ? LedMode::Error
                                        : LedMode::Idle);
}
