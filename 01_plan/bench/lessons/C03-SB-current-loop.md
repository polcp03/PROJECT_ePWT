---
id: C03-SB
cycle: C03
title: Simulink B: close the current loop
date: 2026-11-11
slot: 1
minutes: 60
lede: Yesterday your model needed you to hold the voltages by hand. Today two PI controllers do it, with the gains you calculated on 6 November, a 30 V wall from your 52 V bus, and a step to 60 A. Then the rotor spins, and you find out what your hand prediction forgot.
sources: 04_model/params/motor_params.m (VESC PI form and gains, mcpwm_foc.c as quoted there) · Åström & Murray, Feedback Systems 2e, §9.5 pp. 9-27–9-28 (PI by pole/zero cancellation and its slow disturbance response), §11.4 pp. 11-15–11-17 (integral windup and anti-windup) · Franklin, Powell & Emami-Naeini 8e, §3.4.1, eq. (3.68) (rise time)
---

## Predict {#predict}

Write these before opening Simulink. Use the ωc and gains from your own X1 sheet (6 November).

:::q id=r1 kind=recall
From X1: write your Kp and Ki for the q axis and the d axis, the ωc you chose, and why Ki/Kp = Rs/L is a special choice.
key:
- Kp = ωc·L and Ki = ωc·Rs, per axis: q uses Lq = 112.77 µH, d uses Ld = 99.23 µH
- with ωc = 2000 rad/s (the VESC's own): Kp,q = 0.226 V/A, Kp,d = 0.198 V/A, Ki = 56.0 V/(A·s) on both
- Ki/Kp = Rs/L puts the PI zero exactly on the plant pole (pole/zero cancellation): the loop becomes ωc/s and the closed loop a first-order lag with bandwidth ωc
- the VESC uses exactly this rule (kp = L·bw, ki = R·bw, bw = 2000 rad/s, motor_params.m)
traps:
- using Lq on the d axis too (only a small error: 14 %, but say it)
- confusing ωc in rad/s with Hz (2000 rad/s = 318 Hz)
solution:
Kp = ωc·L, Ki = ωc·Rs. With ωc = 2000 rad/s: Kp,q = 0.226, Kp,d = 0.198 V/A, Ki = 56.0 V/(A·s). The PI zero at Ki/Kp = Rs/L cancels the plant pole, the open loop is ωc/s and the closed loop is a first-order lag with time constant 1/ωc = 0.5 ms. Your VESC runs the same rule (kp 0.2119, ki 56.2 with its averaged L).
:::

:::q id=p1 kind=predict
Rotor locked. Step iq_ref 0 → 60 A. Predict the 10–90 % rise time, the overshoot, and the largest vq the PI asks for. Will it hit the 30 V wall?
key:
- first-order closed loop: rise 10–90 % = ln 9 / ωc = 2.2/ωc = 1.10 ms at ωc = 2000 rad/s
- no overshoot (first order)
- largest vq at the instant of the step: Kp·60 = 0.226 × 60 = 13.5 V
- 13.5 V < 30 V: no saturation at standstill
traps:
- using the second-order rule 1.8/ωn: this loop is first order
- saying it saturates because 60 A "is a lot": compute Kp·error
solution:
tr = ln 9 / 2000 = 1.10 ms, no overshoot, and the peak voltage is Kp·60 = 13.5 V at t = 0+, then it falls to Rs·60 = 1.7 V. Far from 30 V.
:::

:::q id=p2 kind=predict
Same step at 4000 rpm, no decoupling (your VESC has `foc_cc_decoupling = DISABLED`). Will the rise time be the same as at standstill? Guess, with one reason.
key:
- no: slower, because the controller was designed for the R-L plant only
- the back-EMF (21.2 V) and the cross-coupling terms ωe·L·i are disturbances the PI has to fight
- pole/zero cancellation leaves the slow plant pole (Rs/Lq ≈ 250 rad/s, τ ≈ 4 ms) in the disturbance response
- also: vq now starts near 21 V, so Kp·60 = 13.5 V on top reaches 34.7 V, over the 30 V wall
traps:
- "same, the PI does not care about speed" (it does not, but the plant does)
solution:
Slower. The PI was tuned for R-L alone; at speed the plant also has the back-EMF and the cross-coupling ωe·L·i between the axes, and a cancellation design rejects disturbances only with the slow plant pole (τ ≈ 4 ms). And 21.2 V + 13.5 V = 34.7 V asks for more than the 30 V you have.
:::

## Build {#build}

Open yesterday's `models/pmsm_dq.slx` and **save as** `models/pmsm_dq_cl.slx` (keep A untouched as the open-loop reference). Gains go in a new block of `params/motor_params.m` or in a new `params/current_loop_params.m` (`cl.wc`, `cl.Kp_d`, `cl.Kp_q`, `cl.Ki`), tagged as your design, not CONFIG. Stop time 0.06 s.

### Two PI controllers in front of the plant

For each axis: error = i_ref − i (Sum), then a **PID Controller** block set to *PI*, *parallel form*, P = `cl.Kp_q` (or `cl.Kp_d`), I = `cl.Ki`, *continuous time*. Output is vq (or vd) into yesterday's plant. id_ref = 0 (a Constant); iq_ref is a Step 0 → 60 A at t = 0.03 s, so the loop has 30 ms to settle first.

= v = Kp·e + Ki·∫e dt    (the VESC form: v_int += e·Ki·dt; v = v_int + e·Kp)

src: motor_params.m, section 3 (VESC PI form, mcpwm_foc.c:4639–4644 as quoted there)

### The 30 V wall

With SVPWM the largest sine your 52 V bus can make is Vbus/√3 = 30.0 V peak phase. Model it with the PID block's *Output saturation*: upper 30, lower −30, on both axes. Leave *Anti-windup method* on **none** for now.

> Per-axis clamping is a simplification. The real limit is on the length of the voltage arrow, √(vd² + vq²) ≤ 30 V; the VESC limits the vector. Per axis, vd and vq can both be at 29 V and the arrow is 41 V, which the inverter cannot make. Note it; fix it only if time is left.

### Run the steps and measure

1. **Locked rotor** (`rpm_test = 0`): measure 10–90 % rise time of iq, overshoot, peak vq.
2. **4000 rpm**, same step. Same three numbers, plus the largest id excursion.
3. **5000 rpm**, same step: watch vq sitting on the 30 V wall and what iq does when it comes off.

Use the Data Inspector cursors for the 6 A and 54 A crossing times (10 % and 90 % of 60 A).

:::lab piloop
Closing the current loop
:::

### If time is left: anti-windup, then decoupling

**Anti-windup:** set the PID block's method to *clamping* (the integrator stops while the output is saturated) and rerun 5000 rpm.

**Decoupling:** add the feed-forward that the VESC leaves switched off. After each PI, add the term the plant will subtract:

= vd = PI_d − ωe·Lq·iq    vq = PI_q + ωe·(Ld·id + λm)

Rerun 4000 rpm. The PI now sees the bare R-L again.

src: Åström & Murray §11.4, pp. 11-15–11-17 (windup, clamping and back-calculation)

## Check {#check}

:::q id=k1 kind=check
Locked rotor: your rise time, overshoot and peak vq. Compare with your hand prediction.
key:
- rise 10–90 % ≈ 1.10 ms (ln 9 / ωc for ωc = 2000 rad/s; 2.2/ωc in general)
- no overshoot
- peak vq ≈ 13.5 V (Kp·60) at the step, falling to Rs·60 = 1.7 V; never saturated
- agreement with the hand value within a few % means the cancellation worked
traps:
- a rise time near 4 ms: Ki/Kp is not Rs/L, so the zero is not on the pole
- overshoot appearing: a gain typo, or Ld and Lq swapped between axes
solution:
About 1.10 ms, no overshoot, 13.5 V peak. The closed loop behaves like the first-order lag your X1 sheet predicted: the PI zero sits on the plant pole and the loop is ωc/s.
:::

:::q id=k2 kind=check
At 4000 rpm, no decoupling: rise time, overshoot, how long vq sat at 30 V, and the largest id. Why is it slower than at standstill? Is it the saturation?
key:
- rise ≈ 3.3 ms, about 3× slower than at standstill; overshoot about 4–5 %
- vq at 30 V for only about 0.3 ms; id jumps to about +24 A while iq rises
- it is mostly the cross-coupling, not the wall: with the saturation removed the rise is still about 3.4 ms
- rising iq pushes the d axis through ωe·Lq·iq (8.5 V at 60 A), id swings, and ωe·Ld·id feeds back into the q axis
traps:
- blaming the saturation without testing it (take the limit off and rerun: that is the experiment)
- saying the back-EMF slows the step: it is constant at fixed speed, the integrator already holds it before the step
solution:
About 3.3 ms and 4–5 % overshoot. vq touches 30 V for only ~0.3 ms, and removing the limit leaves the rise almost the same, so the wall is not the cause. The cause is the coupling: iq rising puts ωe·Lq·iq ≈ 8.5 V into the d axis, id kicks to ~+24 A, and ωe·Ld·id fights the q axis. The PI was designed for an uncoupled R-L that only exists at standstill.
:::

:::q id=k3 kind=check
At 5000 rpm without anti-windup: how long was vq saturated, what was the overshoot? With clamping? Explain what the integrator was doing while vq sat at 30 V.
key:
- without anti-windup: vq saturated about 22 ms, iq overshoots about 35 % (to ≈ 81 A), rise ≈ 10 ms
- with clamping: overshoot ≈ 2 %, saturated ≈ 7 ms
- while saturated the error stays large, so the integrator keeps charging; when iq gets close, the stored integral holds vq at the wall too long and iq overshoots
- at 5000 rpm the steady voltage arrow is 30.1 V (vq = 28.2 V, vd = −10.6 V): 60 A is right at the edge, so with a vector limit it would not even be reachable
traps:
- "anti-windup makes it faster": here it barely changes the rise; it removes the overshoot
- missing that the 60 A target is barely feasible at 5000 rpm (L3b, the voltage ellipse)
solution:
Without anti-windup vq sits at 30 V for ~22 ms, the integrator winds up, and iq overshoots ~35 %. Clamping stops the integrator while saturated: overshoot ~2 %. Underneath it is L3b again: at 5000 rpm, 60 A needs a 30.1 V arrow (vq 28.2 V, vd −10.6 V), so you are asking for a point on the edge of the voltage ellipse. Per-axis clamping hides that; a vector limit would show it.
:::

:::q id=k4 kind=check
If you added decoupling: rise time at 4000 rpm now? What does that prove, and why might the VESC still leave it off?
key:
- rise ≈ 1.1 ms again (≈ 1.3 ms with clamping), almost no overshoot, id stays near 0
- proves the slowdown was the coupling and back-EMF the design ignored, not the gains
- the feed-forward uses ωe, L and λm: it is only as good as the speed estimate and the parameters (the VESC's detection of λm moves between 15.9 and 17.0 mWb from session to session; its configuration now holds the measured 16.855)
- a wrong feed-forward injects a disturbance instead of cancelling one; a PI alone is more robust to parameter error
traps:
- "the VESC should always enable it": no number to back that up
solution:
Back to ~1.1 ms with id flat: with feed-forward the PI sees the R-L it was designed for. The catch is that decoupling uses ωe, Ld, Lq and λm, and a λm taken from a single detection can be 5 % off; wrong feed-forward adds error. At 2000 rad/s of bandwidth the PI alone is acceptable, which is probably why it is off by default.
:::

## Judgement {#judgement}

:::q id=c1 kind=case
You are in VESC Tool. Your colleague wants a faster current response for launch control and proposes doubling the current-loop bandwidth to 4000 rad/s. What do you check before typing it in? Use your model.
key:
- at standstill the rise halves to ≈ 0.55 ms and the peak vq at a 60 A step doubles to ≈ 27 V, close to the 30 V wall
- the loop runs in discrete time (15 or 30 kHz, Ts not yet confirmed on the device): the sample delay limits how far ωc can go; a continuous model is optimistic
- noise: higher Kp amplifies current-sensor noise into voltage
- need first: what rise time does launch control actually require? a requirement with a number before the change
traps:
- trusting the continuous model's stability at any ωc
- changing a gain without a requirement (the systems-engineering habit)
solution:
The model says the rise halves to ~0.55 ms and the voltage peak goes to ~27 V. But the model is continuous; your VESC samples at 15 or 30 kHz (open question in motor_params.m), and the delay eats phase margin as ωc grows. Higher Kp also amplifies sensor noise. And first ask what launch control needs: traction control acts in tens of ms, so a 1.1 ms current loop is probably not the bottleneck.
:::

:::q id=c2 kind=error
"I set Kp = ωc·Lq and Ki = ωc·Rs, so my current loop has 2000 rad/s of bandwidth at every speed." What is wrong?
key:
- the design assumes the plant is R-L alone; that is true only at standstill or with perfect decoupling
- at 4000 rpm without decoupling the step takes about 3× longer (≈ 3.3 ms instead of 1.1 ms)
- reference tracking can look first-order while disturbance rejection is slow: the cancelled plant pole (τ ≈ 4 ms) stays in it
- near the voltage limit the loop is saturated and there is no bandwidth at all: the loop is open
solution:
It is 2000 rad/s for the plant it was designed for: R-L at standstill. At speed the cross-coupling and back-EMF are disturbances, rejected only as fast as the slow, cancelled plant pole allows (Åström & Murray §9.5 show the same trap on a cruise control), and on the 30 V wall the loop is open. Measured in your model: 1.1 ms at 0 rpm, 3.3 ms at 4000 rpm.
:::

## Close {#close}

:::q id=z0 kind=explain
In at most 5 lines, to an interviewer: how did you tune the current loop, what did your simulation show at speed, and what would you change?
key:
- pole/zero cancellation: Kp = ωc·L, Ki = ωc·Rs, ωc = 2000 rad/s as in his VESC; 1.1 ms rise at standstill, matching the hand calculation
- at 4000 rpm without decoupling about 3× slower, from cross-coupling, not saturation (checked by removing the limit)
- at 5000 rpm the 30 V wall plus windup gave about 35 % overshoot; clamping fixed it
- decoupling restores 1.1 ms but depends on parameters and the speed estimate
solution:
I tuned the PI by pole/zero cancellation, Kp = ωc·L and Ki = ωc·Rs with ωc = 2000 rad/s like my VESC, and got the predicted 1.1 ms rise at standstill. At 4000 rpm without decoupling it was 3× slower; removing the voltage limit showed the cause was cross-coupling, not saturation. At 5000 rpm the 30 V limit wound up the integrator, 35 % overshoot, fixed with clamping. Decoupling restores 1.1 ms but only if λm and L are right.
:::

:::q id=z1 kind=doubt
What is still unclear, or what did the simulation do that you did not expect? Write it as it is.
:::
