// sd_log - owns the microSD. One CSV file per recording: /log_001.csv, /log_002.csv...
// Stores raw frames; decoding happens on the PC, so a new CAN node never changes this module.
//
// File format:
//   t_us,id,ext,dlc,d0,d1,d2,d3,d4,d5,d6,d7      t_us since recording start, id and data in hex
//   #stat,t_us,frames,queue_drops,hw_overflows,rx_err,tx_err   once per second
// pandas: read_csv(path, comment='#') skips the #stat lines.
#pragma once
#include <Stream.h>
#include "can_frame.h"

bool sd_log_begin();                    // false if no card or not FAT32
bool sd_log_open();                     // opens the next free log_NNN.csv
bool sd_log_frame(const CanFrame &f);   // false if the write failed (card removed, full)
void sd_log_stats(const CanStats &s, int64_t t_us);
void sd_log_flush();                    // what has been flushed survives a power cut
void sd_log_close();
const char *sd_log_name();

void sd_log_list(Stream &out);
void sd_log_dump(const char *name, Stream &out);
