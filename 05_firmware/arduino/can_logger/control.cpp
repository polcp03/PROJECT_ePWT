#include "control.h"
#include <Arduino.h>

static const uint8_t PIN_BUTTON = 0;  // BOOT, pressed = LOW
static const uint8_t PIN_LED = 2;
static const unsigned long DEBOUNCE_MS = 30;

static bool stableState = HIGH;
static bool lastReading = HIGH;
static unsigned long lastChange = 0;

void control_begin() {
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
}

bool control_pressed() {
  bool reading = digitalRead(PIN_BUTTON);
  if (reading != lastReading) {
    lastReading = reading;
    lastChange = millis();
  }
  if (millis() - lastChange >= DEBOUNCE_MS && reading != stableState) {
    stableState = reading;
    return stableState == LOW;
  }
  return false;
}

// Idle: short blink every 2 s (alive). Recording: solid. Error: fast blink.
void control_led(LedMode mode) {
  unsigned long t = millis();
  bool on = false;
  switch (mode) {
    case LedMode::Idle:      on = (t % 2000) < 100; break;
    case LedMode::Recording: on = true; break;
    case LedMode::Error:     on = (t % 200) < 100; break;
  }
  digitalWrite(PIN_LED, on);
}
