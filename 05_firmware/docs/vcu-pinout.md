# VCU pinout — ESP32-WROOM-32

**2026-11-01.** The vehicle control unit is the CAN logger board grown up: the same ESP32
records and, later, sends the torque request. Architecture and the reasons behind it:
[DEC-005](../../08_decisions/DEC-005-arquitectura-vcu.md). Current logger wiring:
[can_logger/README](../arduino/can_logger/README.md).

| Sheet | What it shows |
|---|---|
| [1 · Vehicle architecture](vehicle-architecture.svg) | Power path, mechanics, sensors, the two ground domains, CAN as the only link between them |
| [2 · VCU schematic](vcu-schematic.svg) | Every wire of the VCU, with reference designators (U, R, C, J, SW) used in the table below |
| [3 · Perfboard layout](perfboard-layout.html) | The same VCU hole by hole, interactive: where each part, wire and terminal goes, build order and parts list |

![Sheet 1](vehicle-architecture.svg)

![Sheet 2](vcu-schematic.svg)

Regenerate both: `python draw_sheets.py <out>` then `python build_sheets.py <out> <page.html> .`
(the page is the published artifact, https://claude.ai/artifact/FaUSu6HwdwUUkRSe6dvWig).
Sheet 3 is hand-made HTML, published in the **same artifact** as `perfboard.html` (copy
`perfboard-layout.html` next to the page and pass it in `files`). One artifact for all VCU
drawings: the old separate "Placa perforada" artifact was deleted on 2026-11-05.

**Motor NTC** (bought 2026-11-01): 10 kΩ on the **VESC** Hall plug, pins TEMP and GND (check
the pin on the board), beta set in VESC Tool. It never touches the VCU.

## Every pin

| GPIO | Signal | Type | Device | Electrical condition | Status |
|---|---|---|---|---|---|
| 5V (VIN) | 5.3 V rail | power | DC-DC from the 12 V battery | Also feeds MCP2515, SD, wheel Hall. Never from the 13S pack | wired |
| GND | common ground | power | — | Joins the VESC ground **only** through the CAN cable | wired |
| 3V3 | 3.3 V out | power | ESP32 regulator | Pull-ups, the IMU and the throttle grip. **Never** pull an input up to 5 V | wired |
| 34 | wheel speed | digital in, interrupt on falling edge | 3144 Hall, front wheel | Open collector: external 10 kΩ to 3V3 (GPIO 34 has no internal pull-up) | wired |
| 35 | throttle | **analog** in, ADC1 ch 7, 11 dB | Hall grip **on 3V3** | No divider. RC: 1 kΩ series + 100 nF → GND (1.6 kHz). 100 kΩ pull-down | bench (breadboard, no RC yet) |
| 32 | brake, front | digital in, active low | on/off switch, normally open | Switch to GND. External 10 kΩ to 3V3 + 100 nF → GND; debounce 10–20 ms in code | planned |
| 33 | brake, rear | digital in, active low | on/off switch | Same as GPIO 32. **Not wired:** the rear switch is faulty (2026-11-02). Pin and holes stay reserved | reserved |
| 21 | IMU SDA | I2C | GY-LSM6DS3, 0x6A | 10 kΩ to 3V3 (check first whether the module already has them) | planned |
| 22 | IMU SCL | I2C | GY-LSM6DS3 | Same | planned |
| 14 / 13 / 27 / 26 | CAN SCK / SI / SO / CS | SPI (HSPI), 4 MHz | MCP2515 + TJA1050 | SO swings 0–5 V: 1 kΩ / 2 kΩ divider into GPIO 27 | wired |
| 18 / 19 / 23 / 5 | SD SCK / MISO / MOSI / CS | SPI (VSPI) | microSD module | GPIO 5 is a boot strap pin; fine because CS idles high | wired, card dead |
| 0 | BOOT button | digital in | on the board | Start / stop a recording | wired |
| 2 | LED | digital out | on the board | Idle / recording / error | wired |

**Free:** 36 and 39 (input only, ADC1: the next analog signals, e.g. the 12 V battery
voltage through a divider) · 4, 16, 17, 25 (general digital I/O).
**Never:** 6–11 (internal flash) · 1 and 3 (USB serial) · 12 (strap: a pull-up there stops
the boot) · any ADC2 pin (0, 2, 4, 12–15, 25–27) for analog: ADC2 reads nothing with Wi-Fi on.

## Why each new pin is where it is

**Throttle on GPIO 35 (changed 2026-11-05).** It has to be ADC1, because ADC2 is shared with
the Wi-Fi radio. The grip is now **powered from 3V3, not 5 V**, so its output stays below what
the ESP32 tolerates and **no divider is needed**. Measured: 0.80 V at rest, 2.60 V at full,
linear. The rest point does not scale with the supply, only the top does.

- **R4 1 kΩ in series + C2 100 nF to GND, at the pin:** RC filter, cut-off
  1 / (2π · 1 kΩ · 100 nF) ≈ 1.6 kHz. It cuts the inverter's 30 kHz PWM ~19× before the ADC.
  A software average alone cannot do that: slow sampling aliases 30 kHz into a fake slow
  signal (error #18). 0.1 ms of delay, nothing against the 20 ms budget of REQ-VCU-01.
- **R5 100 kΩ pull-down:** a cut signal wire reads 0 V instead of floating. High enough not to
  load the grip. **Check when fitting it:** rest and full readings move less than 10 mV.

| Fault | At the pin | What the code does |
|---|---|---|
| Signal wire cut | 0 V (R5) | below 600 mV → zero torque, latched |
| Rest | 0.80 V | zero demand (≤ 900 mV) |
| Full | 2.60 V | full demand (≥ 2550 mV) |
| Grip GND cut, or signal shorted to 3V3 | ~3.1–3.3 V (expected, not tested) | above 2800 mV → zero torque, latched. Below the 3.6 V absolute maximum |

Window and map from the [can_throttle](../arduino/can_throttle/README.md) contract. The
2.60 V full point is just above the ADC's ~2.45 V linear range at 11 dB; it is calibrated,
so it reads right, but the top 5 % is where the ADC is least accurate.

**Brakes on GPIO 32 and 33.** Digital inputs with an internal pull-up as backup. The
internal one (~45 kΩ) is too weak for a long wire running next to the VESC, so an
external 10 kΩ sets the level and the 100 nF filters spikes. One pin per brake, so the
log tells which brake was used. Only the front one is wired for now: the rear switch
does not work reliably. A rear wheel lock still shows in the log, because the rear wheel
is the motor and its speed comes from the VESC erpm.

**IMU on GPIO 21 / 22.** The ESP32's default I2C pins: no remapping in code.

## Before connecting anything new

1. **Throttle:** done 2026-11-05 (0.80 / 2.60 V on 3V3). It stays unplugged from the VESC
   ADC connector: tied to both, there are two ground paths.
2. **Brakes:** measured 2026-11-02 with the multimeter on continuity. The switches are
   **normally open**: no continuity at rest, continuity while braking (the cable holds the
   microswitch pressed at rest and releases it when the lever is pulled). So a cut wire
   reads "not braking" and the brake + throttle check is lost without any sign. Known
   limitation, accepted for v0; a normally closed contact would fail safe. Still to check:
   no voltage left on the switch wires from the original 36 V system.
3. **VESC:** CAN timeout set to 100 ms and tested with the wheel in the air, 2026-11-05:
   105–121 ms over 5 runs (REQ-VCU-03 verified).
4. **5 V budget:** the DC-DC's rating is not recorded. Check it covers the ESP32 with
   Wi-Fi (~250 mA peaks) plus the modules before adding loads.

**Throttle, measured 2026-11-05** (multimeter, then ESP32 `analogReadMilliVolts`, sketch
`arduino/throttle_cal/`): at 5.3 V supply 0.8 V rest → 4.5 V full, linear. At 3.3 V supply
0.80 V rest (ESP32: 804 mV) → 2.60 V full: the rest point does not scale with the supply,
only the top does, so calibrate with the supply it will run on. Bench noise of the 32-sample
average, at rest, inverter off: ~7 mV p-p (0.4 % of the 1796 mV span). With the motor spinning
at 5 A (no RC yet): spikes up to +80 mV (4.5 % of throttle). The 10 k / 10 k divider tried
first on 5 V gave impossible readings (2.7 V at rest), cause not found; dropped, because 3V3
needs no divider.

Unknowns: the DC-DC
current rating, whether the new IMU module carries its own pull-ups.
