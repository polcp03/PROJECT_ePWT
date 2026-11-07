---
id: C03-SA
cycle: C03
title: Simulink A: your motor's dq model
date: 2026-11-10
slot: 1
minutes: 60
lede: Today you build the motor half of your digital twin with your own hands: two integrators, your measured Rs, Ld, Lq and λm, and the rotor spun at a fixed speed. Then you hit it with voltage steps and check three numbers you can already predict on paper.
sources: 04_model/params/motor_params.m (VESC dq equations, mcpwm_foc.c and virtual_motor.c as quoted there) · Franklin, Powell & Emami-Naeini, Feedback Control of Dynamic Systems 8e, §3.3, Fig. 3.14 (first-order time constant) · Hughes & Drury, Electric Motors and Drives 5e, §9.5.1 pp. 342–344 (torque from the q-axis current)
---

## Predict {#predict}

No theory today: you learnt it in L3a, L3b, K1 and K2. Write the numbers *before* you build. At the end you compare the model against your own predictions, not against a key you read first.

:::q id=r1 kind=recall
From C02: your VESC is in current control. Who sets the phase current: the load, or the throttle? And today the model has **voltage** as its input. Who sets the current in today's model?
key:
- in the VESC (current mode) the throttle asks for amps; the controller adjusts the voltage to get them, if there is voltage left over the back-EMF
- in today's open-loop model nobody asks for a current: the voltage you apply and the motor's own R, L and back-EMF decide it (i = (v − E)/R at steady state)
- this is why tomorrow you need a current loop: to turn a voltage-input plant into a current-input system
traps:
- "the load decides the current" in current mode (his mistake #2 in mistakes.md)
- thinking the dq model "knows" the 120 A limit: the plant has no limit, only the controller does
solution:
In the VESC the throttle asks for amps and the current loop finds the voltage. Today's model has no loop: you apply a voltage and the current is whatever R, L and the back-EMF make it (steady state i = (v − E)/R). Closing the loop tomorrow is what turns this voltage-driven plant into the current-driven one your VESC gives you.
:::

:::q id=p1 kind=predict
Rotor locked (ωe = 0). You apply vq = 1 V as a step, vd = 0. Predict: final iq, time constant, and iq after one time constant. Use Lq = 112.77 µH and Rs = 28.02 mΩ.
key:
- final iq = 1 V / 28.02 mΩ = 35.7 A
- τq = Lq / Rs = 112.77 µH / 28.02 mΩ = 4.02 ms
- after one τ: 63 % of 35.7 A = 22.6 A
- id stays at 0: with ωe = 0 there is no cross-coupling between the axes
traps:
- using Ld for the q axis
- "τ = 3.82 ms" copied from the comment in motor_params.m: that comment is wrong (Judgement)
- forgetting milli in mΩ and getting 35 mA
solution:
iq∞ = 1 / 0.02802 = 35.7 A. τq = 112.77e-6 / 0.02802 = 4.02 ms. At t = τ, iq = 0.632 × 35.7 = 22.6 A. id stays 0 because the coupling terms ωe·L·i vanish at standstill.
:::

:::q id=p2 kind=predict
Rotor spun at 4000 rpm by a dyno. What peak phase back-EMF do you expect? And the torque at iq = 50 A, id = 0?
key:
- ωe = p · 2π · 4000 / 60 = 3 × 418.9 = 1256.6 rad/s
- E = ωe · λm = 1256.6 × 0.016855 = 21.2 V peak phase (amplitude-invariant: it is what vq must supply)
- Te = 1.5 · p · λm · iq = 1.5 × 3 × 0.016855 × 50 = 3.79 N·m
- with id = 0 the reluctance term (Ld − Lq)·id is zero
traps:
- using mechanical rad/s (418.9) and getting 7.1 V
- forgetting the 1.5 or the p in the torque
- giving the line-to-line value (×√3 = 36.7 V): the dq model speaks peak phase
solution:
ωe = 3 × 4000 × 2π / 60 = 1256.6 rad/s, so E = 1256.6 × 0.016855 = 21.2 V peak phase. Te = 1.5 × 3 × 0.016855 × 50 = 3.79 N·m (Kt = 0.0758 N·m/A).
:::

## Build {#build}

Rule from `04_model/CLAUDE.md`: **you place the blocks**, the agent does not. Numbers live in `params/motor_params.m`; blocks reference variables (`mot.Rs`), never literals. Nothing like this exists in the repo yet: `models/` has only the vehicle models `longitudinal_L1.slx` and `longitudinal_L2.slx`. Today's file is new.

### Set up the file and the parameters

Open MATLAB, `cd` to `PROJECT_ePWT/04_model`. New blank model, save it as `models/pmsm_dq.slx`. In *Model Settings → Model Properties → Callbacks → InitFcn* write `run(fullfile(fileparts(get_param(bdroot,'FileName')),'..','params','motor_params.m'))`, so every simulation loads your measured numbers fresh. Solver: `ode23t` (the electrical states are fast), max step `1e-5`, stop time `0.03`.

= Inputs: vd, vq [V], ωe [rad/s]   States: id, iq [A]   Output: Te [N·m]

Do not use the Simscape PMSM block or a Motor Control Blockset example. The roadmap rule: build it from the equations first; compare with the reference block later (C04). The difference between yours and theirs is the lesson.

src: 04_model/CLAUDE.md (rules 1 and 4) · 01_plan/roadmap.md ("Lo que cambia ahora que sé qué toolboxes tengo")

### Write the two current equations with integrators

These are the VESC firmware's equations, quoted at the top of `motor_params.m`, solved for the derivatives:

= did/dt = (vd − Rs·id + ωe·Lq·iq) / Ld
= diq/dt = (vq − Rs·iq − ωe·(Ld·id + λm)) / Lq

Build each with an **Integrator** whose output is the current, a **Sum** for the bracket and a **Gain** `1/mot.Ld` (or `1/mot.Lq`). Feed `mot.Rs·i` back from the integrator output. The cross terms are **Product** blocks of ωe with `mot.Lq·iq` and `mot.Ld·id`. Back-EMF term `ωe·mot.lambda_m` goes into the q sum with a minus sign. Name every signal (id, iq, vd, vq, we, E).

> Put the back-EMF `E = ωe·λm` on its own named line before the sum. Tomorrow you will want to see, on a scope, how much of vq is fighting the back-EMF and how much is pushing current.

### Add the torque and the inputs

Torque, from the same file: `Te = 1.5·p·(λm + (Ld − Lq)·id)·iq`. One Sum, two Products, one Gain `1.5*mot.p`.

Inputs: **Step** blocks for vd and vq (step time 1 ms, so you see the zero before), a **Constant** for ωe. Write ωe from rpm in the block: `mot.p*2*pi*rpm_test/60` with `rpm_test` defined in the workspace. One **Scope** with id, iq and Te; log the signals too (right-click → Log selected signals) so you can read numbers with the Data Inspector cursors.

src: Hughes §9.5.1, pp. 342–344 (torque proportional to the q-axis current)

### Run the three tests

1. **Locked rotor, voltage step.** `rpm_test = 0`, vd = 0, vq step 0 → 1 V. Read the final iq and the time at which iq reaches 63 % of it (measure from the step at 1 ms). Then swap: vd = 1 V, vq = 0, and read τd.
2. **Back-EMF at 4000 rpm.** `rpm_test = 4000`, vd = 0, vq = `mot.p*2*pi*4000/60*mot.lambda_m` (the voltage you predicted) from t = 0, no step. Look at id and iq. Then set vq = 0 (a short circuit at the motor terminals) and read where id and iq settle.
3. **Torque at iq = 50 A.** Back to `rpm_test = 0`. Find the vq that gives iq = 50 A at steady state, apply it, read Te.

:::lab rl
One phase is an R-L circuit
:::

src: Franklin, Powell & Emami-Naeini 8e, §3.3, Fig. 3.14 (time constant of a first-order response)

## Check {#check}

Report what *your* model gave. The grader compares it with the expected values; if they disagree, the reason is the lesson.

:::q id=k1 kind=check
Test 1: what final iq and what τq did your model give? And τd? Do they match your prediction? Paste the numbers with units.
key:
- iq final ≈ 35.7 A (1 V / 28.02 mΩ), within 1 %
- τq ≈ 4.02 ms (63 % point, 22.6 A, at about t = 5.0 ms counting the 1 ms step delay)
- τd ≈ 3.54 ms with vd = 1 V (Ld/Rs = 99.23 µH / 28.02 mΩ)
- id stays exactly 0 in the q test (ωe = 0, no coupling)
traps:
- reading the 63 % time from t = 0 instead of from the step at 1 ms (gives 5.0 ms)
- a final current that never settles: the stop time (30 ms ≈ 7τ) is fine, but a missing Rs feedback makes iq ramp without limit
- iq ending at 35.7 mA or 35 700 A: a units slip in the Gain
solution:
iq → 35.7 A, 63 % (22.6 A) reached 4.02 ms after the step: τq = Lq/Rs. With vd = 1 V, id → 35.7 A and τd = 3.54 ms. If iq ramps forever, the −Rs·iq feedback is missing; if τ is 3.5 ms in the q test, you wired Ld.
:::

:::q id=k2 kind=check
Test 2 at 4000 rpm: with vq = ωe·λm, what did id and iq do? And with vq = 0, where did they settle? What does the sign of the torque tell you?
key:
- with vq = ωe·λm = 21.2 V and vd = 0, both currents stay at about 0: the applied voltage exactly balances the back-EMF
- short circuit (vq = vd = 0): steady id ≈ −163 A, iq ≈ −32 A, |i| ≈ 166 A
- torque ≈ −2.8 N·m: negative, a brake; the shorted motor drags the dyno
- id is the big one: at speed the current is limited by ωe·Ld, not by Rs (≈ −λm/Ld = −170 A as speed grows)
traps:
- expecting short-circuit current = E/Rs = 21.2/0.028 = 756 A (ignores the inductance at 200 Hz)
- currents that grow without limit at speed: a sign error in a cross term
solution:
With vq = E, the voltage cancels the back-EMF and no current flows. Shorted, the currents settle at id ≈ −163 A, iq ≈ −32 A and Te ≈ −2.8 N·m: a braking torque. The current is limited by the reactance ωe·Ld (0.125 Ω at 4000 rpm), far above Rs, so it tends to −λm/Ld ≈ −170 A. That is more than your 120 A motor limit: a shorted phase pair at speed is a real hazard.
:::

:::q id=k3 kind=calc
Test 3: what vq did you need for iq = 50 A at standstill, and what Te did the model give? If you had to hold iq = 50 A, id = 0 at 4000 rpm open loop, what vd and vq would you need?
key:
- standstill: vq = Rs·50 = 1.40 V; Te = 3.79 N·m (Kt = 0.0758 N·m/A)
- at 4000 rpm: vq = Rs·iq + ωe·λm = 1.40 + 21.18 = 22.6 V
- and vd = −ωe·Lq·iq = −1256.6 × 112.77e-6 × 50 = −7.1 V: without it, the cross-coupling pushes id away from 0
- |v| = √(22.6² + 7.1²) = 23.7 V, under the 30 V that 52 V gives with SVPWM
traps:
- forgetting vd at speed (the "q axis only" habit)
- Te ≠ 3.79 N·m: the 1.5, the p, or λm in mWb instead of Wb
solution:
At standstill vq = 0.02802 × 50 = 1.40 V and Te = 1.5 × 3 × 0.016855 × 50 = 3.79 N·m. At 4000 rpm you need vq = 1.40 + 21.18 = 22.6 V and vd = −7.1 V to cancel the coupling term ωe·Lq·iq; |v| = 23.7 V, still inside the 30 V circle. Holding the voltages by hand against coupling and back-EMF at every speed is exactly the job the current loop takes over tomorrow.
:::

## Judgement {#judgement}

:::q id=c1 kind=error
`motor_params.m` says `tau_e_q = Lq/Rs  % 3.82 ms` and `tau_e_d  % 3.49 ms`. Your model says something else. Which one is wrong, how do you know, and what do you do about it?
key:
- the comments are wrong: 112.77 µH / 28.02 mΩ = 4.02 ms and 99.23 µH / 28.02 mΩ = 3.54 ms
- the code computes it right (Lq/Rs); only the hand-written comment is stale, probably from older L or R values
- the model agrees with the hand calculation, two independent routes
- fix the comment in a commit with the reason, so the next reader does not take 3.82 ms as truth
traps:
- trusting the comment because it is in the "source of truth" file
- changing Lq to make 3.82 ms come out
solution:
The comments are stale: Lq/Rs = 4.02 ms and Ld/Rs = 3.54 ms, and both your hand calculation and your model agree. The code is fine; only the text beside it is wrong. Fix the comment in a small commit that says why. A number written by hand in a comment is not a measurement.
:::

:::q id=c2 kind=case
A mentor asks: "Your model has the rotor at a fixed speed. Isn't that cheating? The real rotor slows down when current flows." Defend the choice or concede it, with numbers.
key:
- electrical time constants are about 4 ms; the mechanical one is J/b = 1.12 s (motor alone, measured), hundreds of times slower
- over a 30 ms current test the speed barely moves, so a fixed ωe is a good approximation for current-loop work
- it is a hypothesis with a limit: for launch, coast-down or speed control you must add J·dω/dt = Te − Tload
- say what the model does not capture: no saturation (L falls with current), no harmonics (THD 9.4 %), no iron loss, Rs at an unknown temperature
traps:
- "it is fine because everyone does it" without the time-scale argument
- forgetting that the vehicle model of C01 already has the mechanics: connect them later, not now
solution:
Defend it with time scales: the current settles in about 4 ms, the motor's own mechanics have J/b = 1.12 s, so over a 30 ms test the speed is effectively constant. Concede the limit: anything about acceleration needs J·dω/dt = Te − Tload (your C01 vehicle model). And name what the model leaves out: L that drops with current, the 9.4 % back-EMF harmonics, iron loss, and a resistance at an unknown temperature.
:::

## Close {#close}

:::q id=z0 kind=explain
In at most 5 lines, as to an interviewer: what did you build today, which three numbers did it reproduce, and what does it not capture?
key:
- a dq model of his PMSM from the VESC equations, his measured parameters loaded from a .m file
- τq ≈ 4.0 ms (and τd ≈ 3.5 ms), E = 21.2 V at 4000 rpm, Te = 3.79 N·m at 50 A
- fixed speed is valid because electrical ≪ mechanical time constants
- not captured: saturation, harmonics, temperature, the inverter
solution:
I built a dq model of my PMSM from the VESC firmware equations, with my measured Rs, Ld, Lq and λm loaded from a parameter file. It reproduces the hand calculations: τq = 4.0 ms, 21.2 V back-EMF at 4000 rpm, 3.79 N·m at 50 A of iq. Speed is held fixed, which is fine for current dynamics (4 ms against 1.1 s mechanical). It ignores saturation, back-EMF harmonics, temperature and the inverter.
:::

:::q id=z1 kind=doubt
What is still unclear, or what did Simulink do that you did not expect? Write it as it is; Claude explains it now, and it goes to the "what I don't get" part of the review.
:::
