# Hardware baseline — the quad as it is today

**Source of truth for the hardware.** Last full review: 2026-10-25. CAN, battery and
electronics updated 2026-11-01 (CAN logger working).

Every value carries a tag: **MEASURED** (on this vehicle) · **VESC_ESTIMATE** (VESC
detection, not independent) · **CONFIG** (typed in by a human) · **ASSUMED** (guess,
must be replaced) · **MISSING**. Numbers that enter the model live in
`04_model/params/*.m`; this file says what the hardware *is*, and points there.

Detail and history: [motor-parameters](motor-parameters.md) ·
[open-questions](open-questions.md) · [vesc/](vesc/README.md) ·
[shopping-list](shopping-list.md).

---

## 1. Vehicle

Nitro Motors mini-quad, tubular steel chassis, originally 36 V / 800 W lead-acid.
Converted to Li-ion and a 48 V-class PMSM.

| Item | Value | Tag |
|---|---|---|
| Vehicle mass (no rider) | **38 kg** | MEASURED, scale, 2026-10-08 |
| Rider mass | 72 kg | MEASURED, scale, 2026-10-08 |
| Total | 110 kg | — |
| Wheelbase | 0.71 m | ASSUMED (commercial reference) |
| Static rear weight fraction | 0.65 | ASSUMED — needs a scale under each axle |
| CG height `h_cg` | — | **MISSING** — needed for load transfer |

Subjective: very good on dirt, drifts, rear wheels rarely spin (weight sits rearward).

## 2. Tyres and wheels

Front 13×4.10-6, rear 13×5.00-6 TR13, 6 in rims, pneumatic knobby, tubed.

| Item | Value | Tag |
|---|---|---|
| Nominal radius | 165.1 mm | MEASURED (tyre size) |
| Loaded rolling radius `r_roll` | 155 mm [150–160] | ASSUMED — **most leveraged unmeasured number** |

Measure `r_roll` by roll-out (rider seated, 10 revolutions, `r = D/(20π)`), never with a
ruler. Since 2026-11-01 the wheel sensor counts the revolutions: push the quad slowly,
rider on board, over a measured 10 m and count magnets (10 per turn). Procedure in `04_model/params/vehicle_params.m`. New tyres bought (reported
2026-10-20): measure once they are fitted — the old 155 mm guess does not carry over.

## 3. Transmission

25H chain, **11T / 92T → i = 8.364** (MEASURED: teeth counted, confirmed by Hall count).
Original 11/72; the change to 92T transformed launch and low-speed behaviour.
Efficiency 0.95 [0.90–0.97] ASSUMED — never measured.

## 4. Motor

Donor: Urban Fox scooter, sold as "48 V ~1900 W BLDC". The market reference
(MY1020/BM1109) is **ruled out** — its rated torque and current are inconsistent with
the measured Kt. Treat any datasheet number as belonging to another motor.

| Item | Value | Tag |
|---|---|---|
| Topology | Radial flux, **inner rotor**, outer wound stator, 3 phases | Observed by Pol |
| Pole pairs `p` | **3** | MEASURED (Hall count) |
| Flux linkage `λm` | **16.855 mWb** | MEASURED (3 methods, 0.02 %). VESC detections 2026-11-05 scatter 16.2–17 mWb around it |
| `Rs` per phase | **18.7 mΩ** | VESC_ESTIMATE (includes MOSFETs), 2026-11-05, repeated 3× at 40 A after rewriting the config. Replaces 28.02 mΩ (2026-09-07), which no longer reproduces |
| `Ld` / `Lq` | 99.2 / 112.8 µH, **Lq/Ld = 1.136** (2026-09-07, 40 A) · 97.8 / 113.0 µH, 1.155 (2026-11-05: L 105.39, Lq−Ld 15.19 µH) | VESC_ESTIMATE. Agree within the known current dependence |
| Rotor inertia | 1.558·10⁻⁴ kg·m² ±14 % | MEASURED |
| Back-EMF THD | 9.4 % (5th, 7th) | MEASURED |
| Kt | 0.0758 Nm/A | Derived |
| Magnet arrangement (surface / inset / interior) | — | **MISSING** — saliency says *not pure surface* |
| Stator slot count | — | **MISSING** |
| Temperature sensor | none fitted | MEASURED |

Lq > Ld with a current-dependent ratio means the rotor has *some* saliency; it does
not by itself prove interior magnets (see `02_knowledge/` for the reasoning). Settling
it needs a look inside or an Ld/Lq-vs-angle measurement.

## 5. Inverter — Flipsky FSESC 6.7 Mini Pro (VESC)

Product data: ~70 A continuous, 14–60 V, FOC, Hall support, CAN/USB/UART.

Operating configuration (CONFIG, full list in `motor_params.m` and `vesc/`):
FOC with Hall sensors, current control, PWM 30 kHz, current loop bandwidth 2000 rad/s,
no decoupling, MTPA off, field weakening off.

| Limit | Value |
|---|---|
| Motor current | ±120 A (abs 160 A) — Pol's choice, full power; stays for tests too |
| Battery current | **40 A** discharge / −35 A regen — equals BMS rating, do not raise |
| Duty | 0.95 |
| Battery cut-off | 44.2 → 39.0 V |

Firmware **7.01** (CONFIG, read in VESC Tool 2026-10-31).

**CAN:** mode = **VESC**, 500 kbit/s, controller ID **15**, status messages 1–6 at 50 Hz
(≈ 290 frames/s). Extended id = `(packet << 8) | 15`. Connector pins: `-` (GND), CAL,
CAH, 5V (5V unused). Termination on the VESC side **unclear**: with the logger's 120 Ω
fitted, CAN-H–CAN-L read 88 Ω, and the readings do not add up; the bus runs with
0 errors on a short cable, so it is left as is. **Any link VESC ↔ mains-referenced
equipment needs galvanic isolation** (EXP-001); the logger avoids it by floating on its
own 12 V battery ([DEC-004](../08_decisions/DEC-004-non-isolated-can-floating-logger.md)).

Observed in use: battery current peaks ~40 A, typical 20 A; at launch the motor-current
limit is reached, then duty becomes the limit as speed rises.

## 6. Battery and BMS

13S5P, 65 × SINC ISR18650-26A (no verified datasheet), ~13 Ah.
48.1 V nominal, 54.6 V full, 39.0 V empty.
Pack resistance **≈ 0.18 Ω, battery + wiring + BMS** — MEASURED 2026-10-31, CAN log
(50.9 V at rest → 45.8 V at 29 A; [EXP-002](../07_experiments/EXP-002-spi-noise-can-logger.md)).
Replaces the 0.10 Ω assumption. ~70 mΩ per cell equivalent: part of it is wiring.
Design assumption 5 A/cell = 25 A continuous; observed peaks ~40 A. **Risk 1** in
[open-questions](open-questions.md).

BMS: JK-BD4A17S4P, 40 A continuous, active balancing, Bluetooth only in use.
Pol reports a CAN output with a closed protocol (`syssi/esphome-jk-bms` documents JK
protocols); not connected. The VESC already reports pack voltage and current.
**Decided 2026-11-01 ([DEC-005](../08_decisions/DEC-005-vcu-architecture.md)):** the BMS stays a
passive backup, untouched, and no pack temperature sensor is fitted.

## 7. Driver inputs and sensors

Target wiring (DEC-005, 2026-11-01): throttle, brake switches, wheel speed and IMU go
to the vehicle control unit (the logger ESP32); the rotor Halls stay on the VESC.

- Throttle: 3-wire 5 V Hall, wired directly to VESC ADC. **Moves to the VCU.**
- Brake switches: original, on/off, disconnected. **Go to the VCU.** Measured 2026-11-02:
  **normally open** (continuity only while braking). The rear switch is faulty, so only
  the front brake is wired (GPIO 32); GPIO 33 stays reserved for the rear.
- Wheel speed: **fitted 2026-11-01** on the front wheel. One 3144 Hall on GPIO 34 of the
  logger ESP32, 10 neodymium magnets on a 160 mm diameter circle, ~5 mm gap. Spacing
  redone with a compass; residual ±8 % gap-to-gap error that repeats every turn, and a
  once-per-turn swing that suggests the magnet circle is not centred on the axle. The
  logger stores raw magnet times; speed needs `r_roll` (still ASSUMED, section 2).
- IMU: GY-LSM6DS3 (6-axis) **damaged 2026-11-01** while soldering (SDA pull-up torn off,
  then the chip stopped answering on I2C). Replacement on the shopping list.

## 8. Electronics and tools on hand

| Item | Status |
|---|---|
| ESP32-WROOM-32 (original) | **Destroyed** 2026-09-07 (ground loop, EXP-001) |
| ESP32 ×3 (new) | No. 2 runs the CAN logger (verified 2026-10-31); two spare |
| MCP2515 + TJA1050 CAN module | **In use** in the logger, 5 V, SO through a 1k/2k divider ([DEC-004](../08_decisions/DEC-004-non-isolated-can-floating-logger.md)) |
| microSD module (AMS1117) + 16 GB card | In use in the logger |
| 12 V battery + DC-DC to 5 V (5.3 V out) | Powers the logger, floating from the 13S pack |
| D4184 module, protoboard | Available. D4184 was listed as a DC/DC; the part number is a MOSFET switch module — check |
| Oscilloscope, multimeter, soldering | Available. Floating phase voltages need a differential probe |

**CAN logger working** (2026-11-01): [`05_firmware/arduino/can_logger/`](../05_firmware/arduino/can_logger/README.md).
What is still to buy: [shopping-list](shopping-list.md).

## 9. Still open

Magnet arrangement · slot count · `r_roll` · `h_cg` · axle weights · cell
current capability · drivetrain efficiency · control-loop period (15 vs 30 kHz) ·
BMS overcurrent settings · VESC-side CAN termination.

Superseded source: the August 2026 "master technical context" (in `_archive/`).
