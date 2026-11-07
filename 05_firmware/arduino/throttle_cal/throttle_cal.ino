// throttle_cal — measure the throttle grip on GPIO 35, nothing else.
//
// Bench tool, not the VCU: it decides nothing, it only measures. Its numbers
// (rest, full, noise) are what the throttle module's contract will be written from.
//
// Wiring (bench, 2026-11-05): grip + -> 3V3, grip GND -> GND, signal -> GPIO 35.
// At 3.3 V the grip measured 0.8-2.6 V with the multimeter, so no divider is needed.
//
// Prints 10 times a second:  mV now | min | max | noise (max-min within the 32 samples of this reading)
// Type "reset" + Enter in the monitor to clear min and max.

const int PIN_THROTTLE = 35;      // ADC1 channel 7: works with Wi-Fi on
const int SAMPLES      = 32;      // averaged per reading, against ADC noise
const uint32_t PRINT_MS = 100;    // 10 Hz

uint32_t minMv = UINT32_MAX;
uint32_t maxMv = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_THROTTLE, ADC_11db);  // range up to ~3.1 V
  delay(200);
  Serial.println();
  Serial.println("throttle_cal: mV | min | max | noise   (type 'reset' to clear)");
}

void loop() {
  static uint32_t lastPrint = 0;

  // Average SAMPLES calibrated readings (analogReadMilliVolts uses the chip's eFuse calibration).
  uint32_t sum = 0, lo = UINT32_MAX, hi = 0;
  for (int i = 0; i < SAMPLES; i++) {
    uint32_t mv = analogReadMilliVolts(PIN_THROTTLE);
    sum += mv;
    if (mv < lo) lo = mv;
    if (mv > hi) hi = mv;
  }
  uint32_t mv = sum / SAMPLES;
  if (mv < minMv) minMv = mv;
  if (mv > maxMv) maxMv = mv;

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "reset") {
      minMv = UINT32_MAX;
      maxMv = 0;
      Serial.println("-- min/max cleared --");
    }
  }

  // Unsigned subtraction: still correct when millis() wraps after 49.7 days.
  if (millis() - lastPrint >= PRINT_MS) {
    lastPrint = millis();
    Serial.printf("%4lu mV | min %4lu | max %4lu | noise %3lu\n",
                  (unsigned long)mv, (unsigned long)minMv,
                  (unsigned long)maxMv, (unsigned long)(hi - lo));
  }
}
