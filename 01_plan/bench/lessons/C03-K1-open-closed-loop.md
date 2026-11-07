---
id: C03-K1
cycle: C03
title: Control 1: open and closed loop on your R-L coil
date: 2026-11-05
slot: 2
minutes: 55
lede: After Park, your q axis is a 28 mΩ resistor in series with a 113 µH coil, fighting a back-EMF of 21 V at 4000 rpm. One volt of error is 36 amps. Today you find out why nobody drives that open loop, and why a proportional gain alone is not enough either.
sources: 04_model/params/motor_params.m (Rs, Lq, λm, VESC kp/ki, decoupling off, control period OPEN) · Åström & Murray, Feedback Systems 2e, §1.1 pp. 1-1–1-3 (open vs closed loop), §1.2 and Table 1.1 pp. 1-4–1-5 (feedforward vs feedback), §1.5 and fig. 1.11 pp. 1-13–1-14 (cruise control: feedback rejects a slope disturbance and is robust to mass) · Franklin, Powell & Emami-Naeini 8e, §4.1 eqs. (4.1)–(4.11) and §4.1.3 (basic equations, regulation), §4.2.2 (system type for disturbance rejection), §4.3.1 eqs. (4.56)–(4.61) (proportional control leaves a steady error), §4.4 fig. 4.27 (feedforward by plant inversion). Franklin is an e-book without printed page numbers: cite by section and equation
---

## Predict {#predict}

Two from your open mistakes first, from memory. Then two guesses about today, with your reason.

:::q id=r1 kind=recall
Your quad is powered at a FIXED voltage (no current control) and starts climbing a hill. What happens to the current and the torque, and why? Then: what changes when the VESC is in current control?
key:
- fixed V: I = (V − E)/R; the hill slows the motor, E = ωe·λm drops, so the current and the torque RISE
- that is how a fixed-voltage motor finds the torque the hill needs
- in current control the throttle sets the current; the VESC changes the voltage to hold it, and the hill only changes the speed
traps:
- "current and torque stay the same" (his mistake #15)
- mixing up voltage mode and current mode (same root as mistake #2)
solution:
At fixed voltage, I = (V − E)/R. The hill slows the motor, E falls, and the current and torque grow until they match the hill. In current control the throttle fixes the amps and the VESC moves the voltage to keep them; the hill only decides the speed. Today you see that "the VESC moves the voltage" is a closed loop, and why it has to be one.
:::

:::q id=r2 kind=recall
Someone computes "52 V across your 28 mΩ gives 1860 A". What is the 28 mΩ, and name the two things that keep the real current far below that.
key:
- 28 mΩ is Rs, the resistance of one motor phase (plus MOSFETs), not the battery
- once the motor turns, the back-EMF opposes the supply, so only V − E drives current
- the VESC limits the current with its current loop (120 A motor, 40 A battery)
- battery current and phase current are linked by power, not by √3
traps:
- taking 28 mΩ as the battery resistance (his mistake #16)
- "40 A / √3 ≈ 70 A per phase" (mistake #16)
solution:
28 mΩ is one phase of the motor. Two things save you: the back-EMF, which eats most of the bus voltage once you turn, and the VESC's current loop, which never lets the full voltage sit across the copper. Today's lesson is that second one. Your calculation is not crazy: it says exactly why the loop has to exist.
:::

:::q id=p1 kind=predict
Rotor held still. You apply a fixed 1 V step to the q axis, no controller. Guess: how many amps at the end, and roughly how long does it take to get there?
key:
- final current V/R = 1/0.028 ≈ 36 A
- time constant τ = L/R ≈ 4.0 ms; it reaches 63 % in one τ, ~98 % in 4 τ ≈ 16 ms
traps:
- thinking 1 V is "small": on 28 mΩ it is 36 A
- guessing microseconds or seconds without the L/R ratio
solution:
36 A for every volt, reached with a time constant of about 4 ms. One volt, which is 2 % of your bus, already pushes a third of your motor's current limit. Keep that number in mind for the whole lesson.
:::

:::q id=p2 kind=predict
Now a controller that only multiplies the error by a gain: v = Kp·(iq_ref − iq), with your VESC's kp = 0.21 V/A. You ask 40 A with the rotor held still. Does iq reach 40 A? Then guess what happens at 4000 rpm.
key:
- no: a P controller needs an error to produce any voltage, so iq settles below the reference
- at standstill the shortfall is small-ish (≈ 4.7 A)
- at 4000 rpm the back-EMF (≈ 21 V) must also be produced from the error: the P loop fails badly
solution:
It does not reach 40 A: the only voltage it makes comes from the error, so some error must remain. At standstill it settles near 35 A. At 4000 rpm the loop must also produce 21 V of back-EMF from the error alone, and it cannot. You will compute how badly in idea 4.
:::

## Core: six ideas on your motor {#core}

Each idea starts from your q axis or your VESC, then the law.

### The plant: your q axis is a coil with a battery against it

In L3a you wrote the q-axis voltage equation. Keep id = 0, as your VESC does:

= vq = Rs·iq + Lq·diq/dt + ωe·λm

Read it as a circuit: the inverter's voltage vq pushes through a resistor Rs = 28.02 mΩ and a coil Lq = 113 µH, against a battery whose voltage grows with speed, the back-EMF ωe·λm. In control terms the **plant** is first order:

= iq(s) / vq(s) = 1 / (Lq·s + Rs) = (1/Rs) / (τ·s + 1)    τ = Lq/Rs = 4.0 ms    DC gain 1/Rs = 35.7 A/V

Two numbers make it scary. The **gain** is huge: 36 A per volt, and the inverter can put 30 V on it, which would be over 1000 A if nothing stopped it. The **slope** at the start is V/L: 1 V makes the current rise at 8.8 A per millisecond, 30 V at 265 A/ms. In the half millisecond it takes you to blink, a wrong voltage has already burned through your 120 A limit.

> The back-EMF is not part of the plant here: it is an input you do not choose, a **disturbance**. At 4000 rpm it is 21.2 V, at 1000 rpm 5.3 V. Franklin calls this W, the plant disturbance (§4.1, fig. 4.2).

:::q id=i1 kind=calc
Rotor held still (no back-EMF). You command a 5 V step on the q axis, open loop. Compute: final current, initial slope, current after one τ, and the time it takes to cross the 120 A motor limit.
key:
- final current 5 / 0.02802 = 178 A (over the 120 A limit)
- initial slope V/L = 5 / 113e-6 = 44 A/ms
- after τ = 4.03 ms: 63 % of 178 = 113 A
- crosses 120 A at t = −τ·ln(1 − 120/178) ≈ 1.12·τ ≈ 4.5 ms
traps:
- using Ld (99 µH) for the q axis
- forgetting the exponential: 120 A is not at 120/44 = 2.7 ms (that is the straight-line slope)
solution:
I∞ = 5/0.02802 = 178 A. Slope 5/113 µH = 44 A/ms. At one τ (4.03 ms): 0.632 × 178 = 113 A. It crosses 120 A at −4.03 ms × ln(1 − 0.673) = 4.5 ms. Five volts, one tenth of your bus, overshoots the motor limit in under 5 ms. Nothing in open loop would stop it there.
:::

src: Åström & Murray §1.1, pp. 1-1–1-3 (system, input, output; open and closed loop); dq equation and Rs, Lq from 04_model/params/motor_params.m

### Open loop: why "compute the voltage and apply it" fails

Open loop means: compute vq from the model and apply it, never looking at the current. For 40 A at 4000 rpm you would apply vq = Rs·40 + ωe·λm = 1.12 + 21.18 = 22.30 V. On paper, perfect. In your quad, three things are not what the model says:

- **Rs drifts.** Copper moves 0.39 % per kelvin. Your VESC does not compensate it (`foc_temp_comp = 0`), and the 28 mΩ was measured at an unknown temperature. A motor 60 K hotter has 23 % more resistance.
- **λm is not what you think.** The measured value is 16.855 mWb, but your VESC's detection moves from 15.9 to 17.0 mWb between sessions. A run that lands at 15.92 is 5.5 % off: small, but it multiplies ωe.
- **The back-EMF changes with speed**, all the time, while you ride.

And every error in volts becomes 36 A of error in current, because there is nothing else in the circuit to absorb it. Franklin puts it bluntly: in the open-loop structure the controller has no influence at all on the response to a disturbance (§4.1.3). Åström and Murray summarise it in a table: feedforward (open loop) acts on plans and is sensitive to model errors; feedback acts on deviations and is robust to them (Table 1.1, p. 1-5).

:::q id=i2 kind=calc
Open loop at 4000 rpm. You compute vq for 40 A using the λm from one detection run, 15.92 mWb (your 7-sep session), but the real motor has 16.855 mWb. How many volts are you short, and what current flows in steady state? Then a second, separate case: at standstill, you set the voltage for 40 A with the cold Rs, and the motor is now 60 K hotter. What current flows?
key:
- volt error = ωe·Δλm = 1257 × (16.855 − 15.92) mWb = 1.17 V short
- current error = 1.17 / 0.02802 ≈ 42 A: iq ≈ 40 − 42 ≈ −2 A, the motor brakes instead of pulling
- hot case: R × (1 + 0.0039 × 60) = 1.234·R, so iq = 40 / 1.234 ≈ 32 A (−19 %)
- the speed-dependent error is far worse than the thermal one: it multiplies ωe
traps:
- using mechanical ω (419 rad/s)
- dividing the volt error by (R + something): in open loop there is only R
solution:
Short by 1257 × 0.935 mWb = 1.17 V. On 28 mΩ that is 42 A: instead of +40 A you get about −2 A, a 5.5 % flux error turns pulling into braking. Hot case: Rs grows 23 %, so 1.12 V gives 32 A instead of 40 A. Both small model errors, both big current errors. That is the 1/R gain again.
:::

src: Franklin §4.1, eqs. (4.1)–(4.4) and §4.1.3 (open loop: the controller cannot act on disturbances); Åström & Murray §1.2, Table 1.1, pp. 1-4–1-5; Rs drift 0.39 %/K and λm values from motor_params.m

### Closed loop: measure, compare, correct

Your VESC does not trust the model. Every control period it **measures** the phase currents with its shunts, turns them into iq (Clarke and Park, L2 and L3a), **compares** with the throttle's request, and **corrects** the voltage according to the error. That is feedback: the definition Åström and Murray start with, two systems connected in a cycle, each one's output driving the other (§1.1).

Your VESC's current loop, the q axis, in one line:

= iq_ref (throttle) → ⊕ → error → PI (kp 0.2119 V/A, ki 56.2 V/(A·s)) → vq → limit |v| ≤ 30 V → inverter → coil 1/(Lq·s + Rs) → iq

= disturbance: − ωe·λm enters between the inverter and the coil    feedback: shunts → Clarke → Park (θe) → iq back to ⊕ with a minus sign

Why it beats open loop: if the motor heats or λm is off, the current drops, the error grows, and the controller pushes more volts **without knowing why**. Åström and Murray show the same with cruise control: a slope appears, the speed drops, the controller opens the throttle, for cars from 1200 to 2000 kg alike (fig. 1.11, p. 1-14). Your "slope" is the back-EMF; your "mass" is Rs and λm.

> The control period is every 33 µs or every 67 µs (one or two PWM periods at 30 kHz). Which one your FSESC build runs is still **OPEN** in `motor_params.m`; the model assumes 67 µs. The lab below samples at 33 µs.

:::q id=i3 kind=check
In that loop, name: (a) the reference, (b) the measured output and the sensor, (c) the actuator, (d) the disturbance, and (e) one model error the loop corrects without being told. Then: what does the loop need that open loop did not?
key:
- (a) iq_ref, from the throttle; (b) iq, from the phase shunts through Clarke and Park
- (c) the inverter, through vq (then inverse Park and SVPWM), limited to 30 V
- (d) back-EMF ωe·λm (also the cross-coupling term on d)
- (e) Rs drift with temperature, or λm error: the loop corrects both through the error
- needs: a sensor (shunts + angle θe) and a stable loop; Åström: risk of instability that open loop does not have
traps:
- calling the throttle the disturbance
- forgetting that the measurement depends on θe: a wrong angle feeds back a wrong iq (L3a idea 5)
solution:
Reference: iq_ref from the throttle. Output: iq, measured by the shunts and Park. Actuator: the inverter, via vq, capped at 30 V. Disturbance: the back-EMF. It corrects a hot Rs or a wrong λm without knowing either. The price: you need a good sensor and a good angle, and a loop can go unstable, which an open loop cannot (Table 1.1).
:::

src: Åström & Murray §1.1, pp. 1-1–1-3 (closed loop as interconnected systems); §1.5 and fig. 1.11, pp. 1-13–1-14 (feedback rejects a slope and is robust to mass changes); loop structure and gains from motor_params.m

### P only: fast, but it always leaves an error

Start with the simplest controller: vq = Kp·(iq_ref − iq). Put it in the plant (Franklin §4.3.1 does this for a generic plant):

= Lq·diq/dt = Kp·(iq_ref − iq) − Rs·iq − ωe·λm

= closed-loop pole s = −(Rs + Kp)/Lq    bandwidth ωb = (Rs + Kp)/Lq ≈ Kp/Lq when Kp ≫ Rs

= steady state: iq = (Kp·iq_ref − ωe·λm) / (Rs + Kp)

What this says:

- **The pole moves.** Open loop it was R/L = 248 rad/s (τ = 4 ms). With Kp = 0.2119 V/A it is 2123 rad/s: the loop is 8.6 times faster than the coil. Rise time 10–90 % ≈ 2.2/ωb ≈ 1.0 ms.
- **There is always an error to the reference**: iq_ref·Rs/(Rs + Kp). A P controller only produces voltage from error, so some error must stay. Franklin: a Type 0 system with P control keeps a nonzero offset to a constant reference and cannot fully reject a constant disturbance (§4.3.1).
- **The disturbance is divided by (Rs + Kp)**, not by Rs alone. Feedback shrinks the 36 A/V of open loop to about 4 A/V. Better, not zero.

:::q id=i4 kind=calc
P only, Kp = 0.2119 V/A (your VESC's kp), iq_ref = 40 A. Compute the closed-loop bandwidth, the steady iq at standstill, and the steady iq at 4000 rpm. Then: what Kp would keep the 4000 rpm error under 2 A, and what bandwidth is that?
key:
- ωb = (0.02802 + 0.2119)/113e-6 = 2123 rad/s ≈ 338 Hz (Kp/L alone: 1875 rad/s)
- standstill: iq = 0.2119 × 40 / 0.2399 = 35.3 A, error 4.7 A (12 %)
- 4000 rpm: iq = (8.48 − 21.18)/0.2399 = −53 A: the motor brakes while you ask for +40 A
- error < 2 A needs Kp ≳ 21.18/2 ≈ 10.6 V/A, bandwidth ≈ 94 000 rad/s ≈ 15 kHz: faster than the control period can sample (33 or 67 µs, still open)
traps:
- forgetting Rs in the denominator (small, but it is there)
- treating the back-EMF as "part of the reference" instead of a disturbance the error must produce
- "just raise Kp": the sampling and the one-period delay forbid it (lab l2)
solution:
ωb = 0.2399/113 µH = 2123 rad/s. Standstill: 35.3 A, 4.7 A short. At 4000 rpm the loop must make 21.2 V from the error alone: iq = (8.48 − 21.18)/0.2399 = −53 A. You ask to pull and it brakes. To keep the error under 2 A you would need Kp ≈ 10.6 V/A, a 15 kHz bandwidth: not possible when you only correct every 33–67 µs. P alone is out. Two fixes: feed-forward (next idea) and the integrator (next lesson).
:::

src: Franklin §4.3.1, eqs. (4.56)–(4.61) (proportional control: steady error to a step reference and to a step disturbance, falling as kP grows); §4.2.2 (system type for disturbance rejection)

### Disturbance and feed-forward: give the loop the volts you already know

The back-EMF is not a mystery: ωe comes from the angle estimate and λm is in the configuration. So add it to the controller's output before the loop has to find it:

= vq = Kp·(iq_ref − iq) + ω̂e·λ̂m    (back-EMF decoupling, a feed-forward)

If ω̂e·λ̂m equals the real ωe·λm, the disturbance cancels and the loop is back to its standstill error. If the estimate is off, the loop only has to fight the **difference**: here a 5.5 % λm error (the 7-sep detection), 1.17 V at 4000 rpm, divided by (Rs + Kp). Feed-forward does the big, known part fast; feedback cleans up the small, unknown part. Franklin's §4.4 is exactly this: invert the plant model for the part you know, let feedback handle the rest (fig. 4.27). Åström and Murray: feed-forward needs a good model; feedback does not (Table 1.1).

The same trick for the d axis: add −ω̂e·Lq·iq to cancel the cross-coupling (L3a, c2).

> Your VESC has decoupling **OFF** (`foc_cc_decoupling = 0`). No feed-forward at all. It works anyway because of the integrator in its PI, which builds the 21 V slowly by itself. The cost appears when the speed changes fast.

:::q id=i5 kind=calc
P only, Kp = 0.2119 V/A, 4000 rpm, iq_ref = 40 A. Now you add back-EMF feed-forward using the 7-sep detection's λm = 15.92 mWb (the real one is 16.855). Compute the steady iq. Compare with the −53 A of idea 4 and say what the feed-forward bought and what it did not.
key:
- uncancelled volts = 1257 × 0.935 mWb = 1.17 V
- iq = (0.2119 × 40 − 1.17) / 0.2399 = (8.48 − 1.17)/0.2399 ≈ 30.4 A
- error ≈ 9.6 A: 4.7 A from P against Rs plus 4.9 A from the λm error
- bought: from −53 A to +30 A, the loop no longer has to produce 21 V from error; not bought: zero error (that needs the integrator) and robustness to a wrong λm
traps:
- assuming feed-forward makes the error zero
- dividing the 1.17 V by Rs only (that is open loop; here it is Rs + Kp)
solution:
Residual disturbance 1.17 V. iq = (8.48 − 1.17)/0.2399 = 30.4 A. From −53 A to +30 A: feed-forward did 95 % of the job because it knew 95 % of the back-EMF. The rest, 4.7 A from the P offset and 4.9 A from the wrong λm, is still there. Feed-forward is only as good as your model; that is why the loop still needs feedback with an integrator.
:::

src: Franklin §4.4, fig. 4.27 (feed-forward by plant inversion, for tracking and for a measured disturbance); Åström & Murray §1.2, pp. 1-4–1-5; decoupling setting from motor_params.m

### Cascade: you are the outer loop, the current loop is the inner one

Your throttle does not ask for speed. Your VESC is in current control: the throttle asks for amps, and amps are torque (Kt = 0.0758 N·m/A, L3a). So the current loop is the **inner** loop. The **outer** loop is you: you look at the speed and the trail and move the throttle, at maybe 1–2 Hz. The inner loop runs at about 300 Hz bandwidth. The rule of a cascade: the inner loop must be several times (5–10×) faster than the outer one, so the outer loop can treat it as "asked torque = delivered torque". Later, your VCU will become a new outer loop (traction control, speed limit) that sends a current request to the VESC instead of you.

You already know this structure from the ECU. In a torque-based engine management the pedal is turned into a torque request; inner loops then deliver it through air, spark and fuel. Idle-speed control is the cleanest case: an outer rpm loop computes the torque needed, and fast inner paths (spark first, then air) realise it. Same shape here: the rider's speed loop outside, the 300 Hz current loop inside, and the inner one must be fast and stiff enough that the outer one never notices it.

:::q id=i6 kind=check
Draw your quad as a cascade in words: name the outer loop, its sensor and its output; the inner loop, its sensor and its output. Why must the inner loop be faster? And give the ECU loop you have calibrated that has the same structure, with what is outer and inner there.
key:
- outer: the rider (later the VCU); sensor: eyes/speed (later wheel speed); output: the current request iq_ref via the throttle
- inner: the VESC current loop; sensor: phase shunts + Park; output: vq to the inverter; bandwidth ~2000 rad/s ≈ 300 Hz
- the inner loop must be 5–10× faster so the outer loop sees it as a gain (asked torque ≈ delivered torque), otherwise the two interact and can oscillate
- ECU example with outer and inner named correctly (e.g. idle: rpm loop → torque request → spark/air paths; or boost pressure → wastegate actuator position)
traps:
- putting the current loop outside the speed loop
- saying the VESC controls speed: in current mode it does not
solution:
Outer: me, later the VCU, watching speed and sending an amp request through the throttle. Inner: the VESC current loop, shunts and Park in, vq out, about 300 Hz. The inner loop must be much faster so the outer one can treat it as "torque on request"; if their speeds are close they fight. ECU twin: idle-speed control, where the rpm loop asks for torque and spark and air deliver it.
:::

src: Åström & Murray §1.5 and fig. 1.11, pp. 1-13–1-14 (vehicle speed loop: the throttle commands force, the loop rejects the slope); Kt and current-mode operation from motor_params.m

## Lab: touch it {#lab}

Write your prediction before you move a slider. If it surprises you, say why in the same box.

:::lab rl
One phase as an R-L circuit, open-loop voltage step
:::

:::q id=l1 kind=lab
Predict first, then check: with 1 V, what are the final current and the time to 63 %? Then find the smallest step that crosses the 120 A limit, and at 30 V say how long it takes to cross it.
key:
- 1 V: 35.7 A final, 63 % (22.6 A) at τ = 4.03 ms
- to cross 120 A at all: V > 120 × 0.02802 = 3.36 V
- 30 V: final 1071 A, crosses 120 A after ≈ 0.48 ms
- the time constant does not change with the voltage; only the final value and the slope do
traps:
- expecting τ to shrink with a bigger voltage
solution:
1 V: 36 A, 63 % at 4.03 ms. Anything above 3.36 V would eventually exceed 120 A. At 30 V the final value is 1071 A and you cross 120 A in under half a millisecond. τ stays at 4.03 ms whatever the voltage: it is a property of the coil, not of the drive.
:::

:::lab piloop
Closing the current loop on the R-L phase
:::

:::q id=l2 kind=lab
Make it a P controller: put Ki at its minimum (1 V/(A·s), negligible in 5 ms) and Kp at 0.21 V/A, step 40 A. Predict and read the final error. Then raise Kp to 1, 2, 3 and 4 V/A. Predict what happens to the error and to the shape, then explain what stops you from raising Kp forever.
key:
- Kp 0.21: settles ≈ 35.3 A, error ≈ 4.7 A, no overshoot (first order), rise ≈ 1 ms
- Kp 1: error ≈ 1.1 A; Kp 2: error ≈ 0.55 A but ~13 % overshoot appears; Kp 3: more overshoot and ringing
- Kp 4: it oscillates / limit-cycles against the ±30 V wall
- cause: the one-period delay; stability limit about Kp < Lq/Ts ≈ 3.4 V/A at 33 µs (half that if the real period is 67 µs, still open)
- error never reaches zero with P only, and the lab has no back-EMF: on the moving quad it would be far worse
traps:
- "higher Kp, always better": the delay sets a ceiling
- reading the overshoot as a second-order plant: the plant is first order, the delay adds the dynamics
solution:
At 0.21 V/A it settles near 35 A, 4.7 A short, no overshoot. Kp = 1 cuts the error to 1.1 A; Kp = 2 to 0.55 A, but it now overshoots; Kp = 4 oscillates. The plant alone is first order and could take any gain; what breaks it is that the voltage computed at one sample is only applied at the next. That caps Kp near Lq/Ts ≈ 3.4 V/A at 33 µs. With P alone you can shrink the error, never kill it, and the 21 V of back-EMF is not even in this lab.
:::

## Judgement {#judgement}

Reason from what you know is true, not from what sounds familiar.

:::q id=c1 kind=case
You are in VESC Tool, Motor Settings → FOC → General. You read Current Kp = 0.2119 and Current Ki = 56.20, and decoupling Disabled. A friend says: "The integrator is what makes it oscillate. Set Ki to 0, it is simpler and stable." Before touching anything, what do you predict at standstill and at 4000 rpm with Ki = 0, and what do you answer him? What would you change instead, if anything, and where would you test it first?
key:
- Ki = 0 leaves P only: at standstill iq ≈ 35 A for 40 A asked (−12 %)
- at 4000 rpm the back-EMF must come from the error: iq ≈ −53 A for +40 A asked, the motor brakes: dangerous on a ride
- the integrator is what supplies the 21 V of back-EMF (decoupling is off); bandwidth here is set by kp/L ≈ 1900 rad/s, and VESC derives kp = L·bw, ki = R·bw with bw = 2000 rad/s
- answer: do not remove Ki; if anything, enabling back-EMF decoupling would take the load off the integrator
- test first in the model (Simulink lessons) or on a stand with the current limit set, never on the trail
traps:
- changing a control gain on the quad without a prediction and a criterion with a number
- thinking a missing integrator just makes it "a bit slower"
solution:
Predict first: P only gives 35 A instead of 40 A at standstill, and at 4000 rpm about −53 A, braking when you ask to pull. The integrator is not decoration: with decoupling off it is the only thing that builds the 21 V of back-EMF. Answer: keep Ki. If you want to help the loop, the candidate is decoupling, which is a feed-forward. Try any change in the model first, then on the stand with the current limit configured and a number to compare against.
:::

:::q id=c2 kind=error
A colleague says: "Feedback makes the model unnecessary. With a closed loop you do not need to know Rs, Lq or λm." Where is he right, and where is he wrong? Use your numbers.
key:
- right: the loop corrects model errors it is not told about (hot Rs, wrong λm); 1.17 V of λm error becomes ~4.9 A with P, ~0 with an integrator, instead of 42 A open loop
- wrong: the gains themselves come from the model (VESC: kp = Lq·bw, ki = Rs·bw); a wrong L gives a wrong bandwidth or instability
- wrong: the stability limit depends on Lq and the control period (Kp < L/Ts)
- wrong: feed-forward (decoupling) needs λm and L, and the 30 V limit and observer need them too
solution:
Right that feedback forgives model errors: a 1.17 V λm error costs 42 A open loop and only about 5 A with a plain P loop. Wrong that you can forget the model: your VESC computes kp = Lq·bw and ki = Rs·bw from the measured R and L, the stability limit is near Lq/Ts, and any feed-forward uses λm. Feedback tolerates a model that is a bit wrong; it does not replace having one.
:::

## Close {#close}

:::q id=z0 kind=explain
Explain it as you would to an interviewer, in at most 5 lines: what the plant of your current loop is, why open loop fails on it, what a P controller does and does not fix, and what feed-forward adds.
key:
- plant: q axis as R-L, 1/(Lq·s + Rs), τ ≈ 4 ms, 36 A/V, with the back-EMF as a disturbance
- open loop fails: small volt errors (hot Rs, 5.5 % λm, speed) become tens of amps
- P: moves the pole to (Rs + Kp)/L (~2100 rad/s), divides the disturbance by (Rs + Kp), but always leaves an error; gain capped by the sampling delay
- feed-forward of ωe·λm removes the known part of the disturbance; feedback (with an integrator, next) removes the rest
solution:
After Park, my q axis is a 28 mΩ, 113 µH coil: τ = 4 ms and 36 A per volt, with the back-EMF as a disturbance of 21 V at 4000 rpm. Open loop, a 1 V model error is 36 A, so the VESC measures the current and corrects. A P gain makes the loop ~9 times faster but always leaves an error, and at speed it cannot make the back-EMF from the error. Feed-forward adds the known back-EMF directly; the integrator, next, removes what is left.
:::

:::q id=z1 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
