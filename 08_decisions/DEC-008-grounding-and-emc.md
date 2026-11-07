# DEC-008: Grounding and EMC — floating at DC, bonded at high frequency, IMU on the VCU board

**Date:** 2026-11-06. Decided by Pol ("me parece bien todo lo que dices"), after the EMC study
and the multimeter checks of the same day ([EMC study](../03_hardware/emc-study.md)).

## Decision

1. **Both domains stay floating at DC.** No wire from the pack negative or the 12 V negative
   to the chassis. CAN GND remains the only galvanic link between the 48 V and 12 V sides
   (DEC-004 unchanged).
2. **High-frequency bond at the inverter:** two 10 nF, 100 V X7R ceramics in parallel, with
   1 MΩ across them, from the VESC power ground to the chassis plate under the VESC. Leads
   under 2 cm. Never a wire.
3. **The VESC goes in a home-made aluminium box** (1.5–2 mm), bolted to bare chassis steel.
   The VESC's aluminium plate is isolated from its ground (measured), so it may sit on the box
   floor with a thermal pad. Power cables leave through one side; CAN and Halls through the
   far side.
4. **Rotor Halls:** three 10 nF ceramics, H1/H2/H3 → Hall GND, at the VESC's Hall plug.
5. **The IMU moves onto the VCU board.** No IMU cable. The shielded 4-wire cable goes to the
   front wheel Hall instead, shield to VCU ground at the VCU end only, with 10 kΩ + 1 nF at
   the pin.
6. **Wiring rules:** battery leads together, phases bundled, every low-voltage signal twisted
   with its return, low-voltage crossing power at 90°.

## Alternatives

- **Pack negative wired to the chassis** (the "everything to ground" instinct). Rejected: a
  chafed positive cable touching the frame becomes a dead short of the 13S5P pack. Floating,
  the same fault does nothing. At 54.6 V the risk is fire, not shock.
- **Nothing to the chassis (as before).** Rejected: the switching edges push common-mode
  current through the motor's stray capacitance into the frame, and with no chosen way back it
  returns through the 12 V electronics and the CAN ground wire.
- **12 V negative also to the chassis.** Rejected: with the bond of point 2, it closes a
  high-frequency loop through the CAN ground wire.
- **IMU on the chassis with a shielded cable** (the plan until today). Rejected: I2C is
  open-drain and single-ended. Noise there corrupts bits or locks the bus, and a cable is an
  antenna. On the board, there is no cable.
- **Ferrites as the first fix.** Not adopted as a fix: kept as an A/B test on the phase sleeve
  (EXP-004), kept only if the measurement improves.

## Reasoning

Every current returns to its source. A capacitor gives the high-frequency current a 5 cm path
home at the inverter while blocking DC, so a single insulation fault stays harmless. Sizing:
20 nF is far above any plausible winding-to-case capacitance (typically 0.2–2 nF; ours read
~0 nF on the ANENG 681, unresolved), so its impedance is the lower path.

## Assumptions

- The motor case stays electrically bonded to the chassis through its bracket bolts (measured
  continuous 2026-11-06). If the bracket is repainted, a strap is needed.
- The VESC plate stays isolated from the VESC ground (measured open 2026-11-06).
- The VCU box is rigidly bolted to the chassis: with the IMU on the board, the box's vibration
  is the IMU's vibration.
- The GY-LSM6DS3 module's own pull-ups (to check) are enough with no cable at 100 kHz.

## Consequences

- VCU drawings revised: sheet 1 (chassis bond), sheet 2 (IMU on board, wheel 1 nF), sheet 3
  (perfboard rev C: IMU socket on the board, J6 removed).
- New parts to buy (shopping list): 10 nF 100 V ceramics, 1 nF, 1 MΩ, SMBJ16A.
- EXP-004 measures the effect of each change, one at a time, against REQ-VCU-02.
- The IMU's position is now fixed by the VCU box: it should go near the centre of the quad.
