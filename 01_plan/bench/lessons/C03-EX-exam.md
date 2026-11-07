---
id: C03-EX
cycle: C03
title: C03 exam: dq, limits and the current loop
date: 2026-11-12
slot: 1
minutes: 45
lede: Forty-five minutes, from memory, on your own quad. Sit on the rotor, draw the three walls, close the current loop, pull a number out of a log, and three judgement calls an interviewer would ask.
sources: Hughes & Drury, Electric Motors and Drives, 5th ed. §8.2.2 pp. 266–267, §8.6.1 pp. 287–290, §9.5.1 pp. 342–344, §9.5.2 pp. 345–349, §9.6.3 pp. 358–360 · Åström & Murray, Feedback Systems 2e, §9.5 pp. 9-27–9-28, §11.4 pp. 11-15–11-17 · Franklin, Powell & Emami-Naeini 8e, §3.3 Fig. 3.14, §3.4.1 eq. (3.68) · 04_model/params/motor_params.m (VESC dq equations, PI form and gains)
---

From memory: no notes, no lessons, no AI. A calculator is fine. One attempt per question, equation before the number, units on every number. The app grades each answer as you go and brings the misses back in Review until you get them right on two different days. Several questions look like ones from the lessons; the numbers and the twist are new, so read each one to the end.

## Part 1 · Park and dq {#p1}

:::q id=a1 kind=calc
One sample from your VESC: iU = −13.9 A, iV = 75.2 A. The rotor's d axis is at θe = 40° electrical. Find iW, iα, iβ, then id and iq. How much torque does this make, and how much would the same 80 A make if it all sat on q?
key:
- iW = −iU − iV = −61.3 A; iα = iU = −13.9 A; iβ = (iV − iW)/√3 = 136.5/√3 ≈ 78.8 A (arrow ≈ 80 A at 100°)
- id = iα·cos 40° + iβ·sin 40° ≈ +40.0 A; iq = −iα·sin 40° + iβ·cos 40° ≈ 69.3 A (length still 80 A)
- the current sits 60° electrical ahead of the magnet, not 90°: part of it strengthens the flux instead of pulling
- Te = 1.5·3·(λm + (Ld − Lq)·id)·iq = 4.5 × (16.855 − 0.54) mWb × 69.3 ≈ 5.09 N·m, against 0.0758 × 80 ≈ 6.07 N·m all on q (−16 %)
traps:
- sign slip in iq: it is −iα·sin θe and iα is negative here
- iβ = (iV + iW)/√3 instead of the difference
- forgetting that with Ld < Lq a positive id also removes a little reluctance torque
solution:
iW = −61.3 A, iα = −13.9 A, iβ = 78.8 A: an 80 A arrow at 100°. With the d axis at 40°, the current is 60° ahead of the magnet: id = +40.0 A, iq = 69.3 A. Torque = 4.5 × (0.016855 − 13.54e-6 × 40) × 69.3 ≈ 5.09 N·m. The same 80 A on q would give 6.07 N·m. The 40 A on d heat the copper and push the magnet's flux up; they pull nothing.
:::

:::q id=a2 kind=calc
VESC Tool's realtime page shows **9000 ERPM**. What is the motor shaft speed in rpm, the electrical frequency, ωe, and the peak phase back-EMF? At a control period of 15 kHz and of 30 kHz (your build is still unconfirmed), how many control periods fit in one electrical cycle, and how many degrees does the rotor turn, electrical and mechanical, between two of them?
key:
- ERPM is electrical: rpm = 9000 / p = 3000 rpm at the shaft; fe = 9000/60 = 150 Hz; ωe = 942 rad/s
- E = ωe·λm = 942 × 0.016855 ≈ 15.9 V peak phase
- 15 kHz: 100 periods per cycle, 3.6° electrical = 1.2° mechanical per period; 30 kHz: 200 periods, 1.8° electrical = 0.6° mechanical
- the angle the VESC uses in Park and inverse Park is already up to one period old: the error grows with speed
traps:
- multiplying ERPM by 3 (27 000 rpm): ERPM is already p times the shaft speed (his electrical vs mechanical slips)
- using ωm = 314 rad/s in the back-EMF (gives 5.3 V)
- mixing electrical and mechanical degrees in the last part
solution:
9000 ERPM / 3 = 3000 rpm. fe = 150 Hz, ωe = 942 rad/s, E = 15.9 V peak phase. At 15 kHz the VESC runs 100 times per electrical cycle, and between two runs the rotor turns 3.6° electrical, which is 1.2° mechanical. At 30 kHz it is 200 runs and 1.8° (0.6° mechanical). Electrical is what Park cares about.
:::

:::q id=a3 kind=calc
Climbing at **3000 rpm** with id = 0, iq = **70 A**, steady state. Compute vd, vq and |v|. Then the electrical power into the motor and the battery current at 52 V (ideal inverter). Your friend says "70 A in each phase, so the battery gives 3 × 70 = 210 A". Answer him in one line.
key:
- ωe = 942 rad/s; vd = −ωe·Lq·iq = −942 × 112.77 µH × 70 ≈ −7.44 V; vq = Rs·iq + ωe·λm = 1.96 + 15.89 ≈ 17.85 V; |v| ≈ 19.3 V (< 30 V, fits)
- P = 1.5·(vd·id + vq·iq) = 1.5 × 17.85 × 70 ≈ 1874 W (vd does no work because id = 0)
- check: shaft 5.31 N·m × 314 rad/s ≈ 1668 W plus copper 1.5 × 0.028 × 70² ≈ 206 W = 1874 W
- Ibat ≈ 1874 / 52 ≈ 36 A, just under the 40 A battery limit
- phase and battery current are linked by power, never by 3 or √3
traps:
- 3 × 70 or 70 × √3 for the battery current (his mistake #3 and #16)
- forgetting the 1.5 of the amplitude-invariant transform in the power
- using |v|·|i| instead of vd·id + vq·iq
- using mechanical ω in the back-EMF
solution:
ωe = 942 rad/s. vd = −7.44 V (cross-coupling), vq = 1.96 + 15.89 = 17.85 V, |v| = 19.3 V. P = 1.5 × 17.85 × 70 ≈ 1874 W: 1668 W to the shaft and 206 W of copper. Ibat = 1874/52 ≈ 36 A. To the friend: the inverter conserves power, not amps; 70 A at about 18 V on the motor side is 36 A at 52 V on the battery side.
:::

:::q id=a4 kind=case
You remounted the Hall board after a repair and did not re-run detection. At 2000 rpm the quad feels weaker. VESC Tool shows **Iq = 40 A, Id = 0**, as asked. Suppose the angle the VESC uses is 20° electrical **behind** the real rotor. What are the real id, iq and torque? Why do the Id/Iq plots look perfect, and which logged signal would give the fault away?
key:
- real id = −I·sin ε = +40·sin 20° ≈ +13.7 A, real iq = 40·cos 20° ≈ 37.6 A
- torque = 4.5 × (16.855 − 0.185) mWb × 37.6 ≈ 2.82 N·m against 3.03 N·m expected (−7 %); positive id makes the reluctance term subtract
- the VESC computes Id and Iq with its own (wrong) angle, so in its frame they read exactly what it asked: the error is invisible in the current plots
- what gives it away: the voltage vector does not match the model (|v| ≈ 12.7 V against ≈ 12.0 V predicted at 2000 rpm, 40 A), more battery current for the same acceleration; fix: re-run Hall detection
traps:
- "Id would show the error": no, it is measured in the wrong frame
- wrong sign: an angle behind gives positive id, ahead gives negative id
- electrical vs mechanical: 20° electrical is only 6.7° mechanical of Hall board misalignment
solution:
Real id = +13.7 A, real iq = 37.6 A, torque ≈ 2.82 N·m instead of 3.03 (−7 %), and the positive id even costs a little reluctance torque. VESC Tool shows Iq = 40 A and Id = 0 because it builds both with the same wrong angle. Look at what the angle error cannot hide: the dq voltages. At 2000 rpm and 40 A your model needs |v| ≈ 12.0 V; the misaligned motor needs ≈ 12.7 V, and more battery amps for the same pull. Re-run Hall detection. A 20° electrical error is only 6.7° of mechanical misalignment of the board.
:::

:::scene phases=3 field=on currents=off vectors=on dq=on labels=off rotor=on spin=on speed=0.1 delta=70 caption="Angle 20° behind: the stator field sits 70° from the magnet instead of 90°. Part of the current lies on d and pulls nothing."
Angle error seen from the rotor.
:::

src: Hughes §8.2.2, pp. 266–267 (rotating frame sees a constant phasor); §9.5.1, pp. 342–344 (torque from the current at right angles to the magnet flux); dq equations as quoted in 04_model/params/motor_params.m

## Part 2 · Limits and the id–iq plane {#p2}

:::q id=b1 kind=calc
Pulling away: **1000 rpm**, iq = **120 A**, id = 0, battery at 52 V. A forum post says "120 A × √3 = 208 A from the battery: your 40 A BMS trips at once". Compute vd, vq, the electrical power, how it splits between shaft and copper, and the real battery current. Which wall holds you here?
key:
- ωe = 314 rad/s; vd = −ωe·Lq·iq ≈ −4.25 V; vq = 0.028 × 120 + 314 × 0.016855 = 3.36 + 5.30 ≈ 8.66 V
- P = 1.5 × 8.66 × 120 ≈ 1558 W: shaft 9.10 N·m × 104.7 rad/s ≈ 953 W, copper 1.5 × 0.028 × 120² ≈ 605 W
- Ibat ≈ 1558 / 52 ≈ 30 A: below 40 A
- the 120 A current circle is the wall at 1000 rpm; the battery reaches 40 A only near 1550 rpm (≈ 11 km/h)
traps:
- × √3 or × 3 between phase and battery current (his mistakes #3 and #16)
- forgetting copper loss, which here is 40 % of the input
- calling the 40 A battery limit a circle on the id–iq plane: it is a power limit
solution:
ωe = 314 rad/s, vd = −4.25 V, vq = 8.66 V. P = 1.5 × 8.66 × 120 ≈ 1558 W, of which 953 W reaches the shaft and 605 W heats the copper. Battery: 1558/52 ≈ 30 A. At 1000 rpm the motor needs only about 9 V, so 120 A on the motor side costs 30 A on the battery side. The 120 A circle is the wall; the battery wall arrives a bit later, near 11 km/h.
:::

:::q id=b2 kind=calc
Half-charged pack resting at **48 V**. With the 0.95 duty cap, compute the voltage ceiling, the no-load speed (rpm and km/h: 92/11, wheel 0.155 m) and the corner speed for (0, 120 A) without Rs. Which way does Rs move the corner? Then: would raising the motor current limit to 140 A give you more top speed?
key:
- Vmax = 0.95 × 48/√3 ≈ 26.3 V (against 28.5 V at 52 V)
- no-load: ωe = 26.3 / 0.016855 ≈ 1562 rad/s → 521 rad/s → ≈ 4970 rpm ≈ 34.7 km/h (≈ 5390 rpm at 52 V)
- corner without Rs: ωe = Vmax / √(λm² + (Lq·120)²) = 26.3 / 0.0216 ≈ 1218 rad/s → ≈ 3880 rpm (≈ 27 km/h); Rs eats 3.4 V of vq and pulls it down to ≈ 3480 rpm (≈ 24 km/h)
- no: top speed is set by voltage against back-EMF; a higher current limit only lifts torque below the corner
traps:
- comparing the 48 V bus directly with the phase back-EMF (forgetting √3 and the 0.95)
- dividing by p in the wrong direction
- "more current, more speed": speed comes from voltage, current gives torque (his fixed-voltage vs current confusion, #2 and #15)
- adding λm·ωe and Lq·iq·ωe as scalars instead of in quadrature
solution:
Vmax = 26.3 V. No-load speed: 1562 rad/s electrical, 521 mechanical, about 4970 rpm or 34.7 km/h: the top speed falls almost in proportion to the bus. Corner: |ψ| = √(16.86² + 13.53²) mWb = 21.6 mWb, so 1218 rad/s, ≈ 3880 rpm; with the 3.4 V of Rs·iq it drops to ≈ 3480 rpm. A 140 A limit changes neither number: it only lifts the top of the current circle.
:::

:::q id=b3 kind=calc
Someone enables field weakening at **id = −50 A** and keeps |i| = 120 A. (1) What iq is left and what torque? (2) With iq ≈ 0, what is the no-load speed at 30 V now? (3) At that speed the controller trips: what peak back-EMF does the magnet alone produce, phase and line-to-line, against your 52 V bus? (4) Why can field weakening in your motor never reach "zero flux"?
key:
- iq = √(120² − 50²) ≈ 109.1 A; Te = 4.5 × (16.855 + 13.54e-3 × 50) mWb × 109.1 ≈ 8.61 N·m (vs 9.10 at id = 0)
- flux on d = λm + Ld·id = 16.855 − 4.96 ≈ 11.9 mWb; no-load ωe = 30 / 0.0119 ≈ 2520 rad/s ≈ 8030 rpm (vs 5670)
- at 8030 rpm the magnet alone gives λm·ωe ≈ 42.5 V peak phase, ≈ 73.6 V line-to-line: far above 52 V, the diodes rectify it into the battery (uncontrolled braking, bus overvoltage, beyond the VESC's 60 V)
- the ellipse centre is at −λm/Ld ≈ −170 A, outside the 120 A circle: the current limit stops you before the flux is cancelled
traps:
- the sign: negative id weakens the flux; positive strengthens it
- "field weakening adds power": it trades current (and heat) for speed
- forgetting that on a trip the magnet flux is back at full strength instantly
solution:
(1) iq = 109.1 A, torque ≈ 8.61 N·m: 5 % less for the same amps, the reluctance bonus is tiny. (2) The d-axis flux drops to 11.9 mWb, so 30 V reaches ≈ 2520 rad/s, about 8030 rpm. (3) If the VESC trips there, id vanishes and the full 16.855 mWb returns: 42.5 V peak phase, 73.6 V line-to-line, against a 52 V bus and a 60 V inverter. The diodes conduct, current flows into the pack with nobody controlling it. (4) Cancelling λm needs id = −170 A, beyond the 120 A circle.
:::

src: Hughes §8.6.1, pp. 287–290 (SVPWM, Vbus/√3); §9.5.2, pp. 345–349 (base speed set by inverter voltage; field weakening costs current); §9.6.3, pp. 358–360 (overvoltage on loss of control)

## Part 3 · The current loop {#p3}

:::q id=c1 kind=calc
After a long hill the winding is hot: Rs is 25 % above your measured value. Rotor locked, current loop OFF, you apply **vq = 2 V** as a step. Final iq? Time constant τq? How long until iq reaches 50 A? Compare the final current with a cold motor. What does that say about controlling torque by fixing the voltage?
key:
- hot Rs = 1.25 × 28.02 ≈ 35.0 mΩ; final iq = 2 / 0.035 ≈ 57.1 A (cold: 71.4 A)
- τq = Lq/Rs = 112.77 µH / 35.0 mΩ ≈ 3.22 ms (cold: 4.02 ms)
- t(50 A) = −τ·ln(1 − 50/57.1) ≈ 3.22 ms × 2.09 ≈ 6.7 ms
- with fixed voltage the current (and torque) is set by R, which moves with temperature (0.39 %/K), and once turning by the back-EMF: −20 % torque here for the same command. A current loop removes that dependence
traps:
- "τ is the same because L did not change": τ = L/R falls when R rises
- forgetting milli: 2/35 = 57 mA
- "a fixed voltage gives a fixed current" (his mistakes #2 and #15)
solution:
Hot Rs ≈ 35.0 mΩ: iq → 57.1 A with τq ≈ 3.22 ms, and 50 A after about 6.7 ms. A cold motor would settle at 71.4 A. Same 2 V, 20 % less torque, only from temperature, and it gets worse as soon as the rotor turns and the back-EMF subtracts. That is why the VESC regulates current, not voltage: the loop finds whatever voltage gives the asked amps.
:::

:::q id=c2 kind=calc
Imagine your VESC ran a **P controller only**, Kp = 0.2119 V/A, no integrator, no feed-forward. (1) Rotor locked, iq_ref = 60 A: steady iq and error? (2) Same request at 3000 rpm: steady iq? (3) Now add back-EMF feed-forward using the λm from one detection session, 15.919 mWb: what voltage error is left at 3000 rpm and what does it do with P only? What removes it?
key:
- (1) steady state vq = Kp·(60 − iq) = Rs·iq → iq = Kp·60/(Kp + Rs) ≈ 53.0 A; error ≈ 7.0 A (12 %)
- (2) at 3000 rpm E = 15.9 V: iq = (Kp·60 − E)/(Kp + Rs) = (12.7 − 15.9)/0.240 ≈ −13 A: the motor brakes; P alone cannot even overcome the back-EMF
- (3) feed-forward residual = ωe·(16.855 − 15.919) mWb ≈ 0.88 V → ≈ 3.7 A more error (iq ≈ 49 A)
- the integrator removes any constant error (resistance, back-EMF, wrong feed-forward): that is why it is PI
traps:
- expecting zero error with P only
- forgetting E is ωe·λm with electrical ωe (942 rad/s)
- thinking feed-forward replaces the integrator: it only shrinks the error the integrator must clear
solution:
(1) 0.2119·(60 − iq) = 0.028·iq gives 53.0 A, 7 A short. (2) At 3000 rpm the 15.9 V of back-EMF exceeds the 12.7 V that Kp·60 can command: iq settles at about −13 A, a brake. (3) Feed-forward with the VESC's λm leaves 0.88 V unexplained, which with P only costs about 3.7 A more (iq ≈ 49 A). The integrator keeps adding voltage while any error remains, so in steady state the error is zero whatever the disturbance.
:::

:::q id=c3 kind=calc
Your VESC has **Kp = 0.2119 V/A, Ki = 56.20 V/(A·s)** and uses the average L = 106 µH. (1) Show that the zero sits on the plant pole. (2) What ωc, in rad/s and Hz, closed-loop τ and 10–90 % rise time? (3) A colleague wants ωc = 8000 rad/s. With a loop delay of about 1.5 control periods, how much phase does the delay eat at 2000 and at 8000 rad/s, at 15 kHz? Is 8000 sensible?
key:
- Ki/Kp = 265 rad/s ≈ Rs/L = 0.02802/106e-6 = 264 rad/s: zero on the pole, open loop ≈ ωc/s
- ωc = Kp/L ≈ 2000 rad/s ≈ 318 Hz; closed-loop τ = 1/ωc = 0.5 ms; rise 2.2/ωc ≈ 1.10 ms; no overshoot
- delay phase ≈ ωc·1.5·Ts: Ts = 66.7 µs → 11.5° at 2000 rad/s, 46° at 8000 rad/s (half that at 30 kHz)
- 8000 rad/s at 15 kHz eats about half of a 90° margin: overshoot and noise, and it is only ~12× below the sampling rate; the continuous model would not show it; and first ask which requirement needs a faster loop
traps:
- 318 Hz confused with 2000 Hz (rad/s vs Hz)
- using 1.8/ωn: this loop is first order
- "faster is always better", or changing a gain with no requirement
solution:
(1) Ki/Kp = 265 rad/s and Rs/L = 264 rad/s: the PI zero cancels the R-L pole. (2) ωc = 0.2119/106e-6 ≈ 2000 rad/s = 318 Hz, τ = 0.5 ms, rise ≈ 1.1 ms, no overshoot. (3) A delay of 1.5 × 66.7 µs = 0.1 ms costs ωc·0.1 ms: 0.2 rad = 11.5° at 2000 rad/s, 0.8 rad = 46° at 8000 rad/s. That is the sampling ceiling: past roughly a tenth to a twentieth of the sampling rate the delay dominates. At 15 kHz, 8000 rad/s is too close; and nobody has written why the quad needs it.
:::

:::q id=c4 kind=calc
Full throttle at **5200 rpm**, iq_ref = 60 A, id = 0, no anti-windup, 30 V wall. (1) Can 60 A be reached? What iq is the most the 30 V allow? (2) The loop sits on the wall for 20 ms with about 15 A of error: how much voltage does the integrator store? (3) You then lift the throttle to 30 A. What does the motor do for the next ten-odd milliseconds, and what fixes it?
key:
- 60 A at 5200 rpm needs vq ≈ 29.2 V and vd ≈ −11.1 V, |v| ≈ 31.2 V > 30 V: not reachable; with id = 0 the maximum is iq ≈ 45 A
- stored: Ki·e·t = 56.2 × 15 × 0.020 ≈ 17 V above what is needed
- after lifting to 30 A the error turns negative but the stored integral keeps vq on the wall: iq stays near 45 A until it unwinds (a lag of milliseconds to tens of milliseconds; no exact number is required): an unwanted push
- fix: anti-windup (clamping stops integrating while saturated, or back-calculation); and a vector voltage limit, not per axis
traps:
- blaming the 120 A current limit: it is voltage
- "anti-windup makes it faster": it removes the overshoot and the late push
- forgetting the cross term: vd also needs 11 V at this speed
solution:
At 5200 rpm the back-EMF alone is 27.5 V. 60 A would need a 31.2 V arrow, so the best with id = 0 is about 45 A. Sitting on the wall with 15 A of error, the integrator piles up 56.2 × 15 × 0.02 ≈ 17 V that the inverter cannot deliver. When you ask for 30 A the error flips sign, but that stored voltage keeps vq pinned at 30 V while it bleeds away, so for a while (a rough hand estimate: 10–20 ms; Simulink B will show the real figure) the motor keeps pushing about 45 A. Clamping stops the integrator while the output is saturated; the push disappears.
:::

src: Franklin, Powell & Emami-Naeini 8e, §3.3 Fig. 3.14 (first-order time constant), §3.4.1 eq. (3.68) (rise time); Åström & Murray §9.5, pp. 9-27–9-28 (PI by pole/zero cancellation); §11.4, pp. 11-15–11-17 (windup and anti-windup); VESC PI form and gains in 04_model/params/motor_params.m

## Part 4 · From model to data {#p4}

:::q id=d1 kind=calc
One steady sample from your CAN log: **erpm = 12 000, I_motor = 8.0 A, duty = 0.735, V_in = 50.6 V**. Compute |v|, ωe, vd, vq and λm. Then two lines: why is one sample not a measurement of λm, and which samples must your script throw away?
key:
- |v| = duty·V_in/√3 = 0.735 × 50.6 / 1.732 ≈ 21.47 V (peak phase, amplitude-invariant)
- ωe = 12 000 × 2π/60 ≈ 1257 rad/s (erpm is already electrical: no × p)
- vd = −ωe·Lq·I ≈ −1.13 V; vq = √(21.47² − 1.13²) ≈ 21.44 V; λm = (vq − Rs·I)/ωe = (21.44 − 0.22)/1257 ≈ 16.9 mWb (+0.2 % vs 16.855)
- one sample carries frame-time mismatch (V_in in another frame), quantisation and possible transient: you need many steady samples, a median and a spread
- discard: I_motor exactly 0.0 (motor released, duty is no longer the commanded voltage; reads 6–20 % low), accelerating samples (L·di/dt, read high), low erpm (poor voltage resolution)
traps:
- multiplying erpm by 3 (λm ≈ 5.6 mWb) or dividing it by 3 (≈ 50.7 mWb): electrical vs mechanical
- Vbus/2 instead of Vbus/√3 (≈ 14.6 mWb)
- claiming 0.2 % agreement from one point when the log's spread is ±5 %
solution:
|v| = 21.47 V, ωe = 1257 rad/s, vd = −1.13 V, vq = 21.44 V, λm = (21.44 − 0.22)/1257 ≈ 16.9 mWb, 0.2 % above the scope. Lucky, not proof: log_017's steady samples spread ±5 %. The script keeps only current-controlled (I ≠ 0), quasi-steady samples above ~2000 erpm and reports a count, a median and a 10–90 % band, or no number if there are too few.
:::

:::q id=d2 kind=case
A colleague drafts your C03 gate: **"REQ-MOD-001: The motor model shall be accurate and shall be validated against the CAN logs."** Rewrite it so that C04 can pass or fail it. Then say what makes your version verifiable, and whether passing it means the motor model is validated.
key:
- a need in one line: the model must predict torque per amp (Kt ∝ λm) well enough to design the current loop and the vehicle model
- one quantity, a number, a range and conditions: e.g. back-EMF constant within ±3 % (median of ≥ 50 samples) of λm estimated from CAN, 1000–4900 rpm mechanical, steady speed, id = 0, |I| ≥ 1 A
- independent data: a recording not used to set the parameter; tolerance justified both ways (wider than what the data resolve, tighter than what the use needs)
- verification method named: lambda_from_can.py after passing its synthetic acceptance test, on a steady-hold log, result in the verification matrix
- passing it verifies one parameter at light load; it is one step towards validation, not validation of the whole model
traps:
- "accurate" and "validated" with no number (his mistake #13 and #14 pattern)
- a tolerance tighter than the log can show (±0.2 % from ±5 %)
- checking against the same log used to tune λm
solution:
Example. Need: the model must predict torque per amp within 5 % for loop and vehicle design. "REQ-MOD-001: over 1000–4900 rpm mechanical, at steady speed with id = 0 and |I| ≥ 1 A, the model's λm shall agree with λm estimated from a VESC CAN recording not used to set it, within ±3 % (median of at least 50 samples)." Verified by lambda_from_can.py, once its synthetic test passes, on a steady-hold log in C04. Passing it verifies one parameter at light load: a step towards validating the model, not the validation itself.
:::

src: 04_model/params/motor_params.m (λm by scope 16.855 mWb, no-load telemetry route, |v_dq| = duty·Vbus/√3); C03-LM (log_017 result, ±5 % spread)

## Part 5 · Judgement {#p5}

:::q id=e1 kind=case
Quad on the stand, brake fully on, rotor locked. You switch the VESC to **duty mode** and hold **duty = 0.05**. What phase voltage, current and torque do you get, cold and with the winding 25 % hotter? How much battery current? Then you release the brake: what happens to the current as the wheel spins up? Compare with asking 50 A in current mode.
key:
- phase voltage ≈ 0.05 × 52/√3 ≈ 1.50 V; cold I = 1.50/0.028 ≈ 54 A (≈ 4.1 N·m), hot ≈ 43 A (≈ 3.2 N·m): voltage fixes the current only through R
- battery: 1.5 × 1.50 × 54 ≈ 121 W → ≈ 2.3 A at 52 V; all of it heat in the copper
- brake released: back-EMF grows with speed, I = (V − E)/R falls, the motor settles where E ≈ 1.5 V (≈ 280 rpm) with only the drag current
- current mode: 50 A whatever the temperature, the loop raises the voltage as E grows until it runs out of volts
traps:
- "54 A in the phases means 54 A (or 3 × 54) from the battery" (his mistake #3)
- "the current stays the same when the wheel turns" in duty mode (his mistake #15)
- forgetting that at standstill all power is copper heat: keep it short
solution:
Duty 0.05 is about 1.5 V on each phase. Locked, only R limits the current: 54 A cold (4.1 N·m), 43 A hot. The battery gives just 121 W, 2.3 A. Let the brake go and the back-EMF rises with speed, so the current falls until E nearly equals 1.5 V, around 280 rpm, with just enough current for the drag. In current mode the VESC would hold 50 A as long as it had voltage over the back-EMF: the throttle, not R or speed, would decide.
:::

:::q id=e2 kind=case
At 4000 rpm the torque response feels slow. You want to switch on **decoupling** (feed-forward of ωe·λm and ωe·L·i) in VESC Tool. Before you do: what error does the feed-forward itself carry if the configuration holds the λm from one detection session (15.919 mWb), in volts? What does the PI do with it? What would you check, and with which number, before and after the change?
key:
- feed-forward error at 4000 rpm = ωe·(16.855 − 15.919) mWb = 1257 × 0.936 mWb ≈ 1.18 V of 21.2 V (5.5 %)
- the integrator clears a constant error, so the steady state is fine; but the feed-forward is only as good as ωe, L and λm, and a wrong one injects a disturbance in transients
- benefit expected from the model: rise ≈ 3.3 ms → ≈ 1.1 ms at 4000 rpm
- before: a requirement (which response time, why), a measured baseline (step response of iq in a log), λm checked against the measured 16.855 (detection moves 15.9–17.0 mWb between sessions); after: the same test, same conditions, compare with the number
traps:
- "always enable it" with no number
- changing two things at once (λm and decoupling) and not knowing which helped
- calling the result validation when it is a verification against your own requirement (his mistake #13)
solution:
With the VESC's λm the feed-forward is 1.18 V short at 4000 rpm. The integrator removes that in steady state, so it is not dangerous, but it shows the catch: feed-forward trusts the parameters. Your model says decoupling should take the step from about 3.3 ms back to 1.1 ms. So: write what response the quad needs and why, log a baseline step, fix λm first (one change at a time), then enable decoupling and repeat the same test.
:::

:::q id=e3 kind=error
A colleague explains your VESC: "The current loop runs at 30 kHz, so its bandwidth is 30 kHz. Because Ki/Kp = R/L, it has that bandwidth at every speed. Windup happens when the battery limit is hit, and you fix it by raising Ki. At 5000 rpm full throttle the motor gets 120 A, because the current limit is 120 A." Find every error.
key:
- sampling rate is not bandwidth: ωc = 2000 rad/s ≈ 318 Hz, about 1/47 of a 15 kHz loop; the sample delay caps how high it can go
- pole/zero cancellation gives 2000 rad/s only for the bare R-L plant: at speed, without decoupling, cross-coupling makes the step ~3× slower (≈ 3.3 ms at 4000 rpm)
- windup comes from the voltage saturation (30 V wall), not the battery limit; the fix is clamping or back-calculation; a larger Ki winds up faster
- at 5000 rpm the voltage, not the 120 A limit, caps the current: the back-EMF eats most of the 30 V and only tens of amps fit
traps:
- accepting "bandwidth = PWM frequency"
- "Ki/Kp = R/L makes the loop speed-independent"
- missing that the last claim is the voltage wall from L3b
solution:
Four errors. (1) 30 kHz (or 15 kHz) is how often the loop runs; its bandwidth is 2000 rad/s, 318 Hz. (2) The cancellation design assumes R-L alone; at 4000 rpm without decoupling the step is about three times slower. (3) Windup is the integrator charging while the voltage is saturated; clamping fixes it, a larger Ki makes it worse. (4) At 5000 rpm the back-EMF leaves little voltage, so the current falls far below 120 A: the voltage wall, not the current limit.
:::

src: Åström & Murray §9.5, pp. 9-27–9-28 (slow disturbance response of a cancellation design); §11.4, pp. 11-15–11-17; Hughes §9.5.2, p. 345 (voltage sets base speed)

## Close {#close}

:::q id=z0 kind=explain
An interviewer asks: "How does your VESC control torque, and what limits it?" In at most 6 lines: Park and dq, the current loop and how it is tuned, and the three walls.
key:
- Park with the rotor angle turns 3 phase sines into two constants: iq makes torque (Kt = 0.0758 N·m/A), id is held at 0 (FW and MTPA off, saliency gives only +0.5 %)
- each axis is an R-L plant (τ ≈ 4 ms) plus back-EMF and cross-coupling; two PIs tuned by pole/zero cancellation, Kp = ωc·L, Ki = ωc·Rs, ωc = 2000 rad/s (Kp 0.2119, Ki 56.2), rise ≈ 1.1 ms at standstill, slower at speed without decoupling
- walls: 120 A current circle (launch torque 9.1 N·m), 40 A battery = power (~2.1 kW, from ~11 km/h), voltage ellipse Vmax/ωe (top speed ~37 km/h, scales with bus)
- on the voltage wall the loop is saturated and needs anti-windup
traps:
- "the inverter manages the current" with no mechanism
- leaving out the limits or the tuning rule
solution:
The VESC measures two phase currents, Clarke and Park them with the rotor angle, and gets two constants: iq for torque, 0.0758 N·m per amp, and id, held at zero because my saliency gives MTPA only 0.5 %. Each axis is an R-L of about 4 ms plus back-EMF and coupling; two PIs tuned by pole/zero cancellation give 2000 rad/s, a 1.1 ms rise at standstill, slower at speed because decoupling is off. Three walls: 120 A of current at launch, 40 A of battery (a 2.1 kW power limit) from about 11 km/h, and the 30 V voltage ceiling at top speed, where the loop saturates and needs anti-windup.
:::

:::q id=z1 kind=doubt
What is still unclear after the exam? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
