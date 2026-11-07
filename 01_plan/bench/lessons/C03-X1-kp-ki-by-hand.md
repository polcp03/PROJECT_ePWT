---
id: C03-X1
cycle: C03
title: "Exercise: Kp and Ki by hand for your motor"
date: 2026-11-06
slot: 2
minutes: 50
lede: One job, start to finish, the way a controls engineer would do it on day one: tune the q-axis current loop of your own motor on paper. Choose a bandwidth, get Kp and Ki, predict the step, check the 30 V, compare with what your VESC chose. On 11 November you check every number here in Simulink.
sources: Franklin, Powell & Emami-Naeini, Feedback Control of Dynamic Systems, 8th ed. (ebook, no printed page numbers) §4.3.4 and Example 4.5, §8.5.1–8.5.2 · Åström & Murray, Feedback Systems, 2nd ed. §11.4, pp. 11-15–11-18 · VESC firmware 03_hardware/vesc/_firmware: conf_general.c line 1513, motor/mcpwm_foc.c lines 4639–4695 · 04_model/params/motor_params.m
---

## The job {#job}

Your data, all from `motor_params.m`: Rs = 28.02 mΩ, Lq = 112.8 µH (q axis, where the torque current lives), λm = 16.855 mWb, p = 3, 52 V bus, so about 30 V of voltage vector (28.5 V with the VESC's 0.95 max duty), 120 A motor current limit. Control period OPEN: 66.7 µs (15 kHz, assumed) or 33.3 µs (30 kHz). Decoupling off.

The method from K2, in two lines: cancel the plant pole (Ki/Kp = R/L), then the loop is first order with bandwidth ωc = Kp/L. So Kp = ωc·L and Ki = ωc·R. Do every step with numbers and units. A step without a number is not done.

Write your answers here; on **11 November** you build this loop in Simulink and check each prediction against the simulated step. Keep them, they are your acceptance criteria.

## Steps {#steps}

:::q id=x1 kind=calc
**Step 1. Choose the bandwidth.** Pick a target ωc for your q-axis current loop, in rad/s and Hz, and justify it against two limits: (a) the sampling ceiling ωs/20 for the control period you must assume, and (b) the voltage: the proportional kick Kp·Δi of the largest step you will ask (0 → 120 A at standstill) should not exceed 30 V.
key:
- (a) control period is OPEN, so assume 15 kHz: ωs = 2π × 15 000 = 94 250 rad/s, ωs/20 ≈ 4710 rad/s (750 Hz); at 30 kHz it would be 9425 rad/s
- (b) Kp·120 ≤ 30 V → Kp ≤ 0.25 V/A → ωc ≤ 0.25/112.8 µH ≈ 2200 rad/s
- the voltage limit is the tighter one: a choice around 2000 rad/s (318 Hz) is justified; any value 1000–2200 rad/s with this reasoning is fine
- a choice above about 4700 rad/s is wrong until the control period is confirmed
traps:
- mixing Hz and rad/s
- using 30 kHz as the loop rate without saying it is open
- picking a number "because the VESC uses it" with no limit checked
solution:
Sampling: with the period open you take 15 kHz, so ωs/20 ≈ 4710 rad/s. Voltage: a 120 A step with Kp = ωc·Lq asks Kp·120 volts at once; for 30 V that means ωc ≤ 2200 rad/s. The voltage is the tighter limit. A good choice: ωc = 2000 rad/s, 318 Hz, inside both, and the reference numbers below use it.
:::

:::q id=x2 kind=calc
**Step 2. Kp and Ki.** With your ωc, compute Kp and Ki, with units. Check that Ki/Kp equals the q-axis R/L, and say in one line what that equality buys you.
key:
- for ωc = 2000 rad/s: Kp = 2000 × 112.77 µH = 0.2255 V/A
- Ki = 2000 × 0.02802 Ω = 56.04 V/(A·s)
- Ki/Kp = 248.5 rad/s = Rs/Lq (τ = 4.02 ms): the PI zero cancels the plant pole
- result: the loop gain is Kp/(Lq·s), a first-order closed loop with no overshoot and no steady error
traps:
- swapping them (Kp = ωc·R, Ki = ωc·L)
- using Ld = 99 µH or the average 106 µH for the q loop
- units: Kp in V/A, Ki in V/(A·s)
solution:
Kp = 0.2255 V/A, Ki = 56.04 V/(A·s). Ki/Kp = 248.5 rad/s, exactly Rs/Lq. The PI zero sits on the motor's pole, they cancel, and what remains is a pure integrator Kp/(Lq·s): a first-order closed loop, no overshoot, no leftover error.
:::

:::q id=x3 kind=calc
**Step 3. Predict the step.** Rotor held still, iq reference steps 0 → 60 A. Predict when the current crosses 6 A and 54 A, and the 10–90 % rise time. Does the answer change for a 0 → 20 A step? Why?
key:
- first-order: i(t) = 60·(1 − e^(−ωc·t))
- 10 %: t = ln(1/0.9)/ωc = 0.053 ms; 90 %: t = ln 10/ωc = 1.15 ms
- rise 10–90 % = ln 9/ωc = 1.10 ms
- same for 20 A: a linear loop's timing does not depend on step size, as long as the voltage does not saturate (kick 0.2255 × 60 = 13.5 V here)
traps:
- using τ of the motor (4 ms) instead of 1/ωc (0.5 ms)
- saying a larger step is slower (only true once it saturates)
solution:
i(t) = 60·(1 − e^(−2000·t)). 6 A at 0.053 ms, 54 A at 1.15 ms: rise 1.10 ms. A 20 A step has the same timing, because the loop is linear and the first voltage, 13.5 V for 60 A, is well below the limit. Notice the loop (0.5 ms) is 8 times faster than the motor's own 4 ms.
:::

:::q id=x4 kind=calc
**Step 4. Is 30 V enough?** Same 0 → 60 A step. (a) At standstill: the first voltage asked and the steady voltage. (b) At 4000 rpm, starting from iq ≈ 0: the first voltage asked (remember what the integrator already holds) and the steady |v| with the cross-coupling term. Compare with about 28.5 V.
key:
- (a) first sample Kp·60 = 13.5 V; steady Rs·60 = 1.68 V: fits easily
- (b) ωe = 1257 rad/s, back-EMF 21.18 V already in the q integrator; first sample 21.18 + 13.5 = 34.7 V: above 28.5 V, so the start saturates and the rise is slower than 1.10 ms
- (b) steady: vq = 1.68 + 21.18 = 22.86 V, vd = −1257 × 112.8 µH × 60 = −8.50 V, |v| = 24.4 V: fits, about 4 V of margin
- so 60 A is reachable at 4000 rpm, but the transient briefly hits the wall; anti-windup (the VESC's integrator clamp) keeps it clean
traps:
- forgetting the back-EMF already sitting in the integrator
- forgetting vd from cross-coupling
- using 30 V and missing that the VESC clamps at 0.95 duty
solution:
(a) 13.5 V at once, 1.68 V in steady state: no problem. (b) The integrator already holds about 21.2 V of back-EMF; the step adds 13.5 V: 34.7 V asked, more than 28.5 V, so the first part is voltage-limited. In steady state vq = 22.86 V, vd = −8.50 V, |v| = 24.4 V: inside, with about 4 V to spare. At 4000 rpm the loop gets there, a little late.
:::

:::q id=x5 kind=calc
**Step 5. Compare with your VESC.** Your device has kp = 0.2119 V/A and ki = 56.20 V/(A·s) (motor_params.m, after the 2026-09-07 detections). Compare with your Kp and Ki in %. Which bandwidth did VESC Tool aim for, which inductance did it use, and what is its real bandwidth on your q axis?
key:
- ki: 56.20 vs 56.04, +0.3 %; ki/R = 2006 rad/s
- kp: 0.2119 vs 0.2255, −6 %; kp/106 µH = 1999 rad/s: VESC Tool aimed at 2000 rad/s (tc = 500 µs) with the average L = 106 µH, not Lq
- real q-axis bandwidth = 0.2119/112.8 µH = 1879 rad/s, rise ≈ 1.17 ms
- its zero (265 rad/s) is slightly off the q pole (248.5): about 0.4 % overshoot, negligible
- the old XML (kp 0.102, ki 18.83, bw 1000) is not the device state; confirm live in VESC Tool
traps:
- concluding the VESC is "wrong" because kp differs by 6 %
- trusting 03_hardware/vesc/MOTOR_1.9.xml as current
solution:
ki matches yours to 0.3 %. kp is 6 % lower because VESC Tool used the average inductance, 106 µH: kp/L = 1999 rad/s, so it aimed at exactly 2000 rad/s, tc = 500 µs. On your q axis that is 1879 rad/s and a 1.17 ms rise, with about 0.4 % overshoot from the small zero mismatch. You reached the same design from first principles.
:::

:::lab piloop
Your gains in the current loop
:::

:::q id=x6 kind=lab
**Step 6. Put your numbers in the lab** (above). Set your Kp and your Ki (or Kp and "Cancel the pole"), a 60 A step, 5 ms window. Read the rise time, overshoot and peak voltage. Then a 120 A step: what is the peak voltage now, and is it under 30 V as Step 1 required? Compare with the dashed VESC trace.
key:
- 60 A: rise about 1.0 ms in the lab (formula 1.10 ms; the discrete loop differs a little), no overshoot, peak voltage about 13.8 V
- 120 A: peak about 27.6 V, under 30 V as designed in Step 1 (the lab adds one sample of current rise before the kick)
- VESC dashed trace a little slower (about 1.07 ms in the lab): its kp was sized for 106 µH
- the lab holds the rotor still and samples at 30 kHz: it does not show the 4000 rpm saturation of Step 4
solution:
Your gains: about 1.0 ms, no overshoot, about 13.8 V peak for 60 A. At 120 A the peak is about 27.6 V, still under 30 V, which is exactly what Step 1 bought you. The VESC's trace lags a little because its kp was sized for the average L. The lab cannot show Step 4: no back-EMF, rotor still.
:::

:::q id=x7 kind=error
**Step 7. Find the error.** A colleague looks at your design: "1.1 ms is slow. Double Ki, the integral pushes harder, so the current gets there faster." Use your numbers: what does doubling Ki do to the zero, the rise time and the overshoot? Which knob would you turn instead, and how far?
key:
- 2Ki: the zero moves to 497 rad/s, no longer on the 248.5 rad/s pole: the closed loop becomes second order
- result: rise only from 1.10 to about 0.87 ms, but about 5.5 % overshoot (13 % at 4× Ki), and more windup under saturation
- the speed knob is Kp (bandwidth Kp/L): doubling Kp and Ki together gives 0.55 ms with no overshoot
- but 2Kp means ωc = 4000 rad/s: still under the 4700 rad/s ceiling, yet the 120 A kick becomes 54 V, so big steps saturate; Step 1's limit is why you did not do it
traps:
- agreeing that Ki sets speed
- doubling Kp without re-checking the sampling ceiling and the 30 V kick
solution:
Doubling Ki moves the zero to 497 rad/s, off the motor's pole, so the cancellation is gone. You gain little speed (1.10 → about 0.87 ms) and buy about 5.5 % overshoot, plus more windup when saturated. Speed is Kp's job: double Kp with Ki and you get 0.55 ms clean. That is still inside the 4700 rad/s ceiling, but a 120 A step would ask 54 V; that is why you stopped at 2000 rad/s.
:::

:::q id=x8 kind=explain
**Step 8. Explain it.** In at most 5 lines, as to an interviewer: how you tuned the current loop of your motor, the numbers, and what you will check in Simulink on 11 November.
key:
- cancellation: Ki/Kp = Rs/Lq = 248.5 rad/s, so Kp = ωc·Lq, Ki = ωc·Rs
- ωc = 2000 rad/s, chosen under the voltage limit (≈ 2200 rad/s for a 120 A kick) and the sampling ceiling (≈ 4700 rad/s at 15 kHz): Kp = 0.2255 V/A, Ki = 56.04 V/(A·s)
- prediction: 1.10 ms rise, no overshoot; at 4000 rpm a 60 A step saturates briefly (34.7 V asked)
- the VESC got the same: kp 0.2119, ki 56.20 (2000 rad/s on the average L)
- in Simulink: step response, rise time, overshoot, voltage, at standstill and at 4000 rpm
solution:
The q axis is an R-L plant, 28 mΩ and 113 µH. I put the PI zero on its pole, so Kp = ωc·L and Ki = ωc·R. I chose 2000 rad/s: under the 4700 rad/s sampling ceiling for a 15 kHz loop, and low enough that a 120 A step asks under 30 V. That gives 0.2255 V/A and 56 V/(A·s), a 1.1 ms rise, no overshoot; my VESC chose the same. On 11 November I check rise, overshoot and voltage in Simulink, at standstill and at 4000 rpm.
:::

:::q id=x9 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
