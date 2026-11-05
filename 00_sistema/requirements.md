# Requirements

Light V-cycle ([DEC-006](../08_decisions/DEC-006-ciclo-en-v-ligero.md)). Pol writes them;
Claude reviews them. Each one: a number, the reason for that number, and how it is verified.
**Provisional** = signed, but its number still depends on a check written next to it.

## VCU — vehicle control unit

| ID | Requirement | Why this number | Verified by | Status |
|---|---|---|---|---|
| REQ-VCU-01 | Delay from a throttle grip change to the matching current request arriving at the VESC: **≤ 20 ms**, end to end (ADC sampling + filter + CAN period + transmission) | A car's electronic pedal is handled in the order of a 10 ms task, and a hand takes ~100–200 ms to go from 0 to full throttle, so 20 ms is far below what a rider can notice. It is a budget to share: CAN period and filter delay come out of it | To be defined (bench: step on the throttle input vs. CAN frame timestamp) | **Provisional** (2026-11-05): Pol checks the pedal task raster in INCA at work |
| REQ-VCU-03 | If the VESC stops receiving current commands (VCU frozen, CAN cable cut), motor torque goes to **0 A within 100 ms** and the motor coasts (no brake current) | 100 ms = 10 missed frames at 10 ms, enough margin against a false trip. At 30 km/h it is 0.8 m with the last torque, acceptable for bench and first ride tests | VESC CAN timeout. Test `silence` in [can_throttle](../05_firmware/arduino/can_throttle/README.md): 5 runs, 105–121 ms, of which up to ~21 ms is the VESC's status period | **Verified** 2026-11-05, wheels in the air, within measurement resolution |

## Pending — slots whose number must come from simulation or calculation

Agreed 2026-11-05: no number is written without a calculation or simulation behind it. When
the vehicle model can give these, Pol writes each requirement and Claude reviews it. **Whoever
runs those simulations: fill these from the results.**

| Slot | What it fixes | Number comes from |
|---|---|---|
| REQ-VEH-01 | Acceleration 0–X km/h in Y s, with rider (110 kg) | Vehicle model; first a hand check of the motor limit (120 A · Kt · gear / r_wheel ÷ m) and the tyre limit (μ on dirt, estimated). Pol's first guess of 1.5 g is above both |
| REQ-VEH-02 | Top speed, with and without field weakening | Vehicle model + voltage limit (λ, Ld, bus voltage under load) |
| REQ-SAF-01 | Battery current ≤ BMS limit with margin | BMS 40 A continuous; VESC current-reading error |
| REQ-SAF-02 | Bus voltage ≤ X V in any fault, including a trip at the top field-weakening speed | VESC 57 V limit; simulated overshoot |
| REQ-SAF-03 | Motor temperature ≤ X °C with natural convection only | Motor insulation class (unknown). Not verifiable today: no motor temperature sensor (`03_hardware/open-questions.md`, Risk 4) |
