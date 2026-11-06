---
id: C02-L2
cycle: C02
title: The field that rotates
date: 2026-11-03
minutes: 60
lede: Eighteen slots of copper that never move, three currents that only go up and down, and still a magnetic field that turns at constant strength and drags your rotor with it. This is the door to motor control.
sources: Hughes & Drury, Electric Motors and Drives, 5th ed. §1.3, §5.2, §8.2, §9.3
---

## Predict {#predict}

Two from L1 first, from memory: recalling costs more than rereading, which is why it sticks. Then two guesses about today, with your reason.

:::q id=r1 kind=recall
Same coil, same current (same MMF). You double the air gap. What happens to the flux density in the gap, roughly, and why?
key:
- B roughly halves
- almost all the MMF is spent crossing the gap, because air is thousands of times harder for flux than iron
- so the gap length sets B: B ≈ μ0·N·I / g
traps:
- "the flux stays the same" (the mistake he made in L1 k1)
- talking about the magnet flux "of the rotor" as fixed without the gap
solution:
B falls to about half. Air is roughly 2000 times harder for flux to cross than iron, so nearly all of the coil's MMF (N·I) is used up in the gap: B ≈ μ0·N·I / g. Double g, half B. This is why motor gaps are as thin as the mechanics allow.
:::

:::q id=r2 kind=recall
Your quad cruises on the flat with a fixed average voltage on the motor (throttle not moving, voltage mode). A hill starts. In order: what happens to speed, back-EMF and current? Where does it settle?
key:
- the extra load torque slows the motor: speed drops
- back-EMF E = λ·ω drops with speed
- with fixed V, current I = (V − E)/R rises because V − E grows
- more current gives more torque; it settles where motor torque equals the new load, at a lower speed
traps:
- "the current stays the same" (L1 c1 mistake): that is current mode, not voltage mode
- "the back-EMF drops because the load rises" without the speed link
solution:
Speed drops, so back-EMF (E = λm·ω) drops, so the voltage left to push current (V − E) grows and the current rises. Torque rises with current until it matches the hill: a new balance at lower speed and higher current. In your VESC it is different: in current mode the throttle sets the amps, so on the hill the torque stays the same and only the speed falls.
:::

:::q id=p1 kind=predict
One coil fed with alternating current. Does its magnetic field rotate, or does it only change size and direction?
key:
- it does not rotate: it pulsates along one fixed axis (grows, goes to zero, reverses)
- rotation needs several coils displaced in space and fed with currents displaced in time
traps:
- "it rotates because the current alternates"
solution:
It does not rotate. It grows, falls to zero and reverses, always along the same axis: a pulsating field. Rotation needs coils spread around the bore and currents shifted in time (idea 3).
:::

:::q id=p2 kind=predict
Your motor has 6 magnets (3 pole pairs). If the stator field does one full electrical turn, how far does the rotor turn?
key:
- one third of a turn (120° mechanical)
- one electrical turn covers one N–S pair; with p = 3 a mechanical turn is 3 electrical turns: θe = p·θm
solution:
A third of a turn. One electrical cycle moves the field by one north–south pair; your rotor has three pairs, so θe = 3·θm (idea 4).
:::

## Core: six ideas on your motor {#core}

Each idea starts from the real part in your motor, then gives the law. On a wide screen the motor on the right follows the idea you are reading; on a phone, press the button.

### Open your motor: steel, copper, magnets and a gap of air

Cut your motor in half like a sausage and look at the cut. From outside in: a **stack of thin steel sheets** (laminations, each about 0.35 mm, insulated from each other so eddy currents cannot circulate). Their inner edge is a comb: **teeth** and **slots**. In the slots sits the **copper** of the three phases. Then a thin ring of **air**: the air gap, under a millimetre in a motor this size. Then the **rotor**: another lamination stack with **magnets buried inside it**, small air pockets at their ends (**flux barriers**), and the shaft.

Why a gap at all? The rotor must spin, so it cannot touch the stator. And that thin ring of air is the most important dimension in the machine: the flux from the magnets and from the copper has to jump it twice on every loop (out of one tooth, back into another), and air is about 2000 times harder for flux to cross than steel.

= reluctance = length / (μ0 · μr · area)    μr: steel ≈ 2000, air = 1, magnet ≈ 1.05

> A magnet looks like air to the stator (μr ≈ 1). Flux that the stator pushes along the magnet axis (d axis) has to cross the magnet; flux pushed between magnets (q axis) goes through steel. Harder path, lower inductance: that is why your Ld = 99 µH is lower than your Lq = 113 µH.

:::scene phases=0 labels=on field=off currents=off vectors=off spin=off rotor=on endturns=true caption="Turn it with the mouse. Labels on: find the teeth, the air gap, a buried magnet and its flux barrier."
Labels on, no current.
:::

:::q id=i1 kind=calc
Flux from one magnet crosses a 0.8 mm gap twice per loop and runs about 100 mm through steel with μr = 2000. Which part needs more MMF, and about how many times more? Same cross-section everywhere, for simplicity.
key:
- reluctance is proportional to length / μr
- air: 2 × 0.8 mm = 1.6 mm of air
- steel: 100 mm / 2000 = 0.05 mm of "equivalent air"
- the gap needs about 30 times more MMF than all the steel
traps:
- forgetting the gap is crossed twice
- saying the steel needs more because it is longer
solution:
Gap: 2 × 0.8 = 1.6 mm of air. Steel: 100 mm / 2000 = 0.05 mm of equivalent air. The gap needs about 1.6 / 0.05 ≈ 32 times more MMF. The steel is a nearly free road; the gap is the toll.
:::

src: Hughes §1.3, pp. 7–15 (magnetic circuit and air gap)

### Three phases, three sines 120° apart, that always add to zero

Look at the slots of your motor going round: U+, W−, V+, U−, W+, V−, and the pattern repeats three times (once per pole pair). "U−" means the same U copper coming back the other way: a U coil goes down one slot and back up three slots later. Each phase owns 6 of the 18 slots.

The three phase currents are the same sine, shifted by a third of a cycle. At every instant they add to zero: each wire is the return of the other two, so no neutral wire is needed.

= iU + iV + iW = 0    iU = Î·cos ωt,  iV = Î·cos(ωt − 120°),  iW = Î·cos(ωt − 240°)

:::scene phases=3 currents=on field=off labels=off vectors=off speed=0.08 rotor=on caption="Copper glows with the size of its phase current. ⊙ current comes towards you, ⊗ goes away. Watch the ⊙ group walk round."
Currents on, slow.
:::

:::q id=i2 kind=check
At the instant iU is at its positive peak Î, what are iV and iW? Reason it, do not recall it.
key:
- both are −Î/2
- cos(−120°) = cos(−240°) = −½
- they add to zero with iU
solution:
−Î/2 each: cos(−120°) = cos(−240°) = −½. Î − Î/2 − Î/2 = 0, as it must.
:::

src: Hughes §5.2.1, p. 165

### One phase pulses; three phases rotate

Feed only phase U. Each U slot pushes flux across the gap, but always at the same places: the field grows, dies and reverses, on fixed axes. It pulsates.

Now feed all three. Each phase pushes along its own axis with its value at that instant, and the sum is one field pattern of constant strength, 1.5 times the peak of one phase, that turns at constant speed. It needs two shifts at once: 120° electrical in space (where the coils sit) and 120° in time (when each current peaks). Swap two wires and it turns the other way.

:::scene phases=1 field=on currents=on labels=off vectors=off speed=0.15 rotor=off caption="Only U. The arrows in the gap grow and shrink in place. Nothing travels."
Only phase U.
:::

:::scene phases=3 field=on currents=on labels=off vectors=off speed=0.15 rotor=off caption="U, V and W. Same arrows, now a pattern that travels round the gap at constant size."
All three phases.
:::

:::q id=i3 kind=check
What would happen if the three coils sat in the same slots, with the currents still 120° apart in time?
key:
- the three fields would be on the same axis
- they would add to zero at every instant, because iU + iV + iW = 0
- no field at all: the time shift is useless without the space shift
solution:
Their fields would lie on the same axis and add to zero all the time, because the currents add to zero. No field. You need both shifts.
:::

src: Hughes §5.2.2–5.2.3, §8.2.1, figs. 5.8 and 8.2

### An electrical turn is a third of a mechanical turn

Count the norths in the gap pattern: three, because your stator is wound for 3 pole pairs to match the 6 magnets. One electrical cycle of the currents moves the pattern by one north–south pair, which is a third of the circumference. So your currents must cycle three times for one turn of the shaft.

= fe = p · rpm / 60    ωe = p·ωm    θe = p·θm

:::scene phases=3 field=on currents=off vectors=on labels=off speed=0.15 rotor=on delta=90 caption="Count the three norths. Follow one: it needs three electrical cycles to go all the way round."
Field plus axes.
:::

:::q id=i4 kind=calc
Your motor at 4000 rpm: what frequency do the phase currents have? How many 30 kHz PWM periods fit in one electrical cycle?
key:
- fe = 3 × 4000 / 60 = 200 Hz
- 30 000 / 200 = 150 PWM periods per electrical cycle
- plenty to build a decent sine
solution:
fe = 3 · 4000 / 60 = 200 Hz. 30 000 / 200 = 150 PWM periods per cycle: plenty for a smooth sine. Hughes counts poles (2p) and writes 120·f / poles: the same thing.
:::

### The rotor follows the field like a compass needle

The buried magnets are another field. Like a compass needle, the rotor wants its north axis to point along the stator field. Torque depends on the angle δ between the two: zero when aligned, maximum at 90°, zero again at 180°.

= T ∝ Φmagnet · Φstator · sin δ    in dq terms: all current on q, δ = 90°

This is a synchronous motor: there is average torque only if the field turns exactly with the rotor. To hold δ at 90° the controller must know where the rotor is at every instant. In your motor, the three Hall sensors at the back (40° mechanical apart, which is 120° electrical) give that at start-up; then the VESC estimates it.

:::scene phases=3 field=on currents=off vectors=on labels=off speed=0.12 rotor=on delta=90 caption="Accent arrow: the stator field. Green arrow: a rotor north. Move δ with the slider and watch the torque-per-amp readout."
Move δ.
:::

:::q id=i5 kind=calc
The rotor position estimate is off by 30° electrical. How much torque do you lose per amp? And if it is off by 90°?
key:
- torque ∝ sin δ: with 30° error, δ = 60° or 120°, sin = 0.87: you lose about 13 %
- with 90° error, sin 0° = 0: no torque, all the current only heats the copper
- the rotor angle is the most critical measurement of the control
solution:
sin 60° ≈ 0.87: about 13 % less torque per amp. With 90° of error, sin 0° = 0: zero torque and all the current goes into heat. That is why the rotor angle matters more than any other signal.
:::

src: Hughes §9.3.2, p. 318; §9.5.1, pp. 342–344

### Clarke: three currents become one arrow, two numbers

Instead of following three currents, follow their effect: the field arrow of idea 3. Add the three phases along their axes and scale by ⅔, so the arrow is as long as one phase peak. The arrow lives in a plane, so two numbers are enough: α along phase U, β 90° ahead. It holds at every instant, transients included.

= iα = iU (when the three add to zero)    iβ = (iV − iW) / √3

:::lab clarke
Three currents become one arrow
:::

:::q id=i6 kind=calc
100 A peak currents at ωt = 120°. Compute iU, iV, iW, then iα, iβ, the length and the angle of the arrow. What does the result check?
key:
- iU = −50 A, iV = 100 A, iW = −50 A
- iα = −50 A, iβ = 150/√3 = 86.6 A
- length 100 A = the peak, angle 120° = ωt
traps:
- using sin instead of cos for the phases
solution:
iU = −50 A, iV = 100 A, iW = −50 A, so iα = −50 A and iβ = 150/√3 = 86.6 A. Length 100 A, angle 120°. The arrow sits where the time says and is as long as the peak says.
:::

src: Hughes §8.2.1–8.2.2, fig. 8.3, pp. 262–266

## Lab: touch it {#lab}

Write your prediction before you press. If it surprises you, say why in the same box.

:::q id=l1 kind=lab
In the motor: press "U only", then "U, V, W", with the gap field on. Before pressing: what do you expect in each case? Does the size of the biggest arrows change?
key:
- U only: the arrows grow and shrink in place, nothing travels (pulsating)
- U, V, W: the pattern travels round and the peak keeps the same size
- the peak with three phases is 1.5 times the peak of one
solution:
U only: arrows grow and shrink without moving. Three phases: the pattern travels and the peak keeps its size, 1.5 times the single-phase peak.
:::

:::q id=l2 kind=lab
Press "Swap V and W". Predict first: what changes in the field, and what would the quad do if you swapped two motor wires on the real VESC?
key:
- the field turns the other way
- the motor runs backwards for the same command
- on a real VESC the detection or direction setting fixes it; Hall order must match
solution:
The field reverses direction, so the motor spins the other way for the same command. On the real quad you either swap back or invert the direction in the VESC; the Hall sensor order must match the phase order or start-up fails.
:::

:::lab hexagon
The hexagon and the two circles
:::

:::q id=l3 kind=lab
Bus at 52 V. Raise the asked voltage until the arrow turns red, at 0° and at 30°. Where can you go further? Why is only the circle usable if you want sine currents?
key:
- the corners (0°, 60°…) reach further than the middle of the sides (30°…)
- only the inscribed circle, radius Vbus/√3 = 30 V, is reachable at every angle
- following the hexagon would change the arrow length as it turns: not a sine, harmonics and torque ripple
solution:
At the corners you reach 34.7 V, between them only 30 V. For a sine the arrow must keep its length all the way round, so only the inscribed circle counts: Vbus/√3 = 30.0 V peak with your 52 V bus, 15 % more than the 26 V of sine PWM.
:::

src: Hughes §2.4.3, p. 71; §8.6.1, pp. 287–290

## Judgement {#judgement}

Reason from what you know is true, not from what sounds familiar.

:::q id=c1 kind=case
Phase W breaks open: iW = 0, so iV = −iU. What does the current arrow do? Does it rotate? What happens to a motor at standstill trying to start like this? And to one already running?
key:
- iα = iU and iβ = −iU/√3: the arrow stays on one line and only changes length and sign
- it pulsates, like a single phase
- at standstill: no average torque, it does not know which way to go, it only vibrates
- already running: a pulsating field is two half fields turning opposite ways; the one turning with the rotor still gives torque, so it can keep running with less torque and strong ripple at twice the electrical frequency
solution:
iα = iU, iβ = −iU/√3: the arrow stays on one line (at −30°) and only grows, shrinks and reverses. It pulsates. Stopped: zero average torque, so it does not start, it vibrates. Running: the pulsating field splits into two half-fields turning opposite ways; the forward one keeps giving torque, so it keeps running with less torque and ripple at twice the electrical frequency.
:::

:::q id=c2 kind=error
A colleague says: "Clarke turns three currents into two numbers, so it loses information. That is why the inverter has to measure all three phases." Where is he wrong?
key:
- in a star motor with no neutral connected, iU + iV + iW = 0 always (Kirchhoff at the star point)
- the third current is not new information: it follows from the other two
- Clarke loses nothing; two sensors are enough
- a third sensor is useful for fault detection: if the sum is not zero, something is wrong
solution:
With the star point not connected, Kirchhoff forces iU + iV + iW = 0. The third current carries no new information, so Clarke loses nothing and two current sensors are enough. A third one is for fault detection: if the sum is not zero, something leaks.
:::

## Close {#close}

:::q id=z0 kind=explain
Explain it as you would to an interviewer, in at most 5 lines: how do 18 slots of copper that never move, with currents that only go up and down, make a field that turns, and what does your rotor do with it?
key:
- three phases displaced 120° in space and fed 120° apart in time
- each pulsates on its axis; the sum is one field of constant size that rotates
- p = 3: the field turns once per three electrical cycles
- the magnets lock to it like a compass; torque ∝ sin δ, maximum at 90°, so the controller needs the rotor angle
solution:
Three phases sit 120° apart (electrical) around the bore and carry currents 120° apart in time. Each one alone only pulsates; together they make one field of constant strength that rotates, one pole pair per electrical cycle, so a third of a turn per cycle in my p = 3 motor. The rotor magnets lock onto it like a compass; torque is maximum when the field leads the rotor by 90°, which is why the controller must know the rotor angle.
:::

:::q id=z1 kind=doubt
What is still unclear? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
