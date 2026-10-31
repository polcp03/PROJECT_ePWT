// sd_test - throwaway hardware bring-up test. Not the logger.
// Goal: prove the ESP32 <-> microSD module wiring is alive.
// Writes a few CSV lines, reads them back and prints them.
// Wiring (VSPI): SCK 18, MISO 19, MOSI 23, CS 5. Module VCC on VIN (5 V), GND on GND.

#include <SPI.h>
#include <SD.h>

const uint8_t PIN_CS = 5;
const char *FILE_PATH = "/sd_test.csv";

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!SD.begin(PIN_CS)) {
    Serial.println("SD init FAILED - check wiring, card inserted, card formatted FAT32");
    while (true) { delay(1000); }
  }

  Serial.printf("SD ready - card type %u, size %llu MB\n",
                SD.cardType(), SD.cardSize() / (1024ULL * 1024ULL));

  File f = SD.open(FILE_PATH, FILE_WRITE);
  if (!f) {
    Serial.println("Open for write FAILED");
    while (true) { delay(1000); }
  }
  f.println("t_ms,value");
  for (int i = 0; i < 5; i++) {
    f.printf("%lu,%d\n", (unsigned long)millis(), i);
    delay(100);
  }
  f.close();

  f = SD.open(FILE_PATH, FILE_READ);
  Serial.println("--- read back ---");
  while (f.available()) {
    Serial.write(f.read());
  }
  f.close();
  Serial.println("--- SD test PASSED ---");
}

void loop() {
}
