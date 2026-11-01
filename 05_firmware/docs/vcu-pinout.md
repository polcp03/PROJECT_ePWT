# VCU pinout — ESP32-WROOM-32

**2026-11-01.** The vehicle control unit is the CAN logger board grown up: the same ESP32
records and, later, sends the torque request. Architecture and the reasons behind it:
[DEC-005](../../08_decisions/DEC-005-arquitectura-vcu.md). Current logger wiring:
[can_logger/README](../arduino/can_logger/README.md).

| Sheet | What it shows |
|---|---|
| [1 · Vehicle architecture](vehicle-architecture.svg) | Power path, mechanics, sensors, the two ground domains, CAN as the only link between them |
| [2 · VCU schematic](vcu-schematic.svg) | Every wire of the VCU, with reference designators (U, R, C, J, SW) used in the table below |

![Sheet 1](vehicle-architecture.svg)

![Sheet 2](vcu-schematic.svg)

Regenerate both: `python draw_sheets.py <out>` then `python build_sheets.py <out> <page.html> .`
(the page is the published artifact, https://claude.ai/artifact/FaUSu6HwdwUUkRSe6dvWig).

**Motor NTC** (bought 2026-11-01): 10 kΩ on the **VESC** Hall plug, pins TEMP and GND (check
the pin on the board), beta set in VESC Tool. It never touches the VCU.

## Every pin

| GPIO | Signal | Type | Device | Electrical condition | Status |
|---|---|---|---|---|---|
| 5V (VIN) | 5.3 V rail | power | DC-DC from the 12 V battery | Also feeds MCP2515, SD, wheel Hall, throttle. Never from the 13S pack | wired |
| GND | common ground | power | — | Joins the VESC ground **only** through the CAN cable | wired |
| 3V3 | 3.3 V out | power | ESP32 regulator | Pull-ups and the IMU only. **Never** pull an input up to 5 V | wired |
| 34 | wheel speed | digital in, interrupt on falling edge | 3144 Hall, front wheel | Open collector: external 10 kΩ to 3V3 (GPIO 34 has no internal pull-up) | wired |
| 35 | throttle | **analog** in, ADC1 ch 7, 11 dB | 5 V Hall grip | Divider 10 kΩ top / 12 kΩ bottom (× 0.545) + 100 nF pin → GND | planned |
| 32 | brake, left lever | digital in, active low | on/off switch | Switch to GND. External 10 kΩ to 3V3 + 100 nF → GND; debounce 10–20 ms in code | planned |
| 33 | brake, right lever | digital in, active low | on/off switch | Same as GPIO 32 | planned |
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

**Throttle on GPIO 35.** It has to be ADC1, because ADC2 is shared with the Wi-Fi radio.
The grip is powered from 5 V and its output goes above 3.3 V, which the ESP32 does not
tolerate, so it goes through a divider. 10 k / 12 k gives × 0.545:

| Throttle output | At the pin | What the code does |
|---|---|---|
| 0 V (wire cut) | 0 V | out of window → zero torque. The 12 k pulls the pin down, so a cut wire fails safe |
| ~0.8 V (rest) | ~0.44 V | zero demand |
| full (to be measured, ~4.2 V expected) | ~2.3 V | full demand, still in the ADC's linear range (≤ 2.45 V at 11 dB) |
| 5.3 V (shorted to supply) | 2.89 V | out of window → zero torque. Below the 3.6 V absolute maximum |

The fault window is set **after** measuring the real rest and full voltages with the
multimeter. The 100 nF with the 12 k makes a ~1 ms filter: enough against noise, invisible
to the driver.

**Brakes on GPIO 32 and 33.** Digital inputs with an internal pull-up as backup. The
internal one (~45 kΩ) is too weak for a long wire running next to the VESC, so an
external 10 kΩ sets the level and the 100 nF filters spikes. One pin per lever, so the
log tells which brake was used.

**IMU on GPIO 21 / 22.** The ESP32's default I2C pins: no remapping in code.

## Before connecting anything new

1. **Throttle:** measure its output at rest and at full throttle. Unplug it from the VESC
   ADC connector completely: if it stays tied to both, there are two ground paths.
2. **Brakes:** with the multimeter on continuity, check that each switch is a dry contact
   (no voltage from the original 36 V system) and whether it is normally open or closed.
   Normally open is assumed above. Then a cut wire reads "not braking" and the
   brake + throttle check is lost without any sign; a normally closed switch would fail safe.
3. **VESC:** set the CAN timeout and test it with the wheel in the air **before** the
   throttle stops going to the VESC.
4. **5 V budget:** the DC-DC's rating is not recorded. Check it covers the ESP32 with
   Wi-Fi (~250 mA peaks) plus the modules before adding loads.

Unknowns: the throttle's full-scale voltage, the brake switch contact type, the DC-DC
current rating, whether the new IMU module carries its own pull-ups.
