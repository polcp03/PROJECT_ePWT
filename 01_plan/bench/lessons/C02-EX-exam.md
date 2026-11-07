---
id: C02-EX
cycle: C02
title: C02 exam: from the battery to the rotating field
date: 2026-11-04
slot: 1
minutes: 45
lede: Forty-five minutes, from memory, on your own quad. Battery to torque, the field that rotates, and three judgement calls an engineer gets asked in an interview.
sources: Hughes & Drury, Electric Motors and Drives, 5th ed. §1.6–1.8, §2.2, §2.4, §5.2, §8.2, §9.3
---

From memory: no notes, no lessons, no AI. A calculator is fine. One attempt per question, equation before the number. The app grades each answer as you go and brings the misses back in Review until you get them right on two different days. Some questions look like ones you have missed before; they are not the same, so read them to the end.

## Part 1 · Battery to torque {#p1}

:::q id=a1 kind=case
Quad on the stand, rear wheels in the air, motor turning steadily. You press a brake pad against the rear wheel, harder and harder. Run it twice. (A) The VESC is in duty mode, duty held fixed. (B) The VESC is in current mode, asking a fixed 20 A. In each case: what happens to speed and to motor current, and who decides the current?
key:
- (A) fixed duty = fixed average voltage: the brake slows the motor, E = λm·ωe drops, so I = (V − E)/R rises; the load decides the current
- (A) it settles at a slightly lower speed where Kt·I equals the brake torque (R is tiny, so the speed drop is small until the current limit)
- (B) the current loop holds 20 A, so torque stays at Kt·20 ≈ 1.5 N·m whatever the brake does; only the speed falls, possibly to zero
- (B) the controller (the throttle) decides the current, as long as there is voltage left over the back-EMF to push it
traps:
- "the current is set by the torque demand" in both cases: true only in (A) (his mistake #2)
- "the current stays the same in (A)": that is current mode, not voltage mode (his mistake #15)
- "the battery decides the current"
solution:
(A) With the duty fixed the average voltage is fixed. The brake slows the motor, the back-EMF falls, V − E grows and the current rises until Kt·I matches the brake: the load sets the current, and speed drops only a little because R = 28 mΩ is tiny. (B) In current mode the VESC holds 20 A, so the torque stays at 0.0758 × 20 ≈ 1.5 N·m. If the brake asks for more, nothing pushes back: the wheel slows down and stops. The controller sets the current, provided there is voltage left above the back-EMF.
:::

:::q id=a2 kind=calc
Steep launch: the VESC holds the motor current at its 120 A limit (all on iq) while the motor turns at only 300 rpm. A friend expects the battery to give 120 × 3 = 360 A and the 40 A BMS to trip at once. Estimate the real battery current at 52 V, ignoring inverter losses.
key:
- ωm = 31.4 rad/s; torque 0.0758 × 120 = 9.1 N·m; mechanical power ≈ 286 W
- copper loss 1.5·Rs·I² = 1.5 × 0.028 × 120² ≈ 605 W
- electrical power ≈ 890 W, so Ibat ≈ 890 / 52 ≈ 17 A
- battery and phase current are linked by power, not by 3 or √3: at low speed and high torque, phase current ≫ battery current
traps:
- multiplying or dividing by 3 or √3 (his mistake #3 and #16)
- forgetting the copper loss, which here is twice the useful power
- taking the 28 mΩ as the battery resistance
solution:
ωm = 300 · 2π/60 = 31.4 rad/s. Torque 9.1 N·m, so P_mech = 9.1 × 31.4 ≈ 286 W. Copper loss 1.5 × 0.028 × 120² ≈ 605 W. The battery supplies about 890 W: 890 / 52 ≈ 17 A. The inverter steps the voltage down (the motor needs only a couple of volts here) and the current up, like a gearbox for electricity. Power is what is conserved: Vbat·Ibat ≈ 1.5·(vq·iq). No factor of 3 or √3 links the two currents.
:::

:::q id=a3 kind=calc
Wheels off, full throttle, no load. Your log from September: the motor settled at **5480 rpm** with **iq = 1.88 A**, duty at its 0.95 ceiling, battery 52.8 V. (1) What sets 5480 rpm? Compute the ideal no-load speed for a 30 V phase-voltage ceiling. (2) What sets 1.88 A? What torque does it make, and against what? (3) You raise the VESC motor current limit from 120 A to 160 A. Does either number change?
key:
- no-load speed is set by voltage: the motor accelerates until the back-EMF λm·ωe almost equals the voltage ceiling Vbus/√3 (× 0.95 max duty)
- ideal: ωe = 30 / 0.016855 ≈ 1780 rad/s, ωm = ωe/3 ≈ 593 rad/s ≈ 5670 rpm; with the 0.95 duty cap ≈ 5390 rpm at 52 V; measured 5480 rpm at 52.8 V fits
- no-load current is set by drag: Kt·iq = 0.0758 × 1.88 ≈ 0.14 N·m of bearing friction, viscous and iron losses
- the current limit changes neither: it only caps the torque at low speed; only bus voltage, λm (or field weakening, off) move the no-load speed
traps:
- "the current limit or the controller sets the no-load current"
- "at no load the current is zero": then there would be no torque against friction
- dividing by p in the wrong direction (ωm = ωe / p)
solution:
(1) Voltage. The motor speeds up until λm·ωe nearly equals what the inverter can apply: 30 V / 0.016855 Wb ≈ 1780 rad/s electrical, /3 ≈ 593 rad/s ≈ 5670 rpm. The VESC caps duty at 0.95, which gives about 5390 rpm at 52 V; you measured 5480 rpm with the pack at 52.8 V. (2) Drag. At steady speed the motor torque equals the losses: 0.0758 × 1.88 ≈ 0.14 N·m (friction, viscous drag, iron losses). The current is whatever makes that torque. (3) No. The current limit only matters when the load asks for more than 120 A. To spin faster you need more voltage, less λm, or field weakening (off in your VESC).
:::

:::q id=a4 kind=calc
Phase U, high-side transistor ON, 40 A flowing into the U winding. The PWM switches that transistor OFF. Where does the 40 A go in the next microsecond? What would happen if the lower switch of that leg had no anti-parallel diode? Put a number on it: your L ≈ 106 µH, and imagine the current forced to zero in 100 ns.
key:
- the winding is an inductor: its current cannot jump (v = L·di/dt), so it keeps flowing in the same direction
- it freewheels through the diode across the low-side switch (phase pulled to the bus minus); in dead time the diode carries it on its own
- without the diode: v = L·di/dt = 106 µH × 40 A / 100 ns ≈ 42 kV: a spike that breaks the transistor
- the same diodes return current to the bus when braking (regeneration)
traps:
- "the current stops when the switch opens" (his answer on 3-Nov)
- "the diode protects against reverse battery polarity"
- "the diode is there for shoot-through"
solution:
The winding's current cannot stop instantly, so it keeps flowing into U. With the top switch off, its only path is up through the diode across the bottom switch: the phase sits at the bus minus and the current freewheels, decaying slowly. Without that diode, forcing 40 A to zero in 100 ns would take v = 106e-6 × 40 / 100e-9 ≈ 42 000 V: the switch would break down long before. The same diodes carry the current back to the bus when you brake.
:::

src: Hughes §2.2.1–2.2.3, pp. 45–51; §2.4.1–2.4.3, pp. 62–73

:::q id=a5 kind=calc
Climbing at **3000 rpm** with **80 A** of iq. Compute: peak back-EMF per phase, torque, mechanical power, copper loss, motor efficiency, and the battery current at 52 V. Then the engineering question: can your quad hold this point?
key:
- ωm = 314 rad/s; E = p·λm·ωm ≈ 15.9 V peak; T = 0.0758 × 80 ≈ 6.07 N·m
- P_mech ≈ 1906 W; copper 1.5 × 0.028 × 80² ≈ 269 W; η ≈ 88 %
- electrical ≈ 2175 W, so Ibat ≈ 42 A at 52 V
- above the 40 A battery limit (and the pack sags about 0.18 Ω × 40 A ≈ 7 V): the VESC battery limit will cut iq below 80 A; voltage is fine (≈ 18 V needed of 30 V)
traps:
- giving the efficiency without the numbers (his mistake #17)
- forgetting the 1.5 in the copper loss of three phases
- checking only the motor 120 A limit and not the 40 A battery limit
solution:
ωm = 314 rad/s, E = 3 × 0.016855 × 314 ≈ 15.9 V, T ≈ 6.07 N·m, P_mech ≈ 1906 W, copper ≈ 269 W, η ≈ 88 %. The battery must give about 2175 W: 42 A at 52 V, more once the pack sags. That is over the 40 A battery limit, so the VESC trims iq and the quad slows on that hill. The motor limit (120 A) and the voltage (about 18 V needed against 30 V available) are not the problem; the battery is.
:::

src: Hughes §1.6–1.8, pp. 23–35

## Part 2 · The rotating field {#p2}

:::q id=b1 kind=check
A different machine: only **two** coils, 90° apart around the bore. (1) Feed them with currents 90° apart in time, Î·cos ωt and Î·sin ωt. Does the field rotate? With what strength? (2) Now feed both with the same Î·cos ωt. What does the field do?
key:
- (1) it rotates: the two components are cos and sin of the same angle, so the sum is an arrow of constant length Î turning at ω
- (2) it pulsates on one fixed axis (45° between the coils), growing, vanishing and reversing
- rotation needs both shifts: in space and in time; three phases at 120° are one way, two at 90° another
traps:
- "two coils cannot make a rotating field, you need three"
- "in-phase currents rotate because they alternate"
solution:
(1) It rotates. One coil gives Î·cos ωt along x, the other Î·sin ωt along y: that is an arrow of length Î at angle ωt. It is exactly the α–β picture of Clarke. (2) Both components are always equal, so the arrow stays on the 45° line and only grows, shrinks and reverses: a pulsating field. Space shift alone is not enough; you need the time shift too.
:::

:::q id=b2 kind=calc
Quad at 30 km/h, wheel radius 0.155 m, gear 92/11. Motor speed in rpm? Electrical frequency of the phase currents? How many Hall edges per second does the VESC see (three sensors)? Then one line: a friend says a version of your motor with more pole pairs would run smoother. What does p really change?
key:
- wheel 8.33 / 0.155 ≈ 53.8 rad/s; motor × 8.364 ≈ 450 rad/s ≈ 4290 rpm
- fe = p·rpm/60 = 3 × 4290 / 60 ≈ 215 Hz
- each Hall toggles twice per electrical cycle, three sensors: 6 edges per cycle, ≈ 1290 edges/s
- more p: more torque per amp (Kt = 1.5·p·λm) and a higher electrical frequency at the same speed; smoothness comes from sinusoidal currents and the slot/winding design, not from p
traps:
- dividing by p instead of multiplying
- "more pole pairs = smoother" (his mistake #7)
- counting one edge per Hall per cycle
solution:
8.33 m/s / 0.155 m = 53.8 rad/s at the wheel, × 8.364 = 450 rad/s ≈ 4290 rpm. fe = 3 × 4290 / 60 ≈ 215 Hz. Each Hall switches twice per electrical cycle; three of them give 6 states per cycle: about 1290 edges per second. More pole pairs buy torque per amp and raise the electrical frequency; smoothness comes from the waveform and the slots.
:::

:::q id=b3 kind=calc
The VESC measures only two phases. At one sample it reads iU = 40 A and iV = −60 A. Find iW, then iα, iβ, the length of the current arrow and its angle. Why can it get away with two sensors?
key:
- iW = −iU − iV = 20 A (star point not connected, Kirchhoff)
- iα = iU = 40 A; iβ = (iV − iW)/√3 = −80/√3 ≈ −46.2 A
- length ≈ 61 A, angle ≈ −49°
- the third current carries no new information; a third sensor would only serve fault detection
traps:
- iβ = (iV + iW)/√3 instead of the difference
- forgetting that iW must close the sum
solution:
iW = −(40 − 60) = 20 A. iα = 40 A, iβ = (−60 − 20)/√3 ≈ −46.2 A. Length √(40² + 46.2²) ≈ 61 A at −49°. With no neutral wire, iU + iV + iW = 0 always, so two sensors tell everything.
:::

:::q id=b4 kind=case
The motor is stopped. The VESC holds a fixed current arrow, iα = 50 A, iβ = 0, and does not rotate it: a DC test current, nothing more. What current does each phase carry? What does the rotor do, and where does it end up? How many positions per mechanical turn could it end up in?
key:
- iU = 50 A, iV = iW = −25 A: steady DC, the stator field points along phase U
- torque ∝ sin δ: the rotor turns until a magnet's north (its d axis) lines up with the field, where δ = 0 and torque is zero
- it is a stable lock: push it off and the torque pulls it back
- three possible rest positions per mechanical turn (p = 3), 120° mechanical apart
traps:
- "the rotor spins because there is current"
- "it stops at 90°, where torque is maximum"
- "one position per turn": there are three north poles
solution:
iU = 50 A and iV = iW = −25 A, all DC. The field points along U and does not move. The rotor turns until a north magnet sits on that axis: δ = 0, zero torque, and any push away creates a restoring torque, like a compass. With three north poles, it can lock at three places, 120° mechanical apart. That is how the VESC holds the rotor still while it measures R and L.
:::

:::scene phases=3 field=on currents=on vectors=on labels=off rotor=on spin=off delta=0 dq=on caption="A fixed field and a rotor locked with δ = 0: the d axis on the field arrow, zero torque."
Locked rotor.
:::

src: Hughes §5.2, p. 165; §8.2.1–8.2.2, pp. 262–266; §9.3.2, p. 318

## Part 3 · Judgement {#p3}

:::q id=c1 kind=case
A friend proposes a 14S pack instead of your 13S (one more cell in series, same capacity). "More voltage, more torque: it will launch harder." What part is true? Give numbers for launch torque, no-load speed and top-end power. Is there anything that worries you about 14S with your VESC?
key:
- launch: no change; at low speed torque is limited by current (120 A → 9.1 N·m), there is voltage to spare
- no-load speed and the speed where torque starts to fall rise by 14/13 ≈ +7.7 % (≈ 5670 → 6100 rpm ideal)
- with the same 40 A battery limit, the power ceiling also rises ≈ 7.7 %
- risk: 14S full is 58.8 V against the VESC's 60 V maximum; regenerative braking on a full pack pushes the bus higher: little margin
traps:
- "more voltage = more torque at launch"
- forgetting the battery current limit sets the power ceiling
- not checking the inverter voltage rating
solution:
Launch is the same: at low speed the 120 A limit sets the torque, not the voltage. What rises is everything at the top: the voltage ceiling grows by 14/13 ≈ 7.7 %, so no-load speed goes from about 5670 to 6100 rpm (ideal) and full torque holds to a higher speed; with the same 40 A battery limit, peak power also rises ~7.7 %. The worry: a full 14S pack is 58.8 V and the VESC is rated to 60 V; regen on a full pack lifts the bus above battery voltage, so you would be one braking event from the limit.
:::

:::q id=c2 kind=case
After a hot afternoon you repeat the drill spin test and get λm = **15.2 mWb** instead of 16.855. Assume it is real (the magnets lost flux). What do you feel at launch with the same 120 A limit? What happens to no-load speed? The VESC still thinks λm is the old value: what is now wrong in what it believes?
key:
- λm down ≈ 10 %; Kt = 1.5 × 3 × 0.0152 ≈ 0.068 N·m/A; launch torque at 120 A ≈ 8.2 N·m instead of 9.1
- the current at launch is the same (current mode, and at start E = 0); only the torque per amp falls
- no-load speed rises ≈ 1/0.90: about 5670 → 6290 rpm ideal
- the VESC's flux estimate (used by its observer for position and speed) is now wrong; it should be re-detected
traps:
- "with less field, more current flows at launch" (his mistake #14: at start the current is the same, the force halves)
- "the top speed falls with weaker magnets"
solution:
λm fell about 10 %, so Kt falls to about 0.068 N·m/A: at the same 120 A, launch torque drops from 9.1 to about 8.2 N·m. The current is the same, because the VESC sets it. Back-EMF per rpm also falls 10 %, so the no-load speed rises to about 6290 rpm ideal: less force, more speed, the same trade as in L1. And the VESC's observer now works with a flux 10 % too high: re-run detection before trusting its speed and angle estimates.
:::

:::q id=c3 kind=error
A colleague explains your VESC: "To make the negative half of the sine, the bottom transistor of each leg puts −52 V on the phase. To give the motor more voltage, the VESC raises the PWM frequency above 30 kHz. The diodes across the transistors are there only in case someone connects the battery backwards." Find every error.
key:
- a leg connects its phase to +52 V or to 0 V (battery minus), never to a negative voltage; the AC appears in the difference between phases and the star point
- the average voltage is set by the duty cycle (V̄ = D·Vbus); the frequency stays fixed at 30 kHz
- the diodes give the inductive phase current a path when a switch opens (freewheeling, dead time) and carry regenerative current back to the bus
- they do not protect against reverse polarity: a reversed battery would drive current straight through all of them
traps:
- accepting "the phase goes negative" (his mistake #6)
- "PWM varies the frequency" (his mistake #5)
- calling the diodes protection
solution:
Three errors. (1) There is no −52 V anywhere: each leg switches its phase between +52 V and 0 V. The phase voltages only go negative relative to each other and to the star point. (2) The VESC changes the duty, not the frequency: V̄ = D·Vbus at a fixed 30 kHz. (3) The diodes are the freewheel and regeneration path for the winding current that cannot stop. With a reversed battery they would conduct and short it.
:::

src: Hughes §1.8.1–1.8.2, pp. 30–34; §2.4.3, p. 71

## Close {#close}

:::q id=z0 kind=explain
An interviewer asks: "Take me from your battery to torque on the shaft." In at most 6 lines: battery → inverter → field → torque, with what limits it.
key:
- 52 V DC; the inverter's three legs switch at 30 kHz and the duty sets the average voltage of each phase (V̄ = D·Vbus); the winding inductance smooths the current into near-sines
- three phases 120° apart in space, currents 120° apart in time: one field of constant strength that rotates, one pole pair per electrical cycle (p = 3)
- the magnets lock to it; the controller keeps the field 90° electrical ahead (all current on q) using the rotor angle, torque T = Kt·iq = 0.0758 N·m/A
- limits: current (120 A motor, 40 A battery) caps torque at low speed; voltage (30 V peak against back-EMF λm·ωe) caps speed
traps:
- empty phrases like "the inverter manages the power"
- leaving out what limits the chain
solution:
The battery gives 52 V DC. The inverter's three legs switch it at 30 kHz; the duty of each leg sets its average voltage, and the winding inductance turns those pulses into nearly sinusoidal currents. Three phases sit 120° apart around the bore and carry currents 120° apart in time, so together they make one constant field that rotates, a third of a turn per electrical cycle in my p = 3 motor. The rotor magnets lock onto it; the VESC uses the rotor angle to keep the field 90° ahead, so T = Kt·iq with Kt = 0.0758 N·m/A. Current limits (120 A motor, 40 A battery) cap the torque at low speed; the 30 V voltage ceiling against the back-EMF caps the speed.
:::

:::q id=z1 kind=doubt
What is still unclear after the exam? Write it as it is. Claude explains it now, and it goes to the "what I don't get" part of the review with your mentors.
:::
