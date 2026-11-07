# EXP-002: Noise when accelerating in the CAN logger

**Status:** closed on 2026-11-01. Confirmed and fixed.

## Question

The logger's recordings (`05_firmware/arduino/can_logger/`) cut out after 3–10 s, sooner with
throttle than without. Why, and where does the problem get in?

## Hypotheses

**H1 (Pol).** Interference: the problem appears when accelerating, when the VESC switches
current.

**H2.** If the noise gets in through the CAN bus, the MCP2515 will count bus errors (REC/TEC).
If it gets in through the SPI link between the MCP2515 and the ESP32, the bus will be clean and
the frames will arrive corrupt anyway.

## Method

1. Record in `boot.txt` the reason for every ESP32 reset.
2. Three tests, from least to most noise: **A** the ESP32 alone, **B** the VESC on and the
   motor stopped, **C** with throttle (wheels in the air, current limit set).
3. Classify every frame: good (VESC status ID, DLC 8), ghost (impossible ID) or with flipped
   bits (right ID, physically impossible value).

## Data

Raw files in `06_data/2026-10-31_can_logger_bench/raw/`; decoder
`04_model/scripts/can_log_decode.py`.

| Test | Duration | Good frames/s | Corrupt | Overflows | Bus errors |
|---|---|---|---|---|---|
| Before the fix | 3–10 s | — | PANIC / watchdog resets | — | — |
| A (log_012) | 138 s | — (no VESC) | 0 | 0 | 0 |
| B (log_013) | 144 s | 282 | 39 of 40,659 | 0 | 0 |
| C (log_014) | 70 s | 249 | ~3,150 (152 of 192 with flipped bits, during current) | 14 | 0 |
| **After (log_017)** | 137 s, 12 s with current | **288** | **1** (when switching the VESC on) | **0** | **0** |

In C, 458 V, −3249 °C and 10⁹ erpm appeared inside frames with the right ID.

## Conclusion

- **H1 confirmed:** the noise appears with current.
- **H2: it gets in through SPI, not CAN.** Bus errors are 0 in every test.
- **The resets were a firmware fault uncovered by the noise.** A flipped bit gave a length
  (DLC) of 9–15; the `mcp_can` library copied that many bytes into an 8-byte buffer,
  overwrote memory and the ESP32 crashed (PANIC). Fix: our own reader that never copies more
  than 8 bytes, with SPI lowered from 10 to 4 MHz.
- **The hardware removed the noise:** 5 V straight from the DC-DC to the rail (before, 4.5 V on
  the 5V pin through the USB cable and the board's diode, below the TJA1050's 4.75 V minimum),
  shorter SPI wires and the assembly away from the VESC. The three changes were made at once,
  so **it is not known which mattered most**.
- The double read (each frame is read until two reads agree) counted 0 disagreements in
  log_017: it had nothing to correct. It stays as a safety net and as a meter (`spi_errors` in
  every `#stat` line).

## Bonus data

Voltage drop in log_017: 50.9 V at rest → 45.8 V at 29 A ⇒
**R ≈ 0.18 Ω, battery + cables + BMS** (previously ASSUMED 0.10 Ω). At 29 A that is about
150 W of heat. Per cell (13S5P) it comes to ~70 mΩ, above a healthy 18650 (20–50 mΩ): part of it
is in the wiring. Pol's calculation.

## Limitations

- Test with the wheels in the air; under real load the current and the noise will be larger.
- The three hardware changes were not separated.
- The termination on the VESC side is unclear: the resistance measurements between CAN-H and
  CAN-L don't agree with each other. The bus works with 0 errors with the short cable.
