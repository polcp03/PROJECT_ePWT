// hall_test - throwaway hardware bring-up test. Not the logger.
// Goal: prove the ESP32 <-> 3144 Hall sensor (wheel speed) wiring is alive.
// Prints the output level and how many magnet passes it has counted.
// Wiring: 3144 VCC on VIN (5 V), GND on GND, OUT on GPIO 34.
// GPIO 34 has no internal pull-up: 10 kOhm OUT -> 3V3 (never to 5 V).
// Output is open collector: 1 = no magnet, 0 = south pole facing the marked side.

const uint8_t PIN_HALL = 34;

volatile uint32_t passes = 0;

void IRAM_ATTR onFalling() { passes++; }

void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(PIN_HALL, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL), onFalling, FALLING);
}

// Prints on every level change (polled every 1 ms) plus a heartbeat every 2 s.
void loop() {
  static int lastLevel = -1;
  static uint32_t lastBeat = 0;
  int level = digitalRead(PIN_HALL);
  if (level != lastLevel) {
    Serial.printf("t=%lu ms  OUT=%d (%s)  passes=%lu\n", millis(), level,
                  level ? "no magnet" : "MAGNET", (unsigned long)passes);
    lastLevel = level;
  }
  if (millis() - lastBeat >= 2000) {
    Serial.printf("t=%lu ms  alive, OUT=%d  passes=%lu\n", millis(), level, (unsigned long)passes);
    lastBeat = millis();
  }
  delay(1);
}
