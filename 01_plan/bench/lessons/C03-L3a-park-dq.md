---
id: C03-L3a
cycle: C03
title: Park: riding on the rotor, and the dq equations
date: 2026-11-04
slot: 2
minutes: 55
lede: In L2 three currents became one arrow that turns 200 times a second at 4000 rpm. Now sit on your rotor and look at that arrow from there: it stops. Two constant numbers, id and iq, and four equations that are your VESC's whole picture of the motor.
sources: Hughes & Drury, Electric Motors and Drives, 5th ed. §8.2.2 pp. 266–267; §8.6.2 pp. 291–294; §9.3.5 pp. 326–328; §9.5.1 pp. 342–344; §9.6.3 pp. 358–360. VESC firmware dq equations as quoted in 04_model/params/motor_params.m
---

## Predict {#predict}

Two from your open mistakes first, from memory. Then two guesses about today, with your reason.

:::q id=r1 kind=recall
Your quad at full throttle on a hill, VESC in current control. Who decides how many amps flow in the motor phases: the hill, or you? And when can the VESC fail to deliver what you ask?
key:
- in current mode the throttle sets the current reference; the VESC's current loop forces it, the hill does not
- the hill only changes the speed (more load, less acceleration or the quad slows down)
- the VESC can only push the asked current while it has voltage left over the back-EMF: at high speed (duty near 0.95) the current falls below the request
traps:
- "the load torque decides the current" (his mistake #2): true in voltage mode, not in his VESC
- forgetting the voltage limit: current control is not unconditional
solution:
You do. The throttle is a current request and the VESC's current loop forces it, whatever the hill. The hill only decides what the speed does. The limit is voltage: the current flows only if the inverter has volts left over the back-EMF (ωe·λm). Near the duty ceiling it cannot, and the current drops below what you ask. Today you see this as an equation: the q-axis voltage.
:::

:::q id=r2 kind=recall
"More pole pairs make the motor smoother." What does the number of pole pairs really change, and what is the torque formula that shows it?
key:
- torque per amp: Te = 1.5·p·λm·iq, so Kt grows with p (0.0758 N·m/A for p = 3)
- electrical frequency at the same speed: fe = p·rpm/60
- smoothness comes from the sinusoidal waveform and the slot/winding design, not from p (his mistake #7)
traps:
- repeating "smoother" (mistake #7)
- forgetting that p also raises the electrical frequency the controller must follow
solution:
p multiplies torque per amp (Te = 1.5·p·λm·iq, Kt = 0.0758 N·m/A with your p = 3) and the electrical frequency (fe = p·rpm/60, 200 Hz at 4000 rpm). Smoothness is about waveform shape and slots, not p. You will derive the 1.5 today.
:::

:::q id=p1 kind=predict
You sit on your rotor, turning with it, and look at the stator current arrow from L2 while the quad cruises at constant speed and throttle. What do you see: an arrow turning, standing still, or changing length?
key:
- it stands still and keeps its length
- the arrow turns at ωe and the rotor turns at ωe too (synchronous machine), so relative to the rotor nothing moves
traps:
- "it turns slower" (that is an induction motor, which has slip)
solution:
It stands still. The current arrow turns at ωe and so does the rotor, because the motor is synchronous. From the rotor it is a fixed arrow with fixed length: two constant numbers.
:::

:::q id=p2 kind=predict
A PI controller has to follow a sine reference at 200 Hz. Will it track it well, with no error? Why?
key:
- no: a PI removes steady-state error only for constant references (the integrator wins on DC)
- on a sine it lags and loses amplitude, worse as frequency approaches the loop bandwidth (his loop: 2000 rad/s ≈ 318 Hz)
- this is the reason to change frame: in dq the reference is constant
solution:
Not well. The integrator kills error only for constant (DC) targets. A 200 Hz sine is not far below your loop bandwidth (2000 rad/s ≈ 318 Hz): it would lag and lose amplitude. In the rotor frame the same reference becomes constant, and the PI is perfect again.
:::

## Core: six ideas on your motor {#core}

Each idea starts from your rotor or your VESC, then the law. On a wide screen the motor on the right follows the idea you are reading.

### Ride on the rotor: 200 Hz sines become two constant numbers

At 4000 rpm your phase currents oscillate at 200 Hz, and the Clarke arrow from L2 (iα, iβ) turns 200 times a second. The VESC cannot regulate that well with a PI (Predict p2). The trick: describe the arrow not on axes glued to the stator, but on axes glued to the rotor. The rotor turns at the same electrical speed as the arrow, so on its axes the arrow stops.

Park does this: it rotates the αβ axes by the rotor's electrical angle θe. Hughes says it plainly: an observer riding with the field sees a constant phasor.

= id = iα·cos θe + iβ·sin θe    iq = −iα·sin θe + iβ·cos θe

= inverse:  iα = id·cos θe − iq·sin θe    iβ = id·sin θe + iq·cos θe

It is only a rotation: it does not change the arrow's length, so with amplitude-invariant Clarke the length of (id, iq) is the phase current peak. And it holds at every instant, transients included, not only in steady state. What it needs is θe, which changes 3 times per shaft turn (θe = 3·θm).

:::scene phases=3 field=off currents=on vectors=on dq=on labels=off rotor=on spin=on speed=0.12 delta=90 caption="The d and q axes are painted on the rotor and turn with it. Watch the current arrow: against the stator it turns, against the d–q axes it stands still."
dq axes riding on the rotor.
:::

:::q id=i1 kind=calc
From L2: 100 A peak currents at ωt = 120° gave iα = −50 A, iβ = 86.6 A. At that instant the rotor's d axis is at θe = 30°. Compute id and iq. What does the result say about where the current sits relative to the magnet?
key:
- id = −50·cos 30° + 86.6·sin 30° = −43.3 + 43.3 = 0 A
- iq = 50·sin 30° + 86.6·cos 30° = 25 + 75 = 100 A
- the length is still 100 A (rotation keeps length)
- all the current is on q, 90° electrical ahead of the magnet axis: the maximum-torque position of L2 idea 5
traps:
- sign error in iq: it is −iα·sin θe, and iα is negative
- using mechanical degrees for θe
solution:
id = (−50)(0.866) + (86.6)(0.5) = 0 A. iq = −(−50)(0.5) + (86.6)(0.866) = 25 + 75 = 100 A. Length 100 A, as before. The current arrow is at 120°, the d axis at 30°: the current is exactly 90° ahead of the magnet, all on q. That is δ = 90°, maximum torque per amp.
:::

src: Hughes §8.2.2 and fig. 8.3, pp. 266–267 (two-stage transformation, rotating frame sees a constant phasor)

### d and q on your rotor: iq pulls, id pushes on the magnet's flux

Look at one of your six buried magnets. The **d axis** (direct) goes through the centre of a magnet pole, along its flux. The **q axis** (quadrature) is 90° electrical ahead, which on your p = 3 rotor is 30° mechanical: the steel between two magnets. Hughes notes that on a buried-magnet rotor there are two candidates for "direct axis" (the magnet's and the low-reluctance one) and that the convention is the magnet's. The VESC uses the same.

What each current does physically:

- **iq** makes a stator field 90° from the magnet: the compass needle of L2 pulled at right angles. All the torque comes from here, like I in B·I·l.
- **id** makes a stator field along the magnet axis. It gives no magnet torque. Positive id adds to the magnet's flux, negative id opposes it (field weakening). Your VESC has field weakening and MTPA off, so it asks id = 0 always.

= flux on d:  ψd = Ld·id + λm    flux on q:  ψq = Lq·iq    (the magnet only appears on d)

> Ld = 99 µH < Lq = 113 µH: flux pushed along d must cross the magnet (μr ≈ 1, like air), flux along q runs through steel. Lq/Ld = 1.14 says "not pure surface magnets"; it does not prove interior magnets (your mistake #8). The real layout is not measured.

:::scene phases=0 field=off currents=off vectors=off dq=on labels=on rotor=on spin=off caption="No current. Find a magnet, its d axis through the centre, and the q axis 30° mechanical ahead, between two magnets."
d and q on a still rotor.
:::

:::q id=i2 kind=check
Your VESC asks id = 0. Why is that the efficient choice for your motor below base speed? And what would id = +30 A do to the magnet flux and to the copper?
key:
- torque per amp (magnet part) depends only on iq, so any id is current that heats copper (loss ∝ id² + iq²) without magnet torque
- id = 0 gives maximum torque per amp for a non-salient motor; Hughes: current in phase with E gives minimum copper loss for that torque
- id = +30 A strengthens the d-axis flux (ψd = λm + Ld·id): more back-EMF-like voltage, more saturation risk, more copper loss
- with his small saliency the reluctance term with positive id even subtracts torque, since Ld − Lq < 0
traps:
- "id makes torque too" without the saliency caveat
- "positive id weakens the field" (sign: negative id weakens)
solution:
Copper loss goes with id² + iq², but magnet torque only with iq. Any id is heat for nothing (Hughes: current in phase with E gives the most torque per amp). id = +30 A adds Ld·id ≈ 3 mWb to the 16.9 mWb of the magnet: more flux, more voltage needed at speed, more saturation, more loss. With Ld < Lq it even removes a little torque through the reluctance term (idea 4).
:::

src: Hughes §9.3.5, fig. 9.12, pp. 326–328 (buried magnets, choice of the d axis); §9.5.1, pp. 342–344 (Iq makes torque, Id = 0 gives maximum torque per amp)

### The dq voltage equations, term by term, at 4000 rpm

These are the equations your VESC firmware uses, quoted at the top of `motor_params.m`. Hughes works with phasors and ignores R; these are the same physics written per axis:

= vd = Rs·id + Ld·did/dt − ωe·Lq·iq

= vq = Rs·iq + Lq·diq/dt + ωe·(Ld·id + λm)

Four kinds of term:

- **Rs·i**: the copper (and MOSFETs), 28 mΩ.
- **L·di/dt**: the coil resisting change. Only in transients; in steady state di/dt = 0. τ = L/R ≈ 3.5 ms (d) and 4.0 ms (q).
- **ωe·L·i, cross-coupling**: appears because you look from a turning frame. The q current makes flux Lq·iq; seen by the d axis that flux is turning, so it induces a voltage. It grows with speed.
- **ωe·λm, back-EMF**: the magnet turning. Only on q, because the magnet sits on d and its voltage leads it by 90°.

With id = 0 in steady state, the q equation is vq = R·iq + ωe·λm: the V = I·R + E of L1. Seen in dq, your PMSM is a DC motor plus a d axis and a cross term.

> Your VESC has decoupling OFF (`foc_cc_decoupling = 0`): no feedforward of ωe·λm or ωe·L·i. The PI integrators must build those volts themselves, as if they were a disturbance.

:::q id=i3 kind=calc
Your motor at 4000 rpm, steady state, iq = 40 A, id = 0. Compute ωe, then each term of vd and vq, and |v|. Does it fit in the 30 V peak your 52 V bus gives with SVPWM?
key:
- ωe = 3 × 4000 × 2π/60 = 1257 rad/s (200 Hz)
- vd = −ωe·Lq·iq = −1257 × 112.8 µH × 40 = −5.67 V
- vq = Rs·iq + ωe·λm = 1.12 + 21.18 = 22.30 V
- |v| = √(5.67² + 22.30²) = 23.0 V < 30 V: it fits, about 7 V of margin
- back-EMF is 95 % of vq; the copper drop is tiny
traps:
- using mechanical ω (419 rad/s) instead of electrical
- saying vd = 0 because id = 0 (the cross term is there)
- forgetting the L·di/dt terms are zero only in steady state
solution:
ωe = 1257 rad/s. vd = −1257 · 112.8e-6 · 40 = −5.67 V, all from cross-coupling. vq = 0.028 · 40 + 1257 · 0.016855 = 1.12 + 21.18 = 22.30 V. |v| = 23.0 V, below 30 V: the VESC still has about 7 V to push current changes. Note who dominates: the back-EMF, 21 V of 23.
:::

src: dq equations: VESC firmware as quoted in 04_model/params/motor_params.m (Hughes uses the phasor form V = E + jIXs, §9.5.1, p. 343)

### Torque: Te = 1.5·p·(λm + (Ld − Lq)·id)·iq

Torque from the power balance. With amplitude-invariant Clarke and Park (the VESC's choice), id and iq are peak phase values. Three phases deliver P = 3·Vrms·Irms = 3·(V̂/√2)·(Î/√2) = 1.5·V̂·Î. That is where 1.5 comes from: it is the price of keeping amplitudes, not a property of the motor.

= P = 1.5·(vd·id + vq·iq)

The part of that power that the back-EMF converts is 1.5·ωe·λm·iq. Set it equal to Te·ωm and use ωe = p·ωm:

= Te = 1.5·p·[ λm·iq + (Ld − Lq)·id·iq ]    magnet torque + reluctance torque

> Kt = 1.5 × 3 × 16.855 mWb = 0.0758 N·m per amp of iq: 40 A gives 3.03 N·m, 120 A gives 9.10 N·m at the motor shaft. One detection session gave λm = 15.92 mWb; with that value the VESC would think it makes 0.0716 N·m/A, 5.5 % less. Its detections move between 15.9 and 17.0 mWb from session to session, which is why the measured value is the one in its configuration now.

Your reluctance term: Ld − Lq = −13.5 µH. It helps only with **negative** id. Hughes: on PM/Rel rotors the reluctance share ranges from 1:4 to 1:1; yours is far smaller.

:::q id=i4 kind=calc
iq = 40 A. Compute the torque with id = 0. Then with id = −20 A: how much does the reluctance term add, in N·m and in % of the magnet torque? Is MTPA worth switching on for your motor?
key:
- id = 0: Te = 0.0758 × 40 = 3.03 N·m
- id = −20 A: (Ld − Lq)·id = (−13.54 µH)(−20) = +0.27 mWb, which is 1.6 % of λm
- Te = 1.5 × 3 × (16.855 + 0.271) mWb × 40 = 3.08 N·m, about +0.05 N·m
- but the current magnitude grew from 40 to 44.7 A (+25 % copper loss for +1.6 % torque): MTPA on his motor buys almost nothing
traps:
- forgetting the sign: with Ld < Lq, positive id removes torque
- comparing at equal iq but not at equal total current
solution:
id = 0: 3.03 N·m. id = −20 A: the reluctance term adds 13.54e-6 × 20 = 0.27 mWb of "equivalent flux", 1.6 % of λm, so 3.08 N·m. But |i| went from 40 to 44.7 A, which is 25 % more copper loss for 1.6 % more torque. With saliency this small, MTPA has almost nothing to find: id = 0 is close to optimal. Remember the saliency itself changes with current (measured 13.5 µH at 40 A, more at 98 A).
:::

src: Hughes §9.3.5, pp. 326–327 (PM/Rel torque components); §9.5.1, p. 344 (P = E·Iq, the d.c.-machine form)

### A wrong angle mixes id and iq

Everything above uses θe. Your VESC gets it from the three Hall sensors at low speed and from an observer (a flux estimator) above 2500–4000 ERPM, which is 830–1330 rpm at the motor. If the angle it uses is off by ε, its d–q axes are rotated by ε relative to the real magnet. It thinks it puts 40 A on q; in reality the current sits at 90° + ε from the magnet:

= real id = −I·sin ε    real iq = I·cos ε

So an angle error does two things: less torque (cos ε, the sin δ of L2 i5 seen from the rotor) and a current on d that nobody asked for. If the estimate is ahead (ε > 0), you get negative id (weakening); behind, positive id. The currents still read perfect in the VESC: it measures them in its own wrong frame.

:::scene phases=3 field=on currents=off vectors=on dq=on labels=off rotor=on spin=on speed=0.12 delta=60 caption="δ = 60°: the stator field is 30° short of the q axis. Part of the current now lies on d. Watch the torque-per-amp readout."
Angle error of 30°.
:::

:::q id=i5 kind=calc
The observer is 30° electrical ahead of the real rotor. The VESC holds iq = 40 A, id = 0 in its frame. What are the real id and iq, and the real torque? What does VESC Tool show for Id and Iq?
key:
- real id = −40·sin 30° = −20 A, real iq = 40·cos 30° = 34.6 A
- real torque = 1.5·3·(16.855 + 0.271) mWb × 34.6 A ≈ 2.67 N·m vs 3.03 expected (−12 %)
- same copper loss (still 40 A), less torque
- VESC Tool shows Id ≈ 0 and Iq ≈ 40 A: it measures in its own (wrong) frame, so the error is invisible in the current plots
traps:
- "the VESC would see the error in Id": no, it computes Id with the wrong angle
- forgetting the reluctance term changes sign with the sign of ε
solution:
Real id = −20 A, real iq = 34.6 A. Torque ≈ 2.67 N·m instead of 3.03 (−12 %); with ε = −30° it would be 2.59 N·m, since then id = +20 A and the reluctance term subtracts. VESC Tool shows Id ≈ 0, Iq ≈ 40 A: the controller is happy because it measures in its own frame. You only see the error indirectly: less acceleration, more amps for the same torque, a voltage vector that does not match the model.
:::

src: Hughes §9.5.1, p. 344 (torque ∝ current component at right angles to the magnet flux); §9.6.3, p. 359 (FOC locks the frame to the rotor)

### What your VESC does every control period

Now the map for the next lessons. Every control period (one or two PWM periods at 30 kHz, so 33 or 67 µs; which one your FSESC build uses is still OPEN in `motor_params.m`), the VESC runs:

- measure two (or three) phase currents
- **Clarke**: iU, iV, iW → iα, iβ (L2)
- **angle**: θe from Halls or observer
- **Park** with θe: → id, iq (today)
- **two PI controllers**: id towards 0, iq towards the throttle's request → vd, vq (L4)
- **voltage limit**: |v| ≤ Vbus/√3 = 30 V (L2 hexagon)
- **inverse Park** with the same θe: → vα, vβ
- **SVPWM**: → three duty cycles for the three half-bridges (L1, L2)

Left of Park everything turns at 200 Hz; right of it, in steady state, everything is DC. Hughes draws exactly this for a PM motor (fig. 9.29), with the flux demand set to zero.

= at 200 Hz and 33 µs: 150 control periods per electrical cycle

:::q id=i6 kind=check
In that chain, which signals are constant at steady 4000 rpm and constant throttle, and which oscillate at 200 Hz? Where does θe enter, and what happens to the motor if the Hall cable falls off while you ride at 500 rpm?
key:
- constant: id, iq, their references, vd, vq (DC in the rotor frame)
- 200 Hz: iU, iV, iW, iα, iβ, vα, vβ and the three duties
- θe enters twice: in Park (measure) and in inverse Park (act); an error in it corrupts both
- at 500 rpm (1500 ERPM, below the 2500 ERPM blend) the VESC depends on the Halls: without them it has no angle, the frame is wrong, torque collapses or the motor jerks/stalls; the observer only takes over above 2500–4000 ERPM
traps:
- "the PI outputs oscillate": in steady state they are constant
- forgetting that inverse Park also uses θe
solution:
Constant: id, iq, their references and the PI outputs vd, vq. At 200 Hz: phase currents, iα/iβ, vα/vβ, duties. θe enters twice, in Park and in inverse Park. At 500 rpm you are at 1500 ERPM, below the Hall-to-observer blend (2500–4000 ERPM), so the angle comes only from the Halls: lose them and the VESC loses the frame. Expect jerks, a fault, or no torque. Above ~1330 rpm the observer would carry on.
:::

src: Hughes §9.6.3, fig. 9.29, pp. 358–359 (FOC scheme for a PM motor, flux demand zero); §8.6.2, pp. 291–294 (two measured currents, frame transform, PI on flux and torque components)

## Lab: touch it {#lab}

Write your prediction before you move a slider. If it surprises you, say why in the same box.

:::lab park
abc currents, the αβ arrow and the dq frame
:::

:::q id=l1 kind=lab
Set iq = 40 A, id = 0, angle error 0. Predict first: when you double the speed, what happens to the three phase currents, to the αβ arrow, and to the id and iq readouts? Then do it.
key:
- phase currents: same 40 A peak, twice the frequency
- αβ arrow: same length, turns twice as fast
- id and iq: unchanged (0 and 40 A), they do not care about speed
- the speed shows up in the dq voltages (back-EMF and cross terms), not in the currents
solution:
The sines keep their 40 A peak but go twice as fast; the αβ arrow turns twice as fast at the same length; id = 0 and iq = 40 A do not move. Speed does not appear in the dq currents at all. It appears in the dq voltages, through ωe·λm and ωe·L·i.
:::

:::q id=l2 kind=lab
Now set an angle error of 30°, then 90°. Predict the real id and iq before moving it. At 90°, what does the motor do, and where does the power go?
key:
- 30°: real iq ≈ 34.6 A, real id ≈ ±20 A (sign depends on the sign of the error)
- 90°: real iq = 0, all 40 A on d: no torque
- at 90° all electrical power goes to copper heat: 1.5·Rs·i² = 67 W for 40 A
traps:
- "at 90° the motor runs backwards": no, zero torque; it would take more than 90° to reverse it
solution:
30°: iq ≈ 34.6 A, id ≈ ±20 A. 90°: iq = 0 and the full 40 A on d. No torque, and the 1.5 × 0.028 × 40² = 67 W all heat the copper. Beyond 90° the torque changes sign.
:::

## Judgement {#judgement}

Reason from what you know is true, not from what sounds familiar.

:::q id=c1 kind=case
You are in VESC Tool with the Realtime data plots open on Id and Iq. (a) Quad on a stand, rear wheels in the air, you hold the throttle still at a medium position. (b) Quad on the ground, brake fully on, you ask about 20 A of throttle for two seconds. What should Id and Iq read in each case, and why? Which number in (a) can you not predict yet?
key:
- (a) the wheels spin up until the motor is at the duty ceiling (or a speed where drag equals the asked torque); Iq settles at the small current that just covers the drivetrain drag, not the throttle request
- (a) Id ≈ 0 in both cases: FW and MTPA off, id_ref = 0
- (b) standstill, ωe = 0: Iq ≈ 20 A, steady, as asked (current mode); torque 0.0758 × 20 ≈ 1.5 N·m at the motor; vq ≈ Rs·iq = 0.56 V, duty below 2 %
- (b) at standstill all 20 A is copper heat (≈ 17 W): keep it short; the Halls give the angle at zero speed
- the drag current of (a) with chain and rear wheels is not measured (motor alone: 1.88 A at 5480 rpm)
traps:
- "Iq follows the throttle on the stand": at the voltage limit it cannot
- "Iq = 0 at standstill because nothing turns": torque without motion still needs iq
- "Id is negative to weaken the field": field weakening is off
solution:
(a) The light load lets the motor spin up until it hits the duty ceiling, so the current loop can no longer push the asked current: Iq falls to whatever the drivetrain drag needs. That is a few amps, not measured with the chain on (motor alone: 1.88 A at 5480 rpm). Id stays near 0. (b) Brake on, speed zero: no back-EMF, so Iq sits at the asked 20 A (≈ 1.5 N·m at the motor) with vq ≈ 0.56 V, under 2 % duty. Id ≈ 0. All 17 W goes to heat in the copper: keep it short. The Halls give the angle at zero speed.
:::

:::q id=c2 kind=error
A colleague says: "With id = 0 the motor needs no voltage on the d axis, so vd = 0. The VESC's d-axis PI only matters in field weakening." Where is he wrong? Use your 4000 rpm numbers.
key:
- vd = Rs·id + Ld·did/dt − ωe·Lq·iq: with id = 0 the cross-coupling term remains
- at 4000 rpm and iq = 40 A, vd = −5.67 V, a quarter of |v|
- the d-axis PI must create those volts to hold id at 0; with decoupling off, its integrator does it
- if the d loop were open, the cross term would drive id away from 0 and tilt the current off the q axis
solution:
The cross-coupling term: vd = −ωe·Lq·iq = −5.67 V at 4000 rpm and 40 A, about a quarter of the 23 V total. id = 0 does not mean vd = 0. The d PI must supply those volts all the time, more at higher speed and current, and your VESC does it without feedforward (decoupling off), only with its integrator. Without it, id would drift away from zero.
:::

## Close {#close}

:::q id=z0 kind=explain
Explain it as you would to an interviewer, in at most 5 lines: what Park does, what id and iq mean on your rotor, and why your VESC works in dq instead of on the three phase currents.
key:
- Park rotates the αβ frame by the rotor angle θe; in steady state the currents become constant (id, iq)
- d axis through the magnet, q 90° electrical ahead; iq makes torque (Te = 1.5·p·λm·iq, 0.0758 N·m/A), id strengthens or weakens the magnet flux; VESC holds id = 0
- constant references let two PIs work with zero steady-state error, which they cannot on 200 Hz sines
- it all depends on the angle (Halls, then observer): a wrong angle mixes id and iq and loses torque
solution:
Park rotates the stator-fixed current arrow into a frame glued to the rotor, using the electrical angle θe. On my rotor, d goes through a magnet and q sits between magnets. iq makes the torque, 0.0758 N·m per amp; id only strengthens or weakens the magnet's flux, so my VESC holds it at zero. In that frame the 200 Hz sines are constants, so two simple PIs regulate them with no error. The price is the angle: Halls at low speed, an observer above, and an error in it mixes id and iq.
:::

:::q id=z1 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
