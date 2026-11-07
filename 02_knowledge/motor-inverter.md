# Motor + inverter — what I can explain

Taken from my answers in L1 (25 Oct), corrected. If a sentence doesn't sound like me, I rewrite
it. The mistakes are in [mistakes](mistakes.md).

## Top speed at no load

As it spins, the rotor magnets change the flux through the coils, and that induces a voltage:
the **back-EMF**, proportional to speed (e = ωe·λm). The motor speeds up until the back-EMF
almost equals the maximum voltage the inverter can apply (with SVPWM, Vbus/√3 peak per phase).
There is no voltage left to push current, and without current there is no torque: the speed
levels off. It doesn't quite reach the ideal because some current (1.9 A in my motor) is needed
to overcome friction.

To go faster: more bus voltage or **field weakening**, which is injecting negative id to subtract
flux from the magnet's. It is disabled in my VESC.

## Back-EMF without current

No current is needed, a changing flux is. I measured it on 7 Sep: motor disconnected, spun with a
drill, oscilloscope between two phases → λm = 16.855 mWb.

## Why you need to know where the rotor is

Maximum torque comes when the coils' field is **90 electrical degrees** ahead of the magnets'
field. To put it there, the inverter has to know where the rotor is: on my quad the Hall sensor
says so.

## The path of the energy

Battery (chemical → electrical, watched by the BMS) → **DC link**: capacitors that supply the
current peaks of switching, which the battery cable cannot deliver that fast → six transistors,
two per phase, driven by the microcontroller → three alternating voltages on the phases → torque
on the rotor → chain reduction (11/92), which trades speed for torque → the wheel turns rotation
into forward motion.

## Wrong rotor angle → current on d (2026-11-05, EXP-003)

My explanation, corrected: the inverter measures the phase currents (the VESC 6 design has a
shunt on each phase) and turns them into id and iq with Clarke and Park, **using the angle it
believes**. If that angle is wrong, part of the real torque current lands on the d axis it
believes in. Its setpoint is id = 0, so the controller fights a current that is not really
there, and the torque wobbles. With Hall sensors the error is not fixed: it changes at every
Hall edge, 6 times per electrical turn, so the ripple has a frequency that grows with speed.

Numbers (Claude's, to redo myself): 2 A truly on q, angle 10° off → it sees id ≈ −0.35 A and
iq ≈ 1.97 A. At 2000 erpm the Hall edges come 200 times per second.

## When can the observer read the angle? (2026-11-05)

Back-EMF has no threshold: E = λω grows from zero with speed. The observer is "reliable" when E
is large compared with what it gets wrong: the R·i drop it subtracts (R changes with
temperature), the inverter's voltage error (dead time), and current-sensor offsets. So the speed
where it becomes reliable is not physics, it is a choice. On my quad: 2500/4000 erpm (VESC
default) gave clean control from 4000; 1000/2000 gives it from 2000 with the wheels in the air.
Under load is still to test.

## The rotor of my motor

Inner rotor, wound stator outside. I measure Lq/Ld ≈ 1.14: there is some saliency.
**Answered 6 Nov by opening it:** 9 slots, 6 poles, magnets on the surface **with iron between
them** (an inset rotor). Along q the flux crosses that iron instead of a magnet, so Lq > Ld is
real. It is small (1.14, not 2–3 like a typical IPM) because the iron is only 5 of every 26 mm
of pole pitch. Detail in `03_hardware/motor-parameters.md`. Still to say in my own words: mistakes
#27 and #28.
