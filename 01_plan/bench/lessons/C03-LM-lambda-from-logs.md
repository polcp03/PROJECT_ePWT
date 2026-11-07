---
id: C03-LM
cycle: C03
title: λm from your CAN logs
date: 2026-11-10
slot: 2
minutes: 55
lede: On 7 September you measured λm with a drill and a scope: 16.855 mWb. On 31 October your own logger recorded the VESC while you blipped the throttle. Today you pull λm out of that recording, with no scope and no drill, and you turn the result into the first requirement of your motor model.
sources: 04_model/params/motor_params.m (λm by scope and by no-load telemetry; duty and |v_dq| definitions, mcpwm_foc.c as quoted there) · 04_model/scripts/can_log_decode.py (VESC status frames, comm_can.c scaling) · 07_experiments/EXP-002 and 06_data/README.md (log_017) · 01_plan/roadmap.md (C03 skill gate)
---

## Predict {#predict}

:::q id=p1 kind=predict
Your motor runs at a steady speed with a small current, id = 0 (your VESC has MTPA and field weakening off). Write the q-axis voltage equation at steady state, and solve it for λm. Which term do you expect to be small?
key:
- steady state, d/dt = 0: vq = Rs·iq + ωe·λm (with id = 0 the Ld·id term vanishes)
- so λm = (vq − Rs·iq) / ωe, with ωe in electrical rad/s
- Rs·iq is small: 28 mΩ × 10 A = 0.28 V against ~20 V of back-EMF at 12 000 erpm (≈ 1.4 %)
- the d axis still carries vd = −ωe·Lq·iq, which makes |v| slightly bigger than vq
traps:
- using mechanical speed (ωm) instead of ωe = p·ωm
- forgetting that the VESC reports erpm, which is already electrical
solution:
vq = Rs·iq + ωe·λm, so λm = (vq − Rs·iq)/ωe. The resistive drop is about 1 % of the voltage at cruise, so λm ≈ vq/ωe to first order. Do not forget vd = −ωe·Lq·iq: the arrow the VESC builds is a bit longer than vq.
:::

:::q id=p2 kind=predict
The VESC does not send voltage over CAN. It sends **duty** (status 1) and **input voltage** (status 5). Guess: in FOC, what voltage does duty = 1.0 correspond to? Vbus? Vbus/2? Vbus/√3? Say why.
key:
- duty = 1 is the largest sine SVPWM can make in its linear range: |v_dq| = Vbus/√3 (30 V at 52 V)
- in the VESC's FOC, duty = √3·|v_dq| / Vbus, so |v_dq| = duty·Vbus/√3
- |v_dq| is amplitude-invariant: the peak of the phase (line-to-neutral) voltage, the same quantity as ωe·λm
- his own data confirms it: 7 Sep, duty 0.9486 × 52.77 V / √3 = 28.90 V against |v_dq| = 28.886 V logged by VESC Tool (0.05 %)
traps:
- Vbus/2 (that is sine PWM against the mid-point, 26 V)
- line-to-line (×√3 more), which would give λm 1.73 times too big
solution:
Duty in the VESC's FOC is the length of the voltage arrow scaled so that 1.0 is the inscribed circle of the hexagon: |v_dq| = duty·Vbus/√3. You do not have to take the firmware's word for it: on 7 September VESC Tool logged duty 0.9486, Vbus 52.77 V and |v_dq| 28.886 V, and 0.9486 × 52.77/√3 = 28.90 V.
:::

:::q id=r1 kind=recall
From your own mistakes list (#13): is what you do today **verification** or **validation** of the motor model? One line each.
key:
- verification: did I build the model right, against its requirement (e.g. the model's λm equals the measured parameter)
- validation: does the model predict reality for its use, with data different from the data used to set it
- today is a step towards validating λm: the model's λm came from the scope test, the CAN log is independent data from the vehicle in use
- it is not yet validation of the whole model: only one parameter, at near-zero load, wheels in the air
traps:
- "validating is checking that everything works as designed" (his mistake #13)
solution:
Verification asks "built right?" against a requirement; validation asks "right thing?" against reality, with new data. Today checks the model's λm, set from a scope test, against an independent on-vehicle recording: one step of validation, for one parameter, at light load.
:::

## Build {#build}

Software rule (skill `software-con-ia`): **you write the contract and the acceptance test with a number; the AI writes the code**; you read its output and decide if it passes. Physics stays yours: the equation is the one you wrote in Predict.

### Find the data and its columns

The recording is `06_data/2026-10-31_can_logger_bench/raw/log_017.csv`: 137 s, wheels in the air, throttle blips, 0 corrupt frames after the EXP-002 fix. Raw CAN, one line per frame: `t_us,id,ext,dlc,d0..d7`. The decoder `04_model/scripts/can_log_decode.py` already turns it into signals (`load()` returns a table). The frames you need, all from VESC id 15, each arriving about every 21 ms (≈ 48 Hz):

- status 1: `erpm` (int32), `I_motor` (int16 / 10, A), `duty` (int16 / 1000)
- status 4: `I_batt` (int16 / 10, A)
- status 5: `V_in` (int16 / 10, V)

> Look at `04_model/results/can_logger_log017.png` first: it is mostly throttle blips, very few steady holds. That shapes your filter.

### Write the contract (you, five lines)

In the session, give the AI the header of a new script, `04_model/scripts/lambda_from_can.py`, in your words: inputs, outputs with units, the formula, which samples it keeps and why, and what it does when there are too few. Then ask it to write the code reusing `load()` from `can_log_decode.py`.

:::q id=b1 kind=check
Paste your five-line contract here before you send it to the AI.
key:
- input: path of a can_logger CSV; uses erpm, I_motor, duty, V_in; reuses can_log_decode.load()
- formula: |v| = duty·V_in/√3; vd = −ωe·Lq·I; vq = √(|v|² − vd²); λm = (vq − Rs·I)/ωe with ωe = erpm·2π/60
- sample filter with numbers: current-controlled (I_motor > 0.5 A, not exactly 0), speed high enough for voltage resolution (erpm > 2000), quasi-steady (|d erpm/dt| below a threshold, e.g. 1500–3000 erpm/s)
- outputs: number of samples kept, median and 10–90 % spread of λm in mWb, a least-squares fit of vq against ωe (slope = λm, intercept = voltage offset), a plot of λm against erpm saved to 04_model/results/
- failure: fewer than ~20 samples → says so and gives no number, instead of a number from three points
traps:
- "it reads the log and gives λm" (no filter, no number, no failure case)
- keeping coast samples with I_motor = 0.0 (see Check k2)
- using Vbus/2 or line-to-line scaling
solution:
Example: "lambda_from_can.py <log.csv>. Reads erpm, I_motor, duty, V_in with can_log_decode.load(). Keeps samples with I_motor > 0.5 A, erpm > 2000 and |d erpm/dt| < 3000 erpm/s. For each: |v| = duty·V_in/√3, vq = √(|v|² − (ωe·Lq·I)²), λm = (vq − Rs·I)/ωe. Prints n, median and p10–p90 of λm in mWb and a fit of vq vs ωe with its intercept; saves λm vs erpm as a PNG in 04_model/results/. Under 20 samples it prints 'not enough steady data' and no λm."
:::

### Write the acceptance test (you choose the number)

Before you trust the script on real data, it must pass on data where you **know** the answer. Ask the AI for a test that builds a synthetic log from your dq equations with λm = 16.855 mWb (some steady segments, some noise, some I = 0 coast samples) and runs the script on it.

:::q id=b2 kind=check
What is your acceptance criterion, with its number? Why that number?
key:
- on synthetic data with known λm = 16.855 mWb, the script returns it within a stated tolerance, e.g. ±0.5 % (tighter than the effect being measured)
- and it rejects the I = 0 coast samples and the transients (the test includes them on purpose)
- the tolerance is set by the quantisation in the frames: duty in steps of 0.001 and V_in in steps of 0.1 V (0.2 %) at full speed
- a test that only checks "it runs" or "the number is plausible" is not a test (his mistake #12)
traps:
- testing only on log_017 itself: then the script and the expected value come from the same place
solution:
For example: "On a synthetic log generated with λm = 16.855 mWb, 0.001 duty steps and 0.1 V steps, the script returns 16.855 ± 0.08 mWb (±0.5 %) and keeps none of the I = 0 or accelerating samples." The number comes from the frame resolution, not from hope.
:::

### Run it on log_017 and read the output

Run the test first, then `./.venv/Scripts/python.exe 04_model/scripts/lambda_from_can.py 06_data/2026-10-31_can_logger_bench/raw/log_017.csv`. Read the plot before the numbers: is λm flat across speed?

## Check {#check}

:::q id=k1 kind=check
What did the script give on log_017: samples kept, median λm, 10–90 % spread, the fit's slope and intercept, the speed range? How far is it from 16.855 mWb?
key:
- about 50–100 samples kept, depending on the steadiness threshold (≈ 100 at 3000 erpm/s, ≈ 50 at 1500, ≈ 30 at 800)
- median λm ≈ 16.9–17.0 mWb, 10–90 % spread ≈ 16.3–17.8 mWb
- fit of vq vs ωe: slope ≈ 17.1–17.4 mWb, intercept ≈ 0 V (−0.2 to 0 V)
- 2000–14 800 erpm, i.e. about 670–4930 rpm mechanical
- median within about +0.3 to +1 % of 16.855 mWb (fit +1.6 to +3 %); spread about ±5 %, far wider than the 0.17 % of the scope captures
traps:
- reporting one sample or a mean dominated by transients as "the" λm
- claiming agreement to 0.1 % from a spread of ±5 %
solution:
Expected (computed on this file with I > 0.5 A, erpm > 2000, |d erpm/dt| < 3000 erpm/s): 102 samples, median 17.0 mWb, p10–p90 16.3–17.8 mWb, fit slope 17.1 mWb with ~0 V intercept, over 670–4930 rpm mechanical. The median is about 1 % above the scope's 16.855 mWb. It agrees, but at the ±5 % level of this recording, not at the 0.2 % level of the scope.
:::

:::q id=k2 kind=check
Run it once keeping the samples with I_motor exactly 0.0 (coasting after a blip). What λm do they give, and why do you throw them out?
key:
- they read low, about 13 mWb at 2000–4000 erpm rising to about 16 mWb at 14 000 erpm (6–20 % low), not flat with speed
- exactly 0.0 A is the sign that the VESC has released the motor: no current control, no commanded voltage
- then duty is not the command the formula assumes; it is most likely built from the measured phase voltages, through filters (an inference, not checked in the firmware)
- the filter must keep only current-controlled samples
traps:
- "zero current is the cleanest case, R·i = 0": true only if the controller is still driving at 0 A
solution:
They give about 13 mWb at low speed, rising to about 16 mWb, 6–20 % low, and the error changes with speed. A current of exactly 0.0 A in hundreds of samples means the motor is released, so duty no longer is the voltage the controller commanded. Out. What duty means then is an open question for the firmware, not something to assume.
:::

:::q id=k3 kind=check
Name the factors you are not sure of in this estimate, and which way each one pushes λm.
key:
- V_in arrives in a different frame (status 5) up to ~20 ms from duty: during a sag (50.8 → 47 V in a blip) that alone is several % either way; steady samples limit it
- dead time: the VESC reports the commanded voltage; 0.12 µs × 30 kHz × Vbus ≈ 0.19 V more is applied, which would push λm up by about 5 % at 2000 erpm and 0.8 % at 14 000 erpm; the fit intercept ≈ 0 V says it is not visible in this data
- I_motor is the filtered total current (signed |i|), not iq; it lags in transients and makes Rs·I and vd slightly wrong; small at steady state
- transients left in: L·di/dt and acceleration bias the estimate high (the accelerating samples give 19–23 mWb)
traps:
- listing factors without the direction or the size
solution:
Bus voltage from a different frame (several % in a sag), dead time (+0.19 V: +5 % at 2000 erpm, +0.8 % at 14 000 erpm; not visible, intercept ≈ 0), a filtered total current used as iq (small at steady state), and leftover transients (push high). The ±5 % spread is the recording, not the method: it was a blip test, not a steady hold.
:::

## Judgement {#judgement}

:::q id=c1 kind=case
You want this number to ±1 % next time. What recording do you ask your logger and VESC for, before you even ride?
key:
- steady holds: 3–5 constant speeds (e.g. 1000, 2000, 3000, 4000, 4800 rpm), at least 5 s each, wheels in the air, in current or speed control so I_motor never hits 0.0
- both directions of torque at each speed (small positive and small negative current), so dead time and Rs·i cancel in the average
- higher status rate if the VESC allows, and V_in in the same frame time window
- write the expected value and band before the test (rule 3b in 04_model/CLAUDE.md)
traps:
- "ride the quad and log": the load and the noise add error without adding information about λm
solution:
Ask for steady holds at 4–5 speeds, 5 s each, with small positive and negative current at each, so the dead-time and resistive errors change sign and cancel. Freeze the prediction (16.855 mWb ± your band) before recording. A recording made for the question beats a recording made for something else.
:::

:::q id=c2 kind=error
"The CAN log gives 17.0 mWb and the scope 16.855 mWb, so the CAN log proves the scope was 1 % low. I will change mot.lambda_m to 17.0."
key:
- wrong direction of trust: the scope captures agree to 0.17 % and the no-load telemetry route gave 16.858 mWb; this log has a ±5 % spread
- a 1 % difference inside a ±5 % spread is not a finding
- changing the parameter to fit a log and then "validating" with the same log validates nothing (rule 3b, 04_model/CLAUDE.md)
- the right action: record the agreement and its band, keep 16.855, and design a better test if 1 % matters
solution:
The CAN estimate agrees with the scope within its own ±5 % spread; it cannot overrule a method that is 30 times tighter. Keep 16.855 mWb, write down "agrees within +1 % median, ±5 % spread, log_017", and if 1 % matters, record steady holds.
:::

## Close {#close}

:::q id=z0 kind=explain
In at most 5 lines, to an interviewer: how did you get λm out of a CAN log, and how good is it?
key:
- steady-state q-axis equation: λm = (vq − Rs·iq)/ωe with id = 0
- voltage from the VESC's duty: |v| = duty·Vbus/√3, verified against a VESC Tool log (0.05 %)
- filtered to current-controlled, quasi-steady samples; rejected released-motor samples that read 6–20 % low
- result ≈ 17.0 mWb median, ±5 % spread, within about 1 % of the scope's 16.855 mWb
solution:
At steady state with id = 0, vq = Rs·iq + ωe·λm. The VESC reports duty, and in its FOC |v| = duty·Vbus/√3, which I checked against its own voltage log to 0.05 %. I kept only current-controlled, near-steady samples (released-motor samples read 6–20 % low) and got a median of 17.0 mWb, ±5 % spread, about 1 % above my scope measurement. It agrees, at the level a blip recording allows.
:::

:::q id=g1 kind=case
**C03 gate.** Draft REQ-MOD-001: the acceptance criterion of your motor model, with a number, that C04 will verify against the CAN logs. One sentence for the need, then the requirement (what, how much, over what range, under what conditions), then how it will be verified. A session writes it into `00_system/` after you.
key:
- the need behind it: the model must predict motor torque and voltage well enough to design the current loop and the vehicle model; Kt ∝ λm, so the torque error is the λm error
- a quantity, a tolerance and a range: e.g. "the model's back-EMF constant agrees with λm estimated from on-vehicle CAN logs within ±3 % (median) over 1000–4900 rpm mechanical"
- conditions: steady-speed, current-controlled samples (I ≠ 0), id = 0, a log NOT used to set the parameter
- the tolerance is justified both ways: wider than what the measurement can resolve (median ±1 % here), tighter than what the use needs (e.g. torque within ±5 %)
- verification: the lambda_from_can.py script with its passing acceptance test, run on a new steady-hold recording, result written in the verification matrix
traps:
- no number, or a number with no range and conditions
- a tolerance tighter than the data can show (±0.2 % from a ±5 % log)
- calling it validation of the whole model (it is one parameter, light load)
- verifying with the same log used to tune the parameter
solution:
Example. Need: the model must predict torque per amp within 5 % for current-loop and vehicle design. REQ-MOD-001: "Over 1000–4900 rpm mechanical, at steady speed with id = 0 and |I| ≥ 1 A, the motor model's back-EMF constant shall agree with λm estimated from the VESC CAN log within ±3 % (median of at least 50 samples), using a recording not used to set the model." Verification: lambda_from_can.py, after passing its synthetic test, on a steady-hold recording in C04; result into the verification matrix.
:::

:::q id=z1 kind=doubt
What is still unclear, about the physics or the script? Write it as it is.
:::
