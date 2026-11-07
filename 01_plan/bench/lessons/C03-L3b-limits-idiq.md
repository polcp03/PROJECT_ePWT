---
id: C03-L3b
cycle: C03
title: Torque, limits and the id–iq plane
date: 2026-11-05
slot: 1
minutes: 55
lede: Your quad pulls hard from standstill, stops pulling harder at about 10 km/h and runs out of speed near 37 km/h. Three different walls cause that, and all three fit on one picture: the id–iq plane of your motor.
sources: Hughes & Drury, Electric Motors and Drives, 5th ed. §9.5.1 pp. 342–344, §9.5.2 pp. 345–349, §9.6.3 pp. 358–360, §9.7.3 p. 365, §9.7.4 pp. 366–367, §8.6.1 pp. 287–290
---

## Predict {#predict}

Two of your open mistakes first, from memory. Then one guess about today, with your reason.

:::q id=r1 kind=recall
Full throttle from standstill: the VESC pushes 120 A into the motor phases. Roughly how much current comes out of the battery in the first metre, and what links the two numbers?
key:
- much less than 120 A: around 20 A at a few km/h with his numbers
- the link is power: Vbat·Ibat ≈ electrical power into the motor (plus inverter losses)
- at low speed the motor voltage is small (little back-EMF), so the power is small even with 120 A
- no factor 3 and no √3 between phase and battery current
traps:
- "battery current = phase current × 3" (his error #3)
- "120 / √3 ≈ 70 A" (his error in the 1860 A question)
solution:
About 20 A. Nothing ties the two currents directly; power does: Vbat·Ibat ≈ 1.5·(vd·id + vq·iq). At standstill the motor needs only a few volts (no back-EMF yet, just R·i), so 120 A in the phases is about 1 kW, which is only ~20 A from a 52 V battery. The inverter is a step-down converter: low voltage and high current on the motor side, high voltage and low current on the battery side.
:::

:::q id=r2 kind=recall
In current mode the throttle asks the VESC for amps. Is there any situation where the motor does NOT get the amps you ask for, even below every current limit?
key:
- yes: when there is not enough voltage left to push that current against the back-EMF
- the current controller saturates at its maximum voltage (duty limit)
- this happens at high speed, because the back-EMF grows with speed
traps:
- "the throttle always sets the current" (his error #2, half of it)
- "the load decides the current" (true only in voltage mode)
solution:
Yes. The current only flows if there is voltage to spare to push it against the back-EMF. At high speed the back-EMF ωe·λm eats almost all the voltage the inverter can make, the PI controller hits its voltage ceiling and the current falls short of the request. That is today's second wall.
:::

:::q id=p1 kind=predict
Riding flat out on flat ground, at top speed: which limit stops you going faster: the 120 A motor limit, the 40 A battery limit, or the voltage the inverter can make? One sentence of why.
key:
- the voltage limit
- at top speed on the flat the road needs little torque (tens of amps of iq, not 120)
- the battery gives only ~15 A there, far from 40 A
- the back-EMF has grown until there is no voltage left to push more current
solution:
The voltage. On the flat, rolling resistance and air need only about 1.4 N·m at the motor (≈ 18 A of iq) and the battery gives about 15 A. What stops you is that the back-EMF plus the small R·i and L·di terms reach the inverter's maximum voltage (idea 2).
:::

## Core: six ideas on your motor {#core}

Short recall from L3a: in the rotor frame your motor is two DC-like circuits, d (along a magnet) and q (90° electrical ahead). In steady state:

= vd = Rs·id − ωe·Lq·iq    vq = Rs·iq + ωe·(Ld·id + λm)    Te = 1.5·p·(λm + (Ld − Lq)·id)·iq

Every operating point of your motor is one dot on a plane with id across and iq up. Today you draw the fence around that dot.

### The current circle: 120 A is the motor's wall, not the battery's

Open VESC Tool, Motor Settings → Current: **Motor current max = 120 A**. That number limits the length of the current arrow you met in Clarke, whatever direction it points. On the id–iq plane that is a circle:

= id² + iq² ≤ 120²

Why 120 A? Heat. Copper loss is 1.5·Rs·|i|² = 605 W at 120 A in your 28 mΩ phases (MOSFETs included), and the VESC's MOSFETs and the motor winding (no temperature sensor fitted!) can only take that for seconds. With id = 0 the top of the circle is iq = 120 A, Te = 0.0758 × 120 = **9.1 N·m**, which through 92/11 and a 0.155 m wheel is about 470 N of push.

**Battery current max = 40 A** is a different wall in a different place: it lives on the DC side of the inverter. The inverter turns battery power into motor power, so the two currents are linked by power, never by a fixed factor:

= Vbat·Ibat ≈ 1.5·(vd·id + vq·iq)    (ideal inverter; real one: divide by its efficiency)

> At low speed the motor needs few volts, so 120 A in the phases costs little battery current. At high speed it needs many volts, so even modest phase current costs a lot. The 40 A wall is a power wall: about 52 V × 40 A ≈ 2.1 kW.

:::q id=i1 kind=calc
Launch: motor at 500 rpm (about 3.5 km/h), id = 0, iq = 120 A, battery at 52 V, inverter ideal. Compute ωe, vd, vq, the electrical power and the battery current. Is the battery limit active?
key:
- ωe = 3 × 500 × 2π/60 = 157 rad/s
- vd = −ωe·Lq·iq = −157 × 112.8 µH × 120 ≈ −2.1 V; vq = 0.028 × 120 + 157 × 0.01686 ≈ 3.4 + 2.6 = 6.0 V
- P = 1.5 × vq × iq = 1.5 × 6.0 × 120 ≈ 1080 W (id = 0, so vd does no work)
- Ibat = 1080 / 52 ≈ 21 A: below 40 A, battery limit not active; the 120 A circle is the wall
traps:
- 120 / √3 or 120 / 3 for the battery current (error #3)
- forgetting the 1.5 of the amplitude-invariant transform in the power
- using |v|·|i| instead of vd·id + vq·iq
solution:
ωe = 157 rad/s. vd = −2.1 V, vq = 3.4 + 2.6 = 6.0 V. P = 1.5·(vd·0 + 6.0·120) ≈ 1080 W, of which 605 W is copper loss and ~475 W goes to the shaft. Ibat = 1080/52 ≈ 21 A. So at launch the phases carry 120 A and the battery only 21 A: the motor circle is the wall, the battery has margin.
:::

src: Hughes §9.7.4, pp. 366–367 (intermittent torque region set by the converter's maximum current; I²R limit)

### The voltage circle: why your quad stops at 5480 rpm

Your VESC runs SVPWM. In L2 you found the largest round voltage arrow it can make: Vbus/√3 = **30 V peak** at 52 V. The firmware also caps the duty at 0.95, so in practice the ceiling is 0.95 × 30 = 28.5 V. Every steady operating point must satisfy

= vd² + vq² ≤ Vmax²    Vmax = 0.95·Vbus/√3

At no load (id ≈ 0, iq ≈ 0) almost all of that voltage is back-EMF, ωe·λm. So the no-load speed is where the back-EMF alone fills the circle:

= ωe,max ≈ Vmax / λm

> You measured this on 7-Sep: held at duty 0.9486 with 52.77 V on the bus, the VESC logged 16 440 ERPM (5480 rpm) and |v| = 28.9 V. λm·ωe = 0.016855 × 1722 = 29.0 V. The back-EMF had eaten the whole circle.

:::q id=i2 kind=calc
At what motor speed does the back-EMF alone reach 30 V peak? Give rpm and quad km/h (92/11, wheel 0.155 m). Compare with your measured 5480 rpm and explain the difference with numbers.
key:
- ωe = 30.0 / 0.016855 ≈ 1781 rad/s, ωm = 594 rad/s ≈ 5670 rpm
- quad speed ≈ 594 × 0.155 / 8.364 ≈ 11.0 m/s ≈ 39.6 km/h
- measured 5480 rpm is ~3.4 % lower
- main reason: duty cap 0.95 cuts the ceiling 5 % (28.5 V), partly offset by the higher bus on that day (52.77 V, +1.5 %); the rest is R·i and dead time (~0.19 V)
traps:
- forgetting the pole pairs (ωe = 3·ωm)
- using line-to-line voltage (52 V) against the phase back-EMF
- dividing by 8.364 in the wrong direction
solution:
ωe = 30.0/0.016855 = 1781 rad/s → 594 rad/s mechanical → 5670 rpm → 39.6 km/h. Measured: 5480 rpm, 3.4 % lower. The VESC stops at duty 0.95: 0.95 × 52.77/√3 = 28.9 V, and 28.9 / 0.016855 = 1715 rad/s → 5460 rpm. Add back the 0.19 V of dead time and the small R·i of 1.9 A and you land on 5480. The model and your log agree.
:::

src: Hughes §8.6.1, pp. 287–290 (SVPWM, Vbus/√3); §9.5.2, p. 345 (the voltage the inverter can produce sets base speed)

### The voltage ellipse shrinks with speed: the corner where full torque ends

Put the steady-state voltages into the voltage circle and drop the small R terms. It becomes a limit on the currents:

= (Lq·iq)² + (Ld·id + λm)² ≤ (Vmax / ωe)²

On the id–iq plane this is an **ellipse**. Its centre is at id = −λm/Ld = **−170 A**, iq = 0, because there the stator flux cancels the magnet and no voltage is needed. Its size is Vmax/ωe: huge at low speed, shrinking as you speed up. Allowed points are inside **both** the circle and the ellipse.

Full torque with id = 0 is the top of the circle, (0, 120 A). The **corner speed** (Hughes calls it base speed) is where the shrinking ellipse passes through that point. Below it you have full torque; above it the ellipse cuts the top of the circle off and the maximum torque falls.

> With 30 V and Rs included, your corner is at about 4020 rpm, 28 km/h. Without Rs the formula gives 4420 rpm: the 3.4 V of Rs·iq at 120 A is not negligible in a 30 V motor. With the 0.95 duty cap it is ~3800 rpm.

:::q id=i3 kind=calc
Compute the corner speed with id = 0, iq = 120 A and Vmax = 30 V, first without Rs. Then say in which direction Rs moves it and why. What mechanical power is that?
key:
- without Rs: ωe = Vmax / √(λm² + (Lq·iq)²) = 30 / √(0.016855² + 0.01353²) ≈ 30 / 0.02161 ≈ 1389 rad/s ≈ 4420 rpm
- Rs adds Rs·iq = 3.4 V to vq, so less voltage is left for back-EMF: corner drops to ≈ 4020 rpm (~28 km/h)
- power at the corner ≈ 9.1 N·m × 421 rad/s ≈ 3.8 kW mechanical
- Lq·iq = 13.5 mWb is comparable to λm: the q-axis inductance voltage matters at 120 A
traps:
- using Ld instead of Lq for the iq term
- adding the voltages as scalars (30 = λm·ωe + Lq·iq·ωe) instead of in quadrature
- forgetting that 3.8 kW needs ~85 A from the battery: the battery wall comes first (idea 6)
solution:
Without Rs: |λ| = √(16.86² + 13.53²) mWb = 21.6 mWb, ωe = 30/0.0216 = 1389 rad/s → 4420 rpm. With Rs, vq gets an extra 3.4 V, so the corner falls to ≈ 1264 rad/s → 4020 rpm, 28 km/h. Power ≈ 9.1 N·m × 421 rad/s ≈ 3.8 kW. Hold that number: 3.8 kW plus 0.6 kW of copper is about 85 A from a 52 V battery, more than twice the 40 A wall.
:::

src: Hughes §9.5.2, pp. 345–347, figs. 9.20–9.21 (full torque up to base speed, voltage ∝ speed below it)

### Constant-torque curves and MTPA: why id = 0 is right for you

Pick a torque, say 5 N·m, and draw every (id, iq) that gives it. From the torque equation, iq = Te / (1.5·p·(λm + (Ld − Lq)·id)). In a motor with strong saliency these curves bend a lot and a negative id buys extra **reluctance torque**. Yours has Ld − Lq = −13.5 µH against λm = 16.9 mWb, so the bracket barely changes: 5 N·m needs 65.9 A of iq at id = 0 and 62.9 A at id = −60 A. The curves are almost horizontal lines.

**MTPA** (maximum torque per ampere) means: for each current size, choose the angle that gives the most torque. At 120 A your best point is id ≈ −11 A, iq ≈ 119.5 A: **9.14 N·m instead of 9.10, a 0.5 % gain**. That is less than the 14 % uncertainty of your rotor inertia and well inside the saliency's own drift with current. Hughes shows the same for a non-salient machine: with the current in phase with the back-EMF (id = 0) you get the most torque per amp and the least copper loss.

> That is why your VESC runs `foc_mtpa_mode = 0`, id_ref = 0 always. A table for a 0.5 % gain, built on an Lq − Ld that moves with current, is not worth it.

:::q id=i4 kind=calc
Keep |i| = 120 A and compare id = 0 with id = −40 A. Compute the torque of each. Then: is the "reluctance torque" worth it on your motor?
key:
- id = 0, iq = 120 A: Te = 1.5 × 3 × 0.016855 × 120 = 9.10 N·m
- id = −40 A, iq = √(120² − 40²) = 113.1 A: Te = 1.5 × 3 × (0.016855 + 13.54e-6 × 40) × 113.1 ≈ 8.86 N·m
- id = −40 A loses 2.7 %: the reluctance term (+0.54 mWb) is smaller than what iq loses
- the true optimum is id ≈ −11 A for +0.5 %: not worth it; id = 0 is correct
traps:
- the sign: (Ld − Lq)·id is positive only for negative id, because Ld < Lq
- comparing at the same iq instead of the same |i| (that hides the extra current and heat)
solution:
id = 0: 9.10 N·m. id = −40 A: iq = 113.1 A, flux term 16.855 + 0.54 = 17.40 mWb, Te = 8.86 N·m, 2.7 % LESS for the same amps. The reluctance torque is real but tiny, while the iq you give up is not. The optimum (id ≈ −11 A) gains 0.5 %. On your motor, id = 0 is MTPA for all practical purposes.
:::

src: Hughes §9.5.1, pp. 342–344 (torque from the current component at right angles to the magnet flux; Id = 0 gives maximum torque per ampere)

### Field weakening: negative id pushes the ellipse, and you pay in current

Look at the ellipse again: its centre is at id = −170 A. If you move the operating point to the left (negative id), the stator flux partly cancels the magnet: Ld·id + λm shrinks, so the back-EMF the inverter has to fight shrinks too, and the same 30 V reaches a higher speed. That is **field weakening**. Hughes's warning is the important part: most of the current is then "wasted" opposing the magnet, so it is only good for short bursts.

= flux the inverter sees on d: λm + Ld·id    id = −30 A → 16.86 − 2.98 = 13.88 mWb (−18 %)

What it would buy you: with id = −30 A the no-load speed at 30 V rises from 5670 to about 6890 rpm (+21 %). What it costs:

- **Current.** That −30 A flows all the time, also when you only cruise, and it comes out of the same 120 A circle. Copper loss grows with |i|².
- **The magnets.** Negative id is a field pushing against them. Hot magnets and strong opposing field are how a PM motor demagnetises, and your motor has **no temperature sensor**.
- **Loss of control.** At 6800 rpm the magnet alone makes 62 V line-to-line peak against a 52 V bus. If the controller trips, the inverter diodes rectify that into the battery: uncontrolled braking and an over-voltage on the bus.

> Your VESC has `foc_fw_current_max = 0`: field weakening is OFF. Every top speed you have ridden is the natural one of the magnet and the bus.

:::scene phases=3 field=on currents=off vectors=on dq=on labels=off rotor=on spin=on speed=0.1 delta=120 caption="Stator field 120° ahead of the rotor instead of 90°: part of the current now points against the magnet's d axis. That part makes no torque; it only cancels flux."
Field weakening seen from the rotor.
:::

:::q id=i5 kind=case
A friend says: "Just set Field Weakening Current to 40 A in VESC Tool and the quad goes 25 % faster, free." You are in VESC Tool. What do you answer, and what would you need to have in place before even trying it?
key:
- it is not free: the extra −id adds to |i| and copper loss at every high-speed point, and eats into the 120 A circle
- demagnetisation risk with no motor temperature sensor fitted
- loss of control above ~5700 rpm: back-EMF above the bus, uncontrolled current through the diodes into the battery (BMS regen limit 35 A)
- before trying: a motor temperature sensor, a requirement with a number (how much speed, for how long), a test with the wheels off the ground and current/temperature logged, and a decision on what happens on a fault
traps:
- "it is software, so it cannot break anything"
- thinking field weakening adds power: it adds speed, at roughly the same or more current
solution:
Not free. Every amp of negative id is current that makes no torque, adds copper loss and takes room from the 120 A circle; Hughes says FW in a PM motor is intermittent for this reason. It pushes against hot magnets in a motor with no temperature sensor. And above ~5700 rpm a controller trip leaves a back-EMF higher than the bus, which pumps current through the diodes into the battery. Before trying: a temperature sensor on the winding, a requirement (speed gain, duration), and a wheels-up test with current, temperature and bus voltage logged.
:::

src: Hughes §9.5.2, pp. 347–349, fig. 9.22 (field weakening needs current above rated; most of it opposes the magnet); §9.6.3, pp. 358–360 (FW loop, overvoltage on loss of control); §9.7.3, p. 365 (demagnetisation and efficiency cost)

### Your quad on the plane: launch, hill and flat top speed

Now put the three walls together. The battery wall is not a circle on this plane, but you can draw it: for each speed, the points where 1.5·(vd·id + vq·iq) = 52 V × 40 A. As speed rises the same iq needs more voltage and more power, so the battery wall comes down from above.

With your numbers (ideal inverter, 52 V, Crr 0.03 and CdA 0.6 assumed, wheel 0.155 m assumed):

- **Launch, 0 → ~11 km/h.** Dot at the top of the circle, (0, 120 A). The battery gives 21 A at 3.5 km/h and reaches 40 A at about 1550 rpm, **10.8 km/h**.
- **Above ~11 km/h with full throttle.** The battery wall pushes the dot down the iq axis: at 25 km/h only 67 A (5.1 N·m) fit in 2.1 kW. The 28 km/h corner of the current circle is never reached: the battery cuts torque first.
- **Flat, top speed.** Road load needs only ~18 A of iq. The dot sits low on the iq axis while the ellipse shrinks onto it at about **5250 rpm, 36.7 km/h**. Battery about 15 A. Voltage is the wall.

> Your own baseline says it: "at launch the motor-current limit is reached, then duty becomes the limit as speed rises", and battery peaks ~40 A. Today's plane predicts a battery-limited stretch in between. Your CAN logger can check it: look for Ibat flat at 40 A while iq falls.

:::q id=i6 kind=case
You ride up a long 20 % hill with full throttle. Which limit holds you, at what speed, roughly, and how would you prove it from a VESC log? Then the same question on the flat at top speed.
key:
- 20 % hill: the battery wall, at about 25 km/h, iq ≈ 67 A; voltage still has margin (|v| ≈ 22.5 V of 28.5 V)
- proof on the hill: Ibat sits at 40 A while iq is below 120 A and duty below 0.95
- flat: the voltage wall at ~37 km/h, iq ≈ 18 A, Ibat ≈ 15 A
- proof on the flat: duty at 0.95 while iq is below what the throttle asks and Ibat far below 40 A
traps:
- "the 120 A motor limit on the hill" (only true at very low speed or a very steep hill)
- judging the limit by feel instead of by which logged signal is pinned at its ceiling
solution:
Hill: road load at 25 km/h on 20 % needs ~67 A of iq, which costs 1.5·vq·iq ≈ 2.1 kW: the battery wall. The voltage is only at 22.5 V of 28.5 V and iq is far from 120 A. In the log: Ibat flat at 40 A, duty below 0.95. Flat: only ~18 A of iq and ~15 A from the battery, but duty pinned at 0.95: voltage. The rule: the limit is the signal that sits flat at its ceiling.
:::

## Lab: touch it {#lab}

Write your prediction before you move the slider. If it surprises you, say why in the same box.

:::lab idiq
The id–iq plane of your motor
:::

:::q id=l1 kind=lab
Start at low speed with the operating point at (0, 120 A). Predict the speed at which the ellipse starts to cut that point off, then raise the speed slider until it does. What do you read, and does it match idea 3?
key:
- the prediction: about 4000 rpm with Rs, 4400 rpm without
- above that speed the point (0, 120 A) falls outside the ellipse: full torque is no longer possible with id = 0
- the maximum torque then falls along the top edge of the ellipse
- reading within a few % of the hand calculation (the lab's model choices, e.g. R included or not, explain the rest)
solution:
The ellipse passes through (0, 120 A) at about 4000 rpm with Rs (4400 without). Above it the top of the circle is outside the ellipse, so with id = 0 the most you can get is where the ellipse crosses the iq axis, which falls with speed. That is the corner speed of idea 3.
:::

:::q id=l2 kind=lab
Keep raising the speed. At what speed does the ellipse no longer contain the origin (0, 0)? What does that mean physically, and where is the ellipse's centre when it happens?
key:
- around 5670 rpm with 30 V: back-EMF alone equals Vmax
- above it, even zero current needs more voltage than the inverter has: the no-load speed
- the centre stays at id = −λm/Ld ≈ −170 A, outside the 120 A circle
- so with id = 0 nothing is possible above it; only negative id (field weakening) keeps points inside
solution:
About 5670 rpm (39.6 km/h): the back-EMF alone fills the 30 V circle, so the motor cannot even hold zero current there. The ellipse keeps shrinking around its centre at id = −170 A, outside the current circle, so only points with negative id survive above that speed: field weakening, which your VESC has off.
:::

## Judgement {#judgement}

Reason from the plane, with numbers. A feeling is not an answer.

:::q id=c1 kind=case
On the same flat road, your top speed is clearly lower when the VESC reads 44 V than when it reads 54 V. Explain it with the id–iq plane and give both top speeds. Is it the battery current limit? What else changes near 44 V?
key:
- Vmax = 0.95·Vbus/√3: 29.6 V at 54 V, 24.1 V at 44 V (−19 %)
- the ellipse size is Vmax/ωe, so at 44 V it shrinks onto the low road-load point at a lower speed: ~38 km/h at 54 V vs ~31 km/h at 44 V (≈ 5450 vs 4450 rpm)
- not the battery limit: at top speed Ibat is only ~12–15 A
- near 44 V the VESC's low-voltage fold-back begins (44.2 → 39 V), which cuts current and hurts acceleration; and the pack sags 0.18 Ω × Ibat under load, so the VESC sees less than the resting voltage
traps:
- "less power available, so less speed": the battery is far from 40 A at top speed; it is voltage
- forgetting the duty cap or the √3 and comparing back-EMF with 44 V directly
solution:
Top speed on the flat is the voltage wall. The ellipse is Vmax/ωe in size, and Vmax = 0.95·Vbus/√3 drops from 29.6 V to 24.1 V. The road needs only ~15–19 A of iq, so the dot sits low on the iq axis, and the smaller ellipse reaches it sooner: about 38 km/h (5450 rpm) at 54 V, about 31 km/h (4450 rpm) at 44 V. Top speed scales almost with bus voltage. The battery gives only 12–15 A there, so its 40 A limit has nothing to do with it. Near 44 V two more things: the VESC's fold-back starts at 44.2 V and scales current down (felt in acceleration), and the pack's 0.18 Ω drops ~2.7 V at 15 A, so the bus the VESC uses is lower than what you read at rest. These top speeds lean on Crr, CdA and r_roll, all still assumed.
:::

:::q id=c2 kind=error
A forum post says: "Your BMS is 40 A and your motor limit is 120 A. 120/√3 = 69 A from the battery, so you trip the BMS at every launch. Set motor current to 69 A." Where is he wrong, and what would that change cost you?
key:
- phase and battery current are not linked by √3 (or 3): they are linked by power, Vbat·Ibat ≈ 1.5·(vd·id + vq·iq)
- at launch the motor voltage is a few volts: 120 A in the phases costs ~21 A from the battery (idea 1)
- the battery hits 40 A only from about 11 km/h, and the VESC's own 40 A input limit handles it by reducing iq
- cutting motor current to 69 A would throw away ~43 % of launch torque (9.1 → 5.2 N·m) for no battery benefit
traps:
- accepting √3 because it appears in line vs phase voltage (a different thing)
solution:
√3 relates line and phase voltages of a star winding; it has nothing to do with DC versus AC current. Power links them: at launch the phases need ~6 V, so 120 A is ~1.1 kW, ~21 A from 52 V. The BMS never sees 69 A at launch; the battery reaches 40 A only near 11 km/h, where the VESC's battery limit (also 40 A) trims iq by itself. Setting 69 A would cost 43 % of launch torque and gain nothing.
:::

## Close {#close}

:::q id=z0 kind=explain
Explain it as you would to an interviewer, in at most 5 lines: what limits your quad's torque and speed, and where each limit shows up on the id–iq plane?
key:
- current circle 120 A (heat, MOSFETs): sets launch torque, 9.1 N·m
- battery 40 A is a power limit (~2.1 kW), not a circle: binds from ~11 km/h at full throttle, so the 28 km/h corner is never reached
- voltage ellipse, size Vmax/ωe with Vmax = 0.95·Vbus/√3: sets top speed (~37 km/h on the flat), scales with bus voltage
- id = 0 because saliency is tiny (MTPA +0.5 %); field weakening would push the ellipse but costs current and magnet risk, and is off
solution:
Three walls. The 120 A current circle (heat) gives 9.1 N·m at launch. The 40 A battery limit is a power wall, about 2.1 kW: from about 11 km/h it pulls iq down, so the motor never reaches its 28 km/h corner at full current. The voltage ellipse, Vmax/ωe with Vmax = 0.95·Vbus/√3, sets top speed: about 37 km/h on the flat, lower with a flat battery. I run id = 0 because my saliency gives MTPA only +0.5 %, and field weakening is off: it would buy speed with current, heat and magnet risk.
:::

:::q id=z1 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
