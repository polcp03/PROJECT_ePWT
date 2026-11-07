# DEC-005: Vehicle control unit (VCU) architecture and sensors

**Date:** 2026-11-01. Pol decides, after discussing it with Claude. It makes concrete the target
architecture of the kickoff (C00, slide 5) and step 3 of the [roadmap](../01_plan/roadmap.md).

## Decision

| Signal | Goes to | Why |
|---|---|---|
| **Throttle** | **VCU** (today, the VESC's ADC) | It is the base of traction control: the VCU decides the torque and requests it over CAN |
| **Brake switches** | **VCU** (today, not connected) | Safety (brake + throttle = zero torque), knowing when the speed reference is not valid, and labelling the data |
| **Front wheel speed** | VCU | Already fitted (2026-11-01). Undriven wheel = the vehicle's speed reference |
| **IMU** | VCU | When the new one arrives. Longitudinal acceleration, slope and yaw |
| **Rotor Halls** | **VESC, unchanged** | Commutation needs microseconds; the VCU already gets the rpm over CAN |
| **BMS** | **Nothing.** Passive backup | Closed protocol; pack voltage and current already come from the VESC |
| **Pack temperature** | **No sensor** | The BMS has two probes of its own and cuts if it goes over |

The focus is **VCU + VESC**. The BMS is not touched.

## Alternatives rejected

- **Rotor Halls to the VCU too.** It duplicates what the VESC already sends (erpm).
- **BMS over CAN or UART** (`syssi/esphome-jk-bms`). It would give per-group voltage,
  temperature and a warning before the cut. Rejected on cost/benefit: closed protocol, and the
  focus is motor and inverter. Stays in the backlog.
- **Temperature probe on the outer cells** (what `open-questions.md` asked for). Rejected by
  Pol: the BMS protection is accepted.

## Check: are the sensors enough to validate the model?

Goal of the year: a model validated against the real vehicle (C04 motor, C05 vehicle).

| What has to be validated | Signal | From | Status |
|---|---|---|---|
| Motor (C04): λm, R, current loop | current, erpm, duty cycle, voltage | VESC over CAN | ✅ already recorded |
| Resistance with temperature, `R(T)` | motor temperature | — | ⚠️ **gap**. See below |
| Coast-down (C05): rolling, aero, efficiency | vehicle speed against time | Front wheel Hall | ✅ sensor; missing **`r_roll`** (roll-out) and **SD card** |
| Acceleration (C05): force at the wheel | current + speed + acceleration | VESC + wheel + IMU | ✅ when the IMU arrives |
| Ground slope | pitch | IMU, or measured flat ground | ✅ with the IMU |
| Slip (traction control) | rear vs front wheel | erpm ÷ 3 ÷ 8.364 against the Hall | ✅ |
| Corners | yaw rate | IMU | ✅ with the IMU. Solid rear axle and a single front sensor: in a corner the reference needs the yaw rate |
| Load transfer | `h_cg`, weight per axle | scales, not a sensor | ❌ measurement pending |
| Driver input | throttle, brake | VCU | ✅ with this decision |

**Conclusion:** with what there is, plus the IMU and the brake, everything for 2026 can be
validated. **No more sensors need buying.** What blocks is not sensors: it is the SD card, the
IMU, the 10 m roll-out and the per-axle scales.

**Only gap: the motor temperature.** Copper resistance rises ~0.4 %/K: with 40 K of heating,
`Rs` rises ~16 %. At 120 A that is half a volt more drop, which matters exactly where the duty
cycle is already at the limit. Also, without a sensor, the VESC's 85/100 °C limits are dead
code (Risk 4 in `open-questions.md`). A 10k NTC taped to the case, on the **VESC's** temperature
port (not the VCU's): ~€1.
**Decided by Pol the same day: it is bought** (`shopping-list.md`).

## Consequences

What has to be done **before** the throttle goes through the ESP32 (drive-by-wire):

1. **VESC:** remove the ADC app and configure the **CAN timeout**. If the VCU hangs or goes
   quiet, the VESC has to cut torque by itself. Test it with the wheel in the air.
2. **Throttle:** powered from the VCU's 5 V. Its output goes above 3.3 V and the ESP32's ADC
   does not: **divider**. Use an ADC1 pin (GPIO 32–39), because ADC2 does not work with Wi-Fi
   on. A fault window like the VESC's: out of range → zero torque.
3. **Brake:** each switch, one pin to ground with the internal pull-up. GPIO 32 and 33 have
   one; **34–39 don't**. Before that, check with the multimeter that it is a dry contact (it
   carries no voltage from the original system) and whether it is normally open or closed.
   Debounce in code.
4. **Brake + throttle → zero torque**, in the code from v0.
5. **Ground loop:** the VCU still floats on its 12 V battery ([DEC-004](DEC-004-non-isolated-can-floating-logger.md)).
   With the VCU commanding torque, EXP-001 matters again.

Full pinout, with each pin's conditions: [`05_firmware/vcu-design/vcu-pinout.md`](../05_firmware/vcu-design/vcu-pinout.md).
Throttle GPIO 35, brakes GPIO 32 and 33, IMU GPIO 21/22.

## Assumptions

- The VCU is the evolution of the logger: the same ESP32 records and commands.
- The BMS cuts before the pack becomes dangerous. **Accepted risk:** a BMS cut is a sudden loss
  of power with no warning, and in a 5P group the outer cells get hotter than its probes see.
  The safety rule in `CLAUDE.md` stays: check the pack temperature by hand at the end of every
  high-current test.
- The original brake switches work as they are.

## To find out

- Which wheels does each lever brake? It changes what the front reference means when braking.
- Open question for Pol: if you brake hard and the front wheel locks, what happens to the speed
  reference, and what would traction control do with it?
