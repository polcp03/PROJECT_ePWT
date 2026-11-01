// imu_scan - throwaway hardware bring-up test. Not the logger.
// Goal: prove the ESP32 <-> LSM6DS3 IMU wiring is alive and reliable.
// Scans the I2C bus once, then reads WHO_AM_I 100 times per round and
// prints how many reads came back right.
// Wiring: SDA 21, SCL 22. Module VIN and CS on 3V3, SAO on GND (address 0x6A).
// 10 kOhm pull-up SDA -> 3V3 added by hand (the module's own was torn off).

#include <Wire.h>

const int8_t PIN_SDA = 21;
const int8_t PIN_SCL = 22;
const uint8_t IMU_ADDR = 0x6A;
const uint8_t REG_WHO_AM_I = 0x0F;  // 0x69 = LSM6DS3
const uint8_t WHO_AM_I_EXPECTED = 0x69;
const int READS_PER_ROUND = 100;

int readRegister(uint8_t addr, uint8_t reg) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;  // repeated start
  if (Wire.requestFrom(addr, (uint8_t)1) != 1) return -1;
  return Wire.read();
}

// If a slave was left mid-byte it may hold SDA low: clock SCL until it lets go.
void busRecover() {
  pinMode(PIN_SDA, INPUT);
  pinMode(PIN_SCL, OUTPUT);
  for (int i = 0; i < 9; i++) {
    digitalWrite(PIN_SCL, LOW); delayMicroseconds(10);
    digitalWrite(PIN_SCL, HIGH); delayMicroseconds(10);
  }
  pinMode(PIN_SCL, INPUT);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  busRecover();
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);

  Serial.println("--- I2C scan ---");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) Serial.printf("device at 0x%02X\n", addr);
  }
}

void loop() {
  int ok = 0, noAnswer = 0, wrong = 0;
  for (int i = 0; i < READS_PER_ROUND; i++) {
    int who = readRegister(IMU_ADDR, REG_WHO_AM_I);
    if (who == WHO_AM_I_EXPECTED) ok++;
    else if (who < 0) noAnswer++;
    else wrong++;
    delay(5);
  }
  Serial.printf("WHO_AM_I: %d/%d ok, %d no answer, %d wrong value\n",
                ok, READS_PER_ROUND, noAnswer, wrong);
}
