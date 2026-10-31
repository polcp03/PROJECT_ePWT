#include "sd_log.h"
#include <SD.h>

// VSPI default pins: SCK 18, MISO 19, MOSI 23.
static const uint8_t PIN_CS = 5;

static File file;
static char fileName[16] = "";
static int64_t t0 = 0;
static char bootLine[48] = "";

bool sd_log_begin() {
  return SD.begin(PIN_CS);
}

// One line per boot in /boot.txt, so restarts in the field leave a trace.
void sd_log_boot(const char *reason) {
  int n = 1;
  File f = SD.open("/boot.txt", FILE_READ);
  if (f) {
    while (f.available()) {
      if (f.read() == '\n') n++;
    }
    f.close();
  }
  snprintf(bootLine, sizeof(bootLine), "#boot,%d,%s", n, reason);
  f = SD.open("/boot.txt", FILE_APPEND);
  if (f) {
    f.println(bootLine + 1);  // without the '#'
    f.close();
  }
}

// Next number = highest existing log_NNN.csv + 1, so old recordings are never overwritten.
static int nextLogNumber() {
  int highest = 0;
  File root = SD.open("/");
  for (File f = root.openNextFile(); f; f = root.openNextFile()) {
    int n = 0;
    if (sscanf(f.name(), "log_%d.csv", &n) == 1 && n > highest) {
      highest = n;
    }
    f.close();
  }
  root.close();
  return highest + 1;
}

bool sd_log_open() {
  snprintf(fileName, sizeof(fileName), "/log_%03d.csv", nextLogNumber());
  file = SD.open(fileName, FILE_WRITE);
  if (!file) {
    return false;
  }
  if (bootLine[0]) {
    file.println(bootLine);
  }
  file.println("t_us,id,ext,dlc,d0,d1,d2,d3,d4,d5,d6,d7");
  t0 = esp_timer_get_time();
  return true;
}

bool sd_log_frame(const CanFrame &f) {
  // Frames queued while the file was being opened belong to before the recording.
  if (f.t_us < t0) {
    return true;
  }
  char line[80];
  int n = snprintf(line, sizeof(line), "%lld,%lX,%u,%u",
                   (long long)(f.t_us - t0), (unsigned long)f.id, f.ext, f.dlc);
  for (uint8_t i = 0; i < 8; i++) {
    if (i < f.dlc) {
      n += snprintf(line + n, sizeof(line) - n, ",%02X", f.data[i]);
    } else {
      n += snprintf(line + n, sizeof(line) - n, ",");
    }
  }
  line[n++] = '\n';
  return file.write((const uint8_t *)line, n) == (size_t)n;
}

void sd_log_stats(const CanStats &s, int64_t t_us) {
  file.printf("#stat,%lld,%lu,%lu,%lu,%u,%u,%lu\n", (long long)(t_us - t0),
              (unsigned long)s.frames, (unsigned long)s.queue_drops,
              (unsigned long)s.hw_overflows, s.rx_err, s.tx_err,
              (unsigned long)s.spi_errors);
}

void sd_log_flush() {
  file.flush();
}

void sd_log_close() {
  file.close();
}

const char *sd_log_name() {
  return fileName;
}

void sd_log_list(Stream &out) {
  File root = SD.open("/");
  for (File f = root.openNextFile(); f; f = root.openNextFile()) {
    out.printf("%s\t%lu bytes\n", f.name(), (unsigned long)f.size());
    f.close();
  }
  root.close();
}

void sd_log_dump(const char *name, Stream &out) {
  char path[32];
  snprintf(path, sizeof(path), "%s%s", name[0] == '/' ? "" : "/", name);
  File f = SD.open(path, FILE_READ);
  if (!f) {
    out.printf("cannot open %s\n", path);
    return;
  }
  uint8_t buf[512];
  while (f.available()) {
    int n = f.read(buf, sizeof(buf));
    out.write(buf, n);
  }
  f.close();
  out.println("--- end of file ---");
}
