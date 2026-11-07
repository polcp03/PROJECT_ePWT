---
id: C03-K2
cycle: C03
title: "Control 2: the PI, error and bandwidth"
date: 2026-11-06
slot: 1
minutes: 55
lede: In K1 a P controller on your phase left an error, and at speed it could even drive the current backwards. Today you add the integral, cancel your motor's own time constant with it, and find out how fast the loop may go before the 30 kHz sampling and the 30 V wall stop you. At the end you read your VESC's gains and see that it did exactly this.
sources: Franklin, Powell & Emami-Naeini, Feedback Control of Dynamic Systems, 8th ed. (ebook, no printed page numbers) §4.3.2 eqs. 4.62–4.69, §4.3.4 eqs. 4.72–4.73 and Example 4.5, §4.5, §8.5.1–8.5.2 · Åström & Murray, Feedback Systems, 2nd ed. §11.1 pp. 11-3–11-4 (eq. 11.4), §11.4 pp. 11-15–11-18 (figs. 11.10–11.11), §11.5 pp. 11-21–11-22 (eq. 11.17) · VESC firmware in 03_hardware/vesc/_firmware: motor/mcpwm_foc.c lines 4639–4695, conf_general.c line 1513 · 04_model/params/motor_params.m
---

## Predict {#predict}

Two from your open mistakes first, from memory. Then two guesses about today, with your reason.

:::q id=r1 kind=recall
Your VESC runs its PWM at 30 kHz. When you open the throttle, what does the VESC change in the PWM, and what stays fixed? And roughly how many times per second can it measure the current and correct the voltage?
key:
- it changes the duty cycle (the fraction of each period a switch is on); the frequency stays fixed at 30 kHz (foc_f_zv)
- the current loop runs once per PWM period or once every two: 30 000 or 15 000 times a second (which one is still OPEN for his FSESC)
- so the loop can never react faster than one period, 33 or 67 µs
traps:
- "it changes the frequency" (his mistake #5)
- assuming the loop runs faster than the PWM
solution:
The duty cycle changes; the 30 kHz stays. The VESC measures and corrects once per PWM period or once every two, so 30 000 or 15 000 times a second. Which of the two your FSESC does is still open in motor_params.m. Today that number becomes the ceiling on how fast your current loop can be.
:::

:::q id=r2 kind=recall
Fixed voltage on a DC motor, the quad starts climbing a hill and slows down. What happens to the current, and with which equation?
key:
- I = (V − E)/R: the speed drops, so the back-EMF E drops, so the current rises
- this is voltage mode; his VESC is in current mode, where the current loop forces the current
- the back-EMF is something the current loop has to fight: today it is the "disturbance" the integral removes
traps:
- "current and torque stay the same" (his mistake #15)
solution:
With fixed V, I = (V − E)/R. Slower means less E, so more current. That is voltage mode. Your VESC is in current mode: its loop holds the current, and to do it it must produce exactly the volts the back-EMF eats. Today you see which part of the controller does that.
:::

:::q id=p1 kind=predict
A controller term adds up the error over time: u = Ki·∫e dt. The error has been exactly zero for a full second. What is that term's output now: zero, or something else? Why?
key:
- not necessarily zero: it holds whatever it accumulated before, the area under the past error
- that held value is what lets the loop give a non-zero voltage with zero error
solution:
Not zero. The integral holds the area of all the error it saw before. With zero error it stops changing but keeps its value. That is the whole trick of today: a constant output with zero error.
:::

:::q id=p2 kind=predict
In a PI, u = Kp·e + Ki·∫e dt. Which of the two gains do you think sets how fast the current follows a step, and which one only removes the leftover error? Guess and say why.
key:
- Kp sets the speed (for his R-L phase, bandwidth ≈ Kp/L)
- Ki, set right, only removes the steady error and should cancel the plant's slow pole; raising it mostly adds overshoot
solution:
Kp sets the speed: for your phase the loop bandwidth is about Kp/L. Ki, chosen well, cancels the motor's slow pole and removes the leftover error; pushing it higher buys overshoot more than speed. You will prove both today.
:::

## Core: six ideas on your motor {#core}

Each idea starts from your phase or your VESC, then the law.

### Why the integral: the back-EMF and the hot copper never go away

From K1: your q-axis phase is an R-L circuit, Rs = 28.02 mΩ and Lq = 112.8 µH, τ = Lq/Rs ≈ 4.0 ms. A P controller sets v = Kp·(i_ref − i). It needs an error to make any voltage at all, so in steady state there is always an error left.

Two things make it worse on your quad:

- **Back-EMF.** At 4000 rpm the magnet puts 21.2 V against you on the q axis (decoupling off: nobody subtracts it). A P controller only makes that voltage out of error.
- **Resistance drift.** Your Rs is measured once, cold or at an unknown temperature. Copper rises 0.39 %/K, so a hot motor can be 20–30 % above it, and `foc_temp_comp = 0`.

Integral action fixes both. Åström and Murray give the general argument: if the loop settles at all, the integral can only be finite if the error is zero. It does not need to know R, L or the back-EMF. Franklin shows the same with the final value theorem: integral control rejects a constant disturbance exactly and is robust to plant changes.

= P only, steady state:  i = (Kp·i_ref − ωe·λm) / (Rs + Kp)

:::q id=i1 kind=calc
Use a P controller with Kp = 0.2119 V/A (your VESC's proportional gain) and ask for 40 A on q. Compute the steady current (a) at standstill and (b) at 4000 rpm, with no back-EMF feedforward. What does (b) mean on the quad?
key:
- (a) i = 0.2119·40 / (0.02802 + 0.2119) = 35.3 A, an 11.7 % error
- (b) ωe·λm = 1257 × 0.016855 = 21.18 V; i = (8.48 − 21.18)/0.2399 = −53 A
- (b) the current goes negative: the motor brakes while you ask for drive torque
- an integrator removes both errors without knowing R or λm
traps:
- forgetting the back-EMF (treating 4000 rpm like standstill)
- using mechanical speed, 419 rad/s, instead of ωe = 1257 rad/s
solution:
(a) 0.2119 × 40 / 0.2399 = 35.3 A: almost 12 % short. (b) The back-EMF is 21.18 V and the controller makes only 8.48 V from a 40 A error, so the current ends at (8.48 − 21.18)/0.2399 = −53 A. You ask for drive and get braking. No real P gain fixes this. An integrator does: it keeps adding volts until the error is zero, whatever R and λm are.
:::

src: Åström & Murray §11.1, pp. 11-3–11-4 (the "magic of integral action": zero error whenever a steady state exists); Franklin §4.3.2, eqs. 4.62–4.69 (integral control, constant-disturbance rejection, robustness)

### The PI: Kp + Ki/s, and the zero it carries

Your VESC's current controller is, in its own source (`mcpwm_foc.c`, line 4639 on):

= v_int += err·ki·dt     v = v_int + err·kp

That is the parallel PI. In Laplace form:

= C(s) = Kp + Ki/s = Kp·(s + Ki/Kp) / s

Two things are hidden in that rewrite. The **pole at s = 0** is the integrator: infinite gain at DC, so no steady error. The **zero at s = −Ki/Kp** is a frequency, in rad/s. Below it the controller acts like an integrator; above it, like a plain gain Kp. Its inverse, Ti = Kp/Ki, is the integral time. You choose where that zero sits, and the next idea tells you where.

In steady state at speed, the error is zero, so the whole voltage comes from v_int. The integrator is the part that "learns" the back-EMF.

:::q id=i2 kind=calc
Your VESC's gains: kp = 0.2119 V/A, ki = 56.20 V/(A·s). (a) Where is the PI zero, in rad/s, and what is Ti? Compare it with your q-axis R/L. (b) At 4000 rpm, steady, iq = 40 A, id = 0: how many volts does the q integrator hold?
key:
- (a) zero at Ki/Kp = 56.20/0.2119 = 265 rad/s; Ti = 3.77 ms
- (a) q-axis plant pole R/Lq = 0.02802/112.77 µH = 248 rad/s (τ = 4.02 ms): the zero sits almost on it
- (b) error zero, so vq = v_int = Rs·iq + ωe·λm = 1.12 + 21.18 = 22.30 V
- the integrator holds the back-EMF because decoupling is off
traps:
- giving the zero in Hz without saying so (265 rad/s = 42 Hz)
- thinking Kp·e makes the steady voltage (e = 0 in steady state)
solution:
(a) Zero at 265 rad/s, Ti = 3.77 ms, against a plant pole at 248 rad/s (τ = 4.02 ms). Not a coincidence: next idea. (b) In steady state e = 0, so the proportional term is zero and the integrator carries all 22.30 V, 21.18 of them back-EMF. With decoupling off, that is its job.
:::

src: Franklin §4.3.4, eqs. 4.72–4.73 (PI in time and Laplace form); Åström & Murray §11.1, eq. 11.4, p. 11-4; VESC mcpwm_foc.c lines 4639–4644

### Cancel your motor's pole: Ki/Kp = R/L, bandwidth ωc = Kp/L

Put the PI in front of your phase:

= loop gain  C(s)·G(s) = Kp·(s + Ki/Kp)/s · 1/(L·s + R) = (Kp/L)·(s + Ki/Kp) / [ s·(s + R/L) ]

If you place the zero exactly on the plant pole, Ki/Kp = R/L, the two cancel:

= Ki/Kp = R/L   →   C·G = Kp / (L·s)

What is left is a pure integrator. Closing the loop gives a first-order response with one pole at −Kp/L:

= i/i_ref = 1 / (1 + s·L/Kp)    ωc = Kp/L    rise 10–90 % = ln 9 / ωc ≈ 2.2/ωc

So design is two lines: pick the bandwidth ωc, then **Kp = ωc·L** and **Ki = ωc·R**. No overshoot, no leftover error, and the response does not depend on the step size while the voltage does not saturate. Franklin's Example 4.5 does the same thing on a thermal plant: the PI zero cancels the slow pole.

> Cancellation is only as good as your R and L. Hot copper moves R; current moves L (your Lq − Ld was measured at 40 A). A mismatch leaves a small slow tail, which the integrator still removes, just slowly.

:::q id=i3 kind=calc
You want ωc = 3000 rad/s on your q axis. Compute Kp and Ki, and predict the 10–90 % rise time of a current step. Then: the motor is hot and Rs is 25 % higher than you designed for. Does the current still reach the reference? What changes?
key:
- Kp = 3000 × 112.77 µH = 0.338 V/A; Ki = 3000 × 0.02802 = 84.1 V/(A·s)
- rise 10–90 % = 2.197/3000 = 0.73 ms
- hot: the zero no longer sits on the pole (248 vs 311 rad/s); the response gets a small slow tail, about 1 % short after 5 ms at ωc = 2000, but the integrator still brings the error to zero
- what does not change: zero steady error (integral action does not need R)
traps:
- Ki = ωc·L or Kp = ωc·R (swapped)
- "a hot motor gives a steady current error": not with an integrator
- using Ld (99 µH) for the q loop
solution:
Kp = 0.338 V/A, Ki = 84.1 V/(A·s), rise ≈ 0.73 ms. Hot motor: R/L is now 311 instead of 248 rad/s, so the cancellation is off. The loop gets a slow tail: at ωc = 2000 the step is still about 1 % short after 5 ms and the rise stretches from 1.10 to 1.20 ms. But it gets there: the integrator does not care what R is. Mismatch costs shape, not accuracy.
:::

src: Franklin §4.3.4, Example 4.5 (the PI zero cancels the plant pole, closed loop simpler)

### How fast can it be: sampling and delay set the ceiling

Formula says: any ωc you like, just raise Kp. Your VESC says no. It measures the current once per control period Ts, computes, and the new voltage only reaches the motor at the next PWM update. That is a delay of about one and a half periods (computing, then the hold until the next update). A delay of Td costs ωc·Td of phase at the crossover, and your integrator loop starts with 90° of phase margin:

= phase margin ≈ 90° − ωc·1.5·Ts (in degrees: × 180/π)

Franklin's rule for sample-rate selection: sample 20 to 40 times faster than the closed-loop bandwidth for a smooth response, about 25 times for disturbance rejection. Turned around, with ωs = 2π/Ts:

= ωc ≤ ωs/20 (comfortable) … ωs/10 (aggressive)

> Your control period is OPEN in motor_params.m: Ts = 66.7 µs (15 kHz, assumed, with phase shunts and sample mode V0) or 33.3 µs (30 kHz). Until it is confirmed on the device, design for the slower one.

:::q id=i4 kind=calc
Compute the bandwidth ceiling ωs/10 and ωs/20 for a 30 kHz loop and for a 15 kHz loop, in rad/s and Hz. Which one do you design with today, and why? Then estimate the phase margin your VESC's ~2000 rad/s loop has at 15 kHz.
key:
- 30 kHz: ωs = 188 500 rad/s; ωs/20 = 9425 rad/s (1500 Hz), ωs/10 = 18 850 rad/s (3000 Hz)
- 15 kHz: ωs = 94 250 rad/s; ωs/20 = 4712 rad/s (750 Hz), ωs/10 = 9425 rad/s (1500 Hz)
- design ceiling today: about 4700 rad/s (15 kHz, ωs/20), because the control period is still open: take the slower one
- VESC at 2000 rad/s, Ts = 66.7 µs: lag ≈ 2000 × 1.5 × 66.7 µs = 0.20 rad = 11.5°, phase margin ≈ 78°; comfortable
traps:
- mixing Hz and rad/s (ωs = 2π·f)
- taking the PWM frequency as the loop rate without checking the open item
- "faster is always better": delay eats phase margin
solution:
30 kHz: ceiling 9425 rad/s (comfortable) to 18 850 rad/s. 15 kHz: 4712 to 9425 rad/s. Since the period is open, design for 15 kHz and ωs/20: about 4700 rad/s, 750 Hz. Your VESC sits at about 2000 rad/s, well inside, and its delay costs only about 11° at 15 kHz: phase margin near 78°. At 9425 rad/s on a 15 kHz loop the same estimate drops to about 36°: ringing.
:::

src: Franklin §8.5.1–8.5.2 (sample rate 20–40× the bandwidth for tracking, about 25× for disturbance rejection; a faster rate reduces the delay); §4.5 (digital controllers approximate the continuous one); Åström & Murray §11.5, pp. 11-21–11-22 (computer implementation, latency)

### 30 V is the wall: saturation, windup, anti-windup

Your inverter cannot give more than Vbus/√3 ≈ 30 V of vector length; the VESC keeps a margin with max duty 0.95, so it clamps at about 28.5 V (`mcpwm_foc.c`, line 4684). Any time the PI asks for more, the motor gets 28.5 V and the error stays large longer.

The proportional part is harmless: it drops as soon as the error drops. The integral part is the problem. While the voltage is clamped, the error keeps feeding the integrator, which grows far past anything the inverter can give. When the error finally changes sign, the integrator must first unwind all that extra before the voltage comes off the limit: the current overshoots. That is **windup**. Åström and Murray show it on a cruise control on a steep hill.

The cure, **anti-windup**: stop the integrator from growing while the output is saturated. Åström and Murray feed the difference between the asked and the applied output back into the integrator. Your VESC uses the simplest form: it clamps the integrator itself to the same voltage limit (`vd_int`, `vq_int` truncated at lines 4686–4695), with the d axis served first.

:::q id=i5 kind=check
Quad on the stand, wheels in the air, motor at the duty ceiling. You hold full throttle asking 100 A but only 5 A flow, for 3 s. (a) Without anti-windup, how many volts would the q integrator ask for, with ki = 56.20? (b) What happens when you put the wheels on the ground and the speed drops? (c) What does your VESC do instead?
key:
- (a) the error is about 95 A for 3 s: 95 × 56.20 × 3 ≈ 16 000 V asked, against 28.5 V available
- (b) when the speed drops the back-EMF falls and the current rises, but the integrator still asks thousands of volts: the voltage stays at the limit until it unwinds, so the current overshoots the 100 A request (limited only by l_current_max 120 A and l_abs_current_max 160 A)
- (c) the VESC clamps vq_int to the available voltage (about 28.5 V at 52 V), so it never stores more than the inverter can give and comes off the limit as soon as the error turns
- the 40 A battery limit still caps battery current; it does not stop a phase-current overshoot
traps:
- "the voltage is limited, so there is no problem": the stored integral is the problem, not the output
- confusing the integrator clamp with the current limits
solution:
(a) 95 A × 56.2 × 3 s ≈ 16 000 V of "demand" for an inverter that has 28.5 V. (b) When the wheels load up, speed and back-EMF fall and current rises fast, but the integrator would need ages to unwind 16 000 V: the voltage sits at the limit and the current shoots past 100 A until the current limits or the unwinding stop it. (c) Your VESC clamps the integrator at the voltage limit, so it holds at most about 28.5 V and reacts the moment the error changes sign.
:::

src: Åström & Murray §11.4, pp. 11-15–11-18 (integrator windup, fig. 11.10 cruise control on a hill, fig. 11.11 anti-windup by feeding back the saturation error); §11.5, eq. 11.17, p. 11-22; Franklin §4.3.2 (anti-windup needed whenever the actuator can saturate); VESC mcpwm_foc.c lines 4684–4695

### Your VESC's own gains: it did exactly this

Your device, after the 2026-09-07 detections (`motor_params.m`): **kp = 0.2119 V/A, ki = 56.20 V/(A·s)**. The firmware computes them in `conf_general_calc_apply_foc_cc_kp_ki_gain()` (conf_general.c, line 1513):

= bw = 1/tc    kp = L·bw    ki = R·bw

That is the cancellation rule of idea 3. Divide back: kp/L = 0.2119/106.0 µH = 1999 rad/s and ki/R = 56.20/0.02802 = 2006 rad/s. So VESC Tool chose tc = 500 µs, ωc = 2000 rad/s, 318 Hz.

One detail: the VESC uses the **average** L = 106 µH (its `foc_motor_l`), and the same gains on d and q. On your q axis (Lq = 112.8 µH) the bandwidth is really kp/Lq = 1879 rad/s; on d (Ld = 99.2 µH) it is 2135 rad/s. The zero, 265 rad/s, sits between the two plant poles, 248 (q) and 282 (d). Near enough: on q the mismatch gives only about 0.4 % overshoot.

> The XML export in `03_hardware/vesc/MOTOR_1.9.xml` has older values, kp 0.102 and ki 18.83 (R 18.8 mΩ, L 102 µH, bw 1000 rad/s). They follow the same rule; they are not what motor_params.m records on the device now. Read the live values in VESC Tool before trusting either.

:::q id=i6 kind=check
You are in VESC Tool, connected to the quad. How do you confirm which current gains are really on the device, and how would you check, with a number, that the loop has the bandwidth you think? Give the pass criterion.
key:
- read foc_current_kp and foc_current_ki in the motor's FOC settings (live, not the old XML); compute kp/L and ki/R: both should give about 2000 rad/s
- check the ratio ki/kp ≈ R/L (265 vs 248–282 rad/s)
- verification: rotor held (no back-EMF), a small iq step (e.g. 0 → 20 A, short, current limit set), log iq at the full sample rate, measure the 10–90 % rise
- pass criterion with a number: rise ≈ 2.2/1879 = 1.17 ms on q (say within ±20 %), overshoot below a few %, zero error after about 5 ms
- a plot that "looks fine" is not a criterion (his mistake #12)
traps:
- trusting the XML file in the repo as the device state
- "it works when I ride, so the gains are right": plausible is not verified
solution:
Read kp and ki live in VESC Tool (Motor Settings, FOC), not from the old XML. Check kp/L ≈ ki/R ≈ 2000 rad/s. Then verify: rotor held, current limit set, a short 0 → 20 A step on iq, logged fast. Pass if the 10–90 % rise is about 1.17 ms (±20 %), overshoot under a few percent and no error left after about 5 ms. That number is what you write in the verification matrix, not "it looked fine".
:::

src: VESC firmware conf_general.c line 1513 (kp = L·bw, ki = R·bw); motor_params.m section 3 (device gains, three detections, bw = 2000 rad/s cross-checked)

## Lab: touch it {#lab}

Write your prediction before you move a slider. The lab holds the rotor still (no back-EMF), samples at 30 kHz and applies each voltage one period late, like the VESC.

:::lab piloop
Closing the current loop
:::

:::q id=l1 kind=lab
Press "Cancel the pole" and set Kp to 0.226 V/A (that is 2000 rad/s × Lq). Predict the 10–90 % rise time and the overshoot for a 60 A step, then read them. Now double Kp (keep cancelling): predict again. Then press "Your VESC's gains" and say why its dashed trace is a little slower than yours.
key:
- Kp = 0.226: predicted 2.2/2000 = 1.10 ms, no overshoot; the lab reads about 1.0 ms (the discrete loop differs slightly from the formula)
- Kp doubled (0.45 V/A, ωc 4000 rad/s): rise about halves (formula 0.55 ms, lab about 0.43 ms), still no overshoot
- the VESC's kp was computed with L = 106 µH, so on Lq = 113 µH its bandwidth is about 1880 rad/s: slightly slower (lab about 1.07 ms)
- the error at the end of the window is zero in all three
traps:
- expecting overshoot from a higher Kp: with cancellation the loop is first order
solution:
With cancellation the loop is first order: 1.10 ms predicted, about 1.0 ms in the lab, no overshoot. Double Kp and the rise roughly halves, still no overshoot. The VESC's trace is a bit slower because it sized kp with the average L, 106 µH, not Lq: about 1880 rad/s on your q axis.
:::

:::q id=l2 kind=lab
Keep cancelling, set Kp ≈ 1 V/A and a 100 A step. Predict first: what does the voltage trace do in the first samples, and why? Then switch anti-windup off and compare the current overshoot. Why is the difference small here but huge in the wheels-in-air case of idea 5?
key:
- the first voltage asked is Kp·100 = 100 V: it clamps at 30 V, so the start is a voltage-limited ramp, not the first-order curve
- with anti-windup on: almost no overshoot; off: about 3–4 % overshoot
- small here because the voltage is saturated only for a few hundred microseconds, so the integrator stores little; with the wheels in the air it saturates for seconds
- 1 V/A is about 8900 rad/s, far beyond the 4700 rad/s design ceiling: the lab's 30 kHz loop tolerates it; a 15 kHz loop would ring
traps:
- reading the voltage-limited ramp as "the loop is slow"
solution:
Kp·100 A asks 100 V, so the voltage sits at the 30 V limit and the current ramps at the rate the voltage allows. Anti-windup off adds about 3–4 % overshoot: the integrator only wound up during a short saturation. In the wheels-in-air case it winds for seconds and the overshoot is no longer small. And note that 1 V/A is about 8900 rad/s, above your 4700 rad/s ceiling.
:::

## Judgement {#judgement}

Reason from what you know is true, not from what sounds familiar.

:::q id=c1 kind=case
You ride at 4000 rpm with almost no throttle (iq ≈ 0) and then snap the throttle to ask 60 A. Your VESC's gains, decoupling off. What voltage does the q-axis PI ask for in the first sample, does it fit, and what do you see in the current? What could make this transient cleaner?
key:
- the q integrator already holds about the back-EMF, 21.18 V; the proportional kick adds 0.2119 × 60 = 12.7 V: about 33.9 V asked
- the limit is about 28.5 V (Vbus/√3 × 0.95 duty), so it saturates: the first part of the rise is voltage-limited, slower than the 1.17 ms of the linear loop
- anti-windup (the VESC's integrator clamp) keeps it from overshooting after
- at the end vq ≈ 22.86 V and vd ≈ −8.5 V (cross-coupling): |v| ≈ 24.4 V, inside the limit, so the 60 A is reachable at this speed
- cleaner: a rate limit on the iq request (VESC ramping), or back-EMF feedforward plus a smaller step
traps:
- forgetting the integrator already holds the back-EMF
- checking only the steady state and not the first sample
- forgetting vd from cross-coupling in |v|
solution:
The integrator already holds about 21.2 V of back-EMF; the 60 A error adds 12.7 V. It asks 33.9 V against about 28.5 V available, so the start is voltage-limited and slower than 1.17 ms. The clamp on the integrator stops an overshoot later. In steady state it fits: vq ≈ 22.9 V, vd ≈ −8.5 V, |v| ≈ 24.4 V. A ramped request avoids the saturation altogether.
:::

:::q id=c2 kind=error
A colleague: "A PI is old school. Add a D term and make it a PID: the derivative anticipates the error, so your current loop will be faster." Where is he wrong for your motor?
key:
- the plant is first order (1/(L·s + R)): PI with cancellation already gives a clean first-order loop; the VESC source says the same (no D needed for a first-order plant)
- speed is set by Kp/L and capped by sampling and delay (≈ 4700 rad/s at 15 kHz), not by a missing D
- a derivative amplifies noise, and phase current measured next to 30 kHz switching is noisy
- D does not help with the real limits: the 30 V wall and the one-and-a-half-period delay
traps:
- "derivative always adds phase margin, so more is better"
solution:
Your phase is first order, so a PI that cancels its pole already makes the loop a clean first-order response; the VESC firmware's own comment says no D is needed for that reason. What caps speed is the sampling delay and the 30 V wall, and a D term fixes neither. It does amplify the measurement noise next to 30 kHz switching. Speed comes from Kp, up to the ceiling.
:::

## Close {#close}

:::q id=z0 kind=explain
Explain it as you would to an interviewer, in at most 5 lines: why your current loop needs an integral, how you would choose Kp and Ki for your motor, and what limits how fast you can make it.
key:
- integral: zero steady error against back-EMF (21 V at 4000 rpm, decoupling off) and resistance drift, without knowing them
- cancellation: Ki/Kp = R/L leaves Kp/(L·s); ωc = Kp/L; so Kp = ωc·L, Ki = ωc·R; VESC: 2000 rad/s (kp 0.2119, ki 56.20)
- ceiling: sampling and delay, ωc ≤ ωs/20, about 4700 rad/s at 15 kHz (control period still open)
- 30 V saturation and windup; the VESC clamps its integrators
solution:
A P controller needs an error to make voltage, so against 21 V of back-EMF and drifting resistance it never gets there; the integral removes the error without knowing either. I put the PI zero on the motor's pole, Ki/Kp = R/L, which leaves a pure integrator and a first-order loop with bandwidth Kp/L: Kp = ωc·L, Ki = ωc·R. My VESC did exactly that at 2000 rad/s. The ceiling is sampling and delay, about 4700 rad/s for a 15 kHz loop, and the 30 V limit, where the integrator must be clamped against windup.
:::

:::q id=z1 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
