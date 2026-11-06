# Open questions and hardware risks

What is **not** verified. Every line is a candidate experiment.
Taken from the critical review of 2026-08-21.

## Risk 1 — Battery current margin (the most serious)

Battery peaks of **~40 A** observed against a design assumption of 25 A (5 cells × 5 A).
An overshoot of ~1.6×, about 8 A per cell at peak.

- The SINC ISR18650-26A cells **have no verified datasheet**. Generic or rewrapped cells often
  have inflated current ratings.
- The BMS (JK-BD4A17S4P) has a 40 A continuous limit → at the peaks the BMS limit is also being
  touched, not only the cells'.
- Today the BMS is a passive backstop, visible only over Bluetooth. An overcurrent event would
  be discovered by the sudden cut, not by a prior warning.

**Mitigation while there is no measurement:** the primary limiter is the current limit set in
the VESC itself, with margin below the real capacity of the pack and the BMS rating.
~~Instrument the pack temperature directly~~ — **dropped by Pol on 2026-11-01**
([DEC-005](../08_decisions/DEC-005-vcu-architecture.md)): the BMS protection is accepted.
Accepted risk: in a 5P group the outer cells get hotter than the BMS probes see. The manual
check at the end of every test remains.

**Pending experiment:** voltage drop under load, to estimate the pack's real current capacity.

## Risk 2 — PC / VESC ground loop — **HAPPENED 2026-09-07**

> [!danger] No longer a theoretical risk
> On 2026-09-07 this mechanism destroyed an ESP32-WROOM-32 while fitting the first CAN sniffer.
> The warning below was written **before** the incident and was not read before fitting.
> Quantification pending in [`EXP-001`](../07_experiments/EXP-001-ground-loop-vesc-pc.md).

### The original symptom: VESC USB drops under load

Catalogued as "possible EMI" but never checked. It is a **known, documented failure in the VESC
community**, with no single cause. Three candidate mechanisms, not exclusive:

1. USB termination resistors — the STM32F405 datasheet does not specify the pull-ups well;
   some VESC 6 board revisions changed them.
2. EMI coupling from phase switching into the USB data lines. Hard to fix when USB and power
   are on separate boards (this case).
3. Ground loops between the PC ground and the VESC's (referenced to the battery) as soon as
   current flows. It can kill a regulator.

Since the symptom is "under load, and the motor keeps running", EMI or a ground loop are more
likely than a soldering defect.

**Cheap pending experiment (~30 min):** oscilloscope on D+/D− and on the 5 V rail during a load
ramp. Try an isolated USB hub or a ferrite as a bisection.

### What the 07-Sep incident adds

Mechanism 3 (ground loop) is also the main candidate for the ESP32's death. Setup: CAN module
powered from the ESP32's 3V3 pin, CAN side connected to a VESC switched on with the 13S
battery. That puts the micro's 3.3 V rail in electrical contact with a switching 54 V system,
with nothing in between.

**Design consequence:** any connection between the VESC and mains-referenced equipment needs
galvanic isolation. ISO1050 for CAN, ADUM3160 for USB. See `shopping-list.md`.

> [!note] 2026-10-31: the logger avoids it without isolation
> The CAN logger runs from its own 12 V battery: there is no mains equipment in the loop, so
> the ISO1050 is not needed ([DEC-004](../08_decisions/DEC-004-non-isolated-can-floating-logger.md)).
> Laptop over USB only without its charger. And the logger records under load without depending
> on the VESC's USB, so the USB drop no longer blocks the data.

## Risk 3 — The motor is not identified with certainty

The MY1020/BM1109 reference is not confirmed. Characterising it (phase R, back-EMF, pole pairs)
is cheap and needs no software. → That is the goal of **C01**.

**Rotor construction unknown (2026-11-05).** Lq/Ld ≈ 1.10 says "not a pure surface-magnet
rotor", not "interior magnets": inset magnets or iron saturation give the same. Only opening
the motor answers it. **Open it and photograph the rotor** (magnet layout, flux barriers,
slots) before the id–iq map or MTPA work in the backlog. Pol is wary of reassembly: plan it
(mark the end-bell position, photograph every step, keep the Hall board wiring as it is) and
spin-test after closing.

> [!success] Answered 2026-11-06: opened by Pol
> **Inset surface magnets**: 6 poles on the rotor surface with lamination steel between them,
> 9 slots, star winding. The iron between magnets explains Lq > Ld. Details in
> [motor-parameters](motor-parameters.md#motor-opened--2026-11-06-pol-by-eye-and-ruler-photos-on-his-phone).
> New open point: light rub marks on some magnets (assembly or running?).

**Same opening: inspect the Hall sensors (2026-11-05).** Their placement error (~±10°, 19°
spread, repeatable) causes the current ripple below the Hall→observer handover
([EXP-003](../07_experiments/EXP-003-low-speed-control.md)). Look for a moved, bent, loose or
dirty sensor; photograph their position against the slots; clean. Replace one only if it is
visibly damaged, then re-detect the table and repeat `hall_analyze 20`. Steps in
`01_plan/tasks/tasks.md`.

## Reference implementations to review before programming anything

- **VESC Express** — official firmware from the VESC developers for the ESP32. It does
  practically the same as the planned V1 logger. Review before writing code.
- VESC Tool's FOC detection wizard already estimates R, L and magnetic flux (typical ranges
  ~15–35 mΩ and 4–20 µH for this kind of motor). Useful as an independent check of the manual
  measurement.
- `syssi/esphome-jk-bms` — the JK-BMS protocol over UART/BLE, already reverse-engineered and
  maintained.

## Risk 4 — No temperature sensor in the motor

`m_motor_temp_sens_type = 8` = `TEMP_SENSOR_DISABLED`. That is correct: **no sensor is
installed**. But the consequence is an open risk: the configured motor limits of 85/100 °C are
dead code, and 120 A of motor current are available on a winding already known to heat up.

Today the machine's thermal protection is **the procedure, not the system**: a current limit in
the VESC and a manual check at the end of the test.

- Without a sensor the thermal model and the `R(T)` compensation cannot be validated
  (`foc_temp_comp = 0`, consistent).
- The `R` estimated by the VESC belongs to the temperature of the detection run. Without a
  temperature measurement nobody knows which temperature.

**Cheap:** the VESC already supports NTC 10k / KTY / PT1000 on the temperature port. An NTC
taped to the case does not give the winding temperature, but it gives the trend and re-enables
the fold-back. It is the only sensor gap for validating the model
([DEC-005](../08_decisions/DEC-005-vcu-architecture.md)): **it is being bought** (Pol, 2026-11-01).

## VESC configuration audit — 2026-09-06

Full review of `MOTOR_1.9.xml` + `MOTOR_1.9_app.xml` against the firmware.

**Internal consistency: correct.** `kp = L·bw` and `ki = R·bw` give the same `bw = 2000 rad/s`
with both numbers, and `observer_gain = 1e3/λ²` = 3.898e6 ≈ 3.9e6 configured. The detection was
applied properly.

**Deviations found:**

| Field | Value | Should be | Impact |
|---|---|---|---|
| `si_gear_ratio` | ~~6.5~~ → **8.363** | 8.36 (92/11) | ✅ Settled. The 09-Sep export already said 8.363: the 6.5 note was old |
| `si_motor_poles` | ~~14~~ → **6** | 6 (p = 3 MEASURED) | ✅ Corrected in the VESC and re-exported on 01-Oct. It **does** enter the reported speed |
| `si_wheel_diameter` | 0.30 m | 2·r_roll ≈ 0.31 m | ⚠️ ~3 %. Decide which is right when the roll-out is measured |
| `si_battery_ah` | 13 | unverified | Only the range estimate |
| `foc_encoder_ratio` | 7 | — | Irrelevant, there is no encoder |

> [!success] Updated 2026-10-09
> What follows described the state before correcting. Today the speed channel only carries the
> ~3 % of the wheel diameter.

`si_gear_ratio` does not affect control, but it **does corrupt the speed channel of every log**.
Since rule no. 3 of `04_model/CLAUDE.md` says the model is worth nothing until it correlates
against `06_data/`, it is a cheap blocker: one field.

**Command chain confirmed** (to model the driver input):
`app_to_use = 2` (ADC), `ctrl_type = 3` (current, with reverse by button), linear map
0.81 → 3.30 V, and a **ramp of 0.3 s up / 0.1 s down**. That ramp (400 A/s) dominates the
perceived dynamics over the current loop (~1.5 ms). Detail in
[`04_model/params/throttle_params.m`](../04_model/params/throttle_params.m).

## Answered on the bench — the VESC controlled badly below ~2500 erpm (2026-11-05)

Full record: [EXP-003](../07_experiments/EXP-003-low-speed-control.md). Two causes, found the
same evening with the wheels in the air:
1. **Hard start = over-tensioned chain.** Chain off: breakaway ~7 A → ~2.5 A, turns at 2 % duty.
2. **Current ripple below ~4000 erpm = Hall angle** (sensor placement, ~±10°). Moving the
   Hall→observer handover from 2500/4000 to **1000/2000 erpm** cut the id ripple at
   2000–3400 erpm from ~2 A to ~0.15 A.

**Still open:** the observer at 1000–2000 erpm **under load** (chain back on, at a tension
spec), and the observer's flux linkage (detections scatter 16.2–17 mWb against 16.86 mWb
measured), which matters most at low speed.

**Export of 23:41 checked:** handover 1000/2000 ✓, `si_motor_poles` 6 ✓, battery current
39 / −25 A ✓. Motor current ±120 A is Pol's choice (full power), not a discrepancy.

## Confirmed hardware gotcha

The TJA1050 is 5 V logic. Many cheap MCP2515/TJA1050 modules power the whole module at 5 V,
out of spec for the ESP32's 3.3 V GPIOs. **Check the module's real logic level with a
multimeter before wiring it directly.**
