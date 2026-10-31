# can_logger — every CAN frame on the bus, to a microSD

ESP32 + MCP2515/TJA1050 + microSD. Records the VESC's raw CAN traffic while the quad
runs, with no PC attached. Decoding happens later on the PC, so adding a node (BMS,
a second ESP32) never changes the firmware.

**Status (2026-11-01):** works under throttle. 137 s recording, 33 783 frames,
peaks of 49 A motor / 29 A battery: 0 corrupted frames, 0 SPI errors, 0 overflows,
0 bus errors. How it got there: [EXP-002](../../../07_experiments/EXP-002-ruido-spi-can-logger.md).

## Modules

| File | One job |
|---|---|
| `can_frame.h` | The only shared types: `CanFrame`, `CanStats` |
| `can_rx` | Reads the MCP2515 into a RAM queue. Own task on core 0, busy-polling |
| `sd_log` | Writes frames to `log_NNN.csv`; `boot.txt` keeps every reset reason |
| `control` | BOOT button and LED |
| `can_logger.ino` | State machine (Idle / Recording / Error). Knows nothing about SPI or files |

`can_rx` talks to the MCP2515 directly instead of through `mcp_can` (used only to
configure the chip at boot): it reads each receive buffer until two reads agree and
never trusts the DLC for a copy. A corrupted DLC used to crash the ESP32.

## Wiring

| From | To | Note |
|---|---|---|
| 12 V battery → DC-DC | 5 V rail | Separate from the 13S pack: the logger floats |
| 5 V rail | ESP32 `5V`, MCP2515 `VCC`, SD `VCC` | Straight from the DC-DC, not through USB. TJA1050 needs ≥ 4.75 V |
| MCP2515 `SCK` `SI` `CS` | GPIO 14, 13, 26 | HSPI, 4 MHz |
| MCP2515 `SO` | 1 kΩ → GPIO 27, 2 kΩ GPIO 27 → GND | SO swings 0–5 V; the divider gives 3.3 V |
| SD `SCK` `MISO` `MOSI` `CS` | GPIO 18, 19, 23, 5 | VSPI. Module has its own 3.3 V regulator |
| MCP2515 `L` `H` `GND` | VESC CAN: `CAL`, `CAH`, `-` | VESC `5V` pin unused. J1 = 120 Ω on the MCP2515 side |

Keep the SPI wires short and the logger away from the VESC and the phase wires:
that, not firmware, removed the noise.

VESC: CAN mode VESC, 500 kbit/s, ID 15, status messages 1–6 at 50 Hz (≈ 290 frames/s).

## Use

- **BOOT** starts a recording; press again to stop. One file per recording.
- **LED:** short blink every 2 s = idle · steady = recording · fast blink = error (no SD).
- **Serial, 921600:** `start`, `stop`, `ls`, `cat log_017.csv`. A status line per second.
- **Live view:** `monitor.ps1` (Windows). Waits for COM4, highlights SPI errors.
  Laptop **on battery** while connected to the vehicle.

## File format

```
#boot,18,POWERON                         why the ESP32 last restarted
t_us,id,ext,dlc,d0,...,d7                id and data in hex
#stat,t_us,frames,queue_drops,hw_overflows,rx_err,tx_err,spi_errors   once per second
```

Decode: `04_model/scripts/can_log_decode.py <out_dir> log_017.csv`.

**Download:** use a microSD card reader. `cat` over USB works but corrupts a few lines
in large files at 921600 baud; if forced to, download three times and keep the lines
present in at least two.
