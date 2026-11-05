# EXP-003 — Why the VESC controls badly below ~2500 erpm

**Status: answered on the bench, 2026-11-05** (chain = hard start; Hall angle = low-speed ripple). Open: behaviour under load. Started 2026-11-05, wheels in the air. Symptom found during the CAN
bring-up ([can_throttle](../05_firmware/arduino/can_throttle/README.md)).

## Question

Why does the motor current go wild at low speed, when above ~2500 erpm the VESC follows the
request within 0.5 A?

## Symptom

- Current mode (over CAN): for a steady 5.7 A request between 0 and 2500 erpm the current
  the VESC reports swings **5–18 A**, and sometimes goes **negative** with the motor stopped.
  It needs **~7 A** to break away.
- Duty mode (VESC Tool): 10–30 % the motor "tries" and does not turn; 50 % turns.
- Released, the wheel slows down hard: ~13 000 erpm/s.
- Above ~2500–3000 erpm it is clean.

## Why 2500 erpm is the suspicious number

`foc_sensor_mode = 2`: FOC with **Hall sensors** at low speed. Between `foc_sl_erpm_start` =
2500 and `foc_sl_erpm` = 4000 the VESC hands over to the **sensorless observer**, which reads
the rotor angle from the back-EMF (E = λω). The bad zone ends exactly where the Halls stop
being used. So two suspects: the angle from the Halls, or something mechanical that only
hurts at low speed.

## Hypotheses (cheapest first)

1. **Halls:** bad table, a dead or noisy Hall, wrong wiring. (Pol)
2. **Chain friction / stick-slip:** the chain was tensioned very tight "so there is no lag".
   At low speed the VESC assumes the rotor turns at constant speed between two Hall edges.
   If the rotor sticks and jumps, that guess is wrong and the current goes wild. (Pol)

## What was measured

| Test | Result | Reading |
|---|---|---|
| Hall supply, multimeter | 5 V | ok |
| H1, H2, H3 switch, multimeter, turning by hand | all three switch | no dead Hall |
| Hall table, old (detected with chain) | 61, 129, 93, 193, 30, 161 | gaps 56, 58, 65, 58, 58, 67°: fine |
| Hall table, re-detected **without chain** | 63, 132, 97, 197, 32, 164 | gaps 56, 61, 63, 58, 59, 63°: fine |
| `hall_analyze 10`, **with chain** | edges 85, 47, 65, 62, 56, 75° | changes with current → the chain distorts it |
| `hall_analyze 20`, **with chain** | 66, 51, 73, 55, 62, 48° | |
| `hall_analyze 10`, **without chain** | 57, 53, 69, 59, 61, 54° (spread 16) | repeatable within ±2° |
| `hall_analyze 20`, **without chain**, ×3 | 58, 51, 70, 59, 61, 55° (spread 19), same after re-detection | the real placement of the sensors |

**How to read the Hall table.** The VESC stores each state's angle on a scale where
**200 = 360°** (`foc_math.c`: `ang_hall_int / 200.0 * 2π`); 255 = invalid state (0 and 7).
Six valid states, ideally 60° apart.

**How to read `hall_analyze`.** It turns the field open loop (no sensors) through 720° and
logs where each Hall edge falls. It prints the six gaps and the spread (max − min). The VESC
calls < 10 good, < 15 usable, above that "significantly misaligned".

## Conclusions so far

- **The Halls work and the table is right.** All three switch, both tables are ~60° apart.
- **Hall placement error: 19° spread, real and repeatable** (edges within about ±10° of where
  they should be). Above the VESC's 15° "usable" line. Physically a 10° angle error costs
  only ~1.5 % of torque (cos 10°), so on its own **it does not explain** 5→18 A swings.
  Probably factory placement. No evidence of rotor damage from the chain: damage would show
  as friction or noise, not as a fixed offset identical on every run.
- **With the chain the measurements change with current; without it they repeat.** The chain
  adds enough friction to distort even an open-loop test. **Main suspect: chain friction.**

## Next — the test that decides it

Chain off, new table applied, VESC Tool, hands and cables away from the sprocket:
1. Duty 10, 20, 30 %, as before.
2. Current 2, 3, 5 A from standstill, a few seconds each.

**Pass:** the motor starts smoothly at ~2 A, and the reported current stays within ±1 A of the
request below 2500 erpm, never negative.
- **Pass → the chain is the cause.** Refit it with a tension given as a number (sag at the
  middle of the free span; check the chain's spec, ~1–2 cm is the usual rule for small
  chains) and the sprockets aligned, then repeat with the chain on.
- **Fail → the Hall error moves up the list:** then test `foc_hall_interp_erp`, and moving
  `foc_sl_erpm_start`, **one change at a time**.

## Results — chain off, 2026-11-05 22:06

Log: VESC Tool, 147 s, 5354 samples. Data and plots: [`06_data/2026-11-05_low-speed-no-chain/`](../06_data/2026-11-05_low-speed-no-chain/).
Two current runs (1 A, 2 A, then ~2.5 A) and one duty sweep (2 → 48 % in 2 % steps).

| Check | Result |
|---|---|
| Breakaway | 1 A and 2 A: rotor does **not** move (0 erpm for ~10 s each). Moves at ~2.3–2.5 A. With the chain it needed ~7 A |
| Duty start | Turns at **2 % duty** (113–231 erpm). With the chain, 30 % did not turn it |
| "Negative current" at standstill | **Display sign, not braking.** iq = +1.0 / +2.0 A (forward torque), battery current 0. VESC Tool's "motor current" is `SIGN(vq·iq)·|i|` (`mcpwm_foc.c:1188`). At standstill vq is −0.03 to −0.08 V, smaller than the dead-time voltage error, so its sign is noise |
| Spin-up to 16 000 erpm | Physics, not a fault: no load, so a constant current is a constant torque and the motor accelerates until the back-EMF meets the battery (duty 0.95, vq 28.2 V ≈ λω = 27.2 V + R·i). It passes 4000 erpm without a jump |
| Current ripple vs speed (duty sweep, id std) | 0.45 A below 500 erpm → **2.1 A at 2000–2500** → 1.2–1.6 A in the blend → **0.14–0.2 A above 4000** (observer only). Peaks −7 / +6 A of id with the rotor turning freely |
| Faults | `fault_code` = 0 in all 5354 samples. Four ~2 s gaps in the log stream (t = 10.6, 15.2, 45.2, 95.9 s) |

**Verdict.** Pass on the main question: **the chain caused the "won't start" symptom** (breakaway
7 A → 2.5 A, duty 30 % → 2 %). Fail on the second criterion: below 4000 erpm the current is still
noisy, chain off, so there is a second, smaller problem. It sits **exactly where the Hall angle
is used** and disappears where the observer alone gives the angle. Main suspect now: the Hall
angle between edges (19° placement spread, interpolation above `foc_hall_interp_erpm` = 500).

**Next, one change at a time:**
1. Move the blend down (`foc_sl_erpm_start` / `foc_sl_erpm` 2500/4000 → about 1000/2000) and
   repeat the duty sweep. If the noisy band moves down with it, the Hall angle is the cause.
   The observer has enough signal there: at 1500 erpm, E = λω ≈ 2.5 V against R·i ≈ 0.05 V.
2. Refit the chain to a tension spec and repeat with the chain on.

## Results — handover moved down, 2026-11-05 23:14

Only change (reported by Pol, **not yet confirmed by a config export**): `foc_sl_erpm_start` /
`foc_sl_erpm` 2500/4000 → 1000/2000. Same duty sweep, twice, plus one current run. Log
`2026-11-05_23-14-20.csv`, 5277 samples, fault code 0 in all. Plot: `4_before_after.png`.

| Speed band | id ripple (std), before → after | Reported speed ripple (std), before → after |
|---|---|---|
| 2000–3400 erpm | 1.7–2.4 A → **0.12–0.21 A** | 21–27 → **2–3 erpm** |
| 1000–1700 erpm | 0.5–1.2 A → 0.36–0.73 A | 24–31 → 7–19 erpm |
| above 4000 erpm | 0.12–0.21 A → same | 2.4–5 → same |

**Verdict: pass.** Above 2000 erpm the ripple is now at the observer's level (< 0.3 A), and
the noisy band moved down with the handover. **The Hall angle is the cause of the
low-speed current ripple**; the chain was the cause of the hard start. The second sweep
repeats the first within ±0.1 A.

Watch-out when reading the speed: the reported erpm is a PLL on the **same angle** the
controller uses (`foc_speed_soure = 0`, "corrected" phase, `mcpwm_foc.c:3823`). In the Hall
zone a wobbly erpm is the angle error seen a second time, not independent proof that the rotor
speed wobbles.

**Left open:**
- Below ~1700 erpm there is still some ripple (Halls still in charge there). Below 500 erpm the
  VESC does not interpolate (`foc_hall_interp_erpm` = 500), so the angle moves in 60° steps.
  Normal for Halls; it matters for launches under load, not here.
- Is the observer good enough at 1000–2000 erpm **under load**? Wheels-in-the-air says
  nothing about that. To check when the chain is back on.
- Confirm 1000/2000 with an XML export (and `l_current_max`).

VESC Tool message "could not get position working" (Pol, corrected wording): it appears when
logging starts, and the rotor-position plot stays empty. The controller logged no fault in either
run, so it is a VESC Tool plot limitation, not a control fault. Cause not checked.

## Options for the Hall ripple (decided with Pol, 2026-11-05)

| Option | Verdict |
|---|---|
| **A. Keep the handover at 1000/2000 erpm** | **Chosen.** Halls only where the observer cannot work (standstill and launches) |
| B. Re-detect the Hall table | No: done twice, same 19°. The error is where the sensors sit; the table stores one angle per state and cannot move an edge |
| C. Inspect the sensors | When the motor is opened for the rotor photos (`01_plan/tareas-quad.md`, `03_hardware/open-questions.md` Risk 3) |
| D. HFI (sensorless at standstill by signal injection) | Not now: needs saliency, and the motor has little (Lq/Ld ≈ 1.14); audible whine |
| Sensorless everywhere | No: at standstill E = λω = 0, nothing to read; a launch under load needs the Halls (errores #21) |

**Next, in order:**
1. ~~Export the VESC config~~ Done 23:41: 1000/2000 ✓, poles 6 ✓, battery 39/−25 A ✓, motor
   current ±120 A by choice.
2. Chain back on at a measured tension, then the same duty sweep with the chain. Compare with
   these two runs.
3. Under load, when the logger records to the SD again (`tareas-quad.md`, test F): does the
   observer at 1000–2000 erpm hold? If not, raise the handover 500 erpm at a time.
4. Check the observer's own parameters against the measured motor: `foc_motor_flux_linkage`
   16.19 mWb vs λm 16.86 mWb measured (−4 %); `foc_motor_r` 18.8 mΩ vs 28.0 mΩ in
   `baseline.md`. Both matter most at low speed, which is exactly where the handover now sits.

## Can the Hall signal be filtered? (research, 2026-11-05)

- **The VESC has one Hall filter, and it is already on:** `m_hall_extra_samples` = 3 reads
  each Hall 7 times and takes the majority (`utils_sys.c:92`). It removes electrical glitches
  of microseconds. It cannot move an edge that is physically in the wrong place, and any
  slower filter would only add delay, which is another angle error.
- **The VESC does not correct misplaced sensors.** The table stores one angle per state; the
  firmware assumes each edge is halfway between two states. Forum replies say the same: "it
  will work, less efficiently". A real fix in software would store the six measured edge
  angles (what `hall_analyze` prints) instead: that needs custom firmware. Not now.
- **Others with the same symptom:** the usual community advice goes the **other way**, raising
  the handover to 4000–7000 erpm for torque at low speed, because the observer is weak under
  load. That is why the load test decides (`01_plan/tareas-quad.md`, test F).
- An open report (VESC forum, Jan 2026, no reply) says the interpolation under-predicts speed
  at low erpm because `foc_hall_interp_erpm` also sets a rate limit (`fmaxf` in
  `foc_correct_hall`). Seen in our source; not tested here.

Sources: [esk8.news, sensored FOC](https://forum.esk8.news/t/motor-issues-sensored-foc/7404) ·
[esk8 builders, stuttering at low speed](https://electric-skateboard.builders/t/sensored-motors-stuttering-at-low-speed-high-throttle-but-only-on-foc/53321) ·
[VESC forum, interpolation](https://vesc-project.com/node/4903) ·
[VESC forum, hall_analyze](https://vesc-project.com/node/3002) ·
[IEEE, Hall misalignment](https://ieeexplore.ieee.org/document/4763350).

## Mistakes made on the way (Claude)

- The Hall table was first converted with **256 = 360°**. That invented a 130° gap that never
  existed. The firmware says 200 = 360°. Lesson: read the source before converting a
  third-party number (`05_firmware/CLAUDE.md`, rule 3).

## Config discrepancies found, closed

From the export of 2026-11-05 17:29: `si_motor_poles = 9`, `l_in_current_max = 99` A. Export of
23:41: poles 6, battery current 39 / −25 A. Motor current stays at ±120 A: Pol's choice.

## Limitations

Wheels in the air: no load, so it says nothing yet about launches under real load.
