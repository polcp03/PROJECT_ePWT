// Sketch that checks the build chain.
// It does nothing useful: it only proves arduino-cli compiles for the ESP32.
#include <Arduino.h>

// The generic esp32:esp32:esp32 board does not define LED_PIN.
static const uint8_t LED_PIN = 2;

static const uint32_t LOOP_PERIOD_MS = 500;
static uint32_t last_tick = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  const uint32_t now = millis();
  if (now - last_tick >= LOOP_PERIOD_MS) {
    last_tick = now;
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    Serial.printf("t=%lu ms\n", (unsigned long)now);
  }
}
