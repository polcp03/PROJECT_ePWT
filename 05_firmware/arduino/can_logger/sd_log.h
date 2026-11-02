// sd_log - owns the microSD. One CSV file per recording: /log_001.csv, /log_002.csv...
// Stores raw frames; decoding happens on the PC, so a new CAN node never changes this module.
//
// File format:
//   #boot,<n>,<reset reason>                       why the ESP32 last restarted
//   t_us,id,ext,dlc,d0,d1,d2,d3,d4,d5,d6,d7      t_us since recording start, id and data in hex
//   #stat,t_us,frames,queue_drops,hw_overflows,rx_err,tx_err,spi_errors   once per second
//   #wheel,t_us                                    one line per magnet on the front wheel
//   #wstat,t_us,pulses,rejected,queue_drops         wheel sensor health, once per second
// pandas: read_csv(path, comment='#') skips the # lines, so the CAN part reads as before.
#pragma once
#include <Stream.h>
#include "can_frame.h"

bool sd_log_begin();                    // false if no card or not FAT32
void sd_log_boot(const char *reason);   // appends to /boot.txt; also goes into each log header
bool sd_log_open();                     // opens the next free log_NNN.csv
bool sd_log_frame(const CanFrame &f);   // false if the write failed (card removed, full)
void sd_log_stats(const CanStats &s, int64_t t_us);
bool sd_log_wheel(int64_t t_us);        // one magnet; t_us is esp_timer time, like CanFrame
void sd_log_wheel_stats(uint32_t pulses, uint32_t rejected, uint32_t queue_drops, int64_t t_us);
void sd_log_flush();                    // what has been flushed survives a power cut
void sd_log_close();
const char *sd_log_name();

void sd_log_list(Stream &out);
void sd_log_dump(const char *name, Stream &out);
