// wheel_capture - raw data capture for the wheel speed sensor. No filtering.
// Goal: see what the 3144 output really looks like with the wheel spinning,
// before deciding how to turn pulses into speed.
// Wiring: 3144 VCC on VIN (5 V), GND on GND, OUT on GPIO 34, 10 kOhm OUT -> 3V3.
// Wheel: 10 magnets. Output 0 = magnet in front of the sensor.
//
// Output, one CSV line per level change seen by polling the pin (every ~1 us):
//   t_us,level,isr_edges
// isr_edges = falling edges the interrupt saw since the previous line. If it is
// much bigger than 1, the line has glitches too short for the polling to see.

const uint8_t PIN_HALL = 34;

volatile uint32_t isrEdges = 0;

void IRAM_ATTR onFalling() { isrEdges++; }

// GPIO 34 lives in the second input register (pins 32-39), bit 34 - 32 = 2.
static inline int readHall() { return (REG_READ(GPIO_IN1_REG) >> (PIN_HALL - 32)) & 1; }

void setup() {
  Serial.begin(921600);
  delay(1000);
  pinMode(PIN_HALL, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL), onFalling, FALLING);
  Serial.println("t_us,level,isr_edges");
}

void loop() {
  static int lastLevel = -1;
  static uint32_t lastBeat = 0;
  int level = readHall();
  uint32_t now = micros();
  if (level != lastLevel) {
    uint32_t edges = isrEdges;
    isrEdges = 0;
    Serial.printf("%lu,%d,%lu\n", now, level, edges);
    lastLevel = level;
  }
  if (now - lastBeat >= 2000000) {  // heartbeat so a still wheel is not silence
    Serial.printf("# alive %lu, isr_edges pending %lu\n", now, isrEdges);
    lastBeat = now;
  }
}
