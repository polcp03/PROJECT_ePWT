# Quad tasks

> Updated 6 Nov 2026. **Tick things off in the [Quad Tasks page](https://claude.ai/artifact/4hkig3fuuywMzBDRh6fefu)**,
> not in a chat. Your ticks are saved there; every Sunday the sync copies them into this file.
> Nothing here is a new direction: it all comes from the roadmap, DEC-005 and DEC-008.
>
> **Next up:** wait for the parts, then get the logger recording on the quad again (section 3).

<!--
Format, read by build.py:
  - [ ] todo · [~] ordered (buy items only) · [x] done
  {#id} is the task's permanent id: the page stores ticks under it. Never change an id.
  {#id buy} makes it a purchase: To buy → Ordered → Arrived.
  Indented lines under a task are its details. Relative links become plain text on the page.
-->

## 1 · Buy {#buy}

Everything is ordered (6 Nov). Tap **Arrived** when it is in your hands.

### For the logger and the VCU board

- [~] microSD card 16–32 GB, branded (SanDisk or Samsung) · ~6 € {#sd-card buy}
  The old Kodak died on 1 Nov: it answers but keeps nothing. Without a card the logger records
  nothing. Over 32 GB comes as exFAT and must be reformatted to FAT32.
- [~] USB microSD card reader · ~5 € {#sd-reader buy}
  The PC has no SD slot. Downloading over the ESP32's USB corrupts big files; a reader takes seconds.
- [~] IMU GY-LSM6DS3 ×2 · ~5 € each {#imu buy}
  The old one broke while soldering (the SDA resistor came off). The second is a spare.
- [~] NTC thermistor 10 kΩ with lead ×2 (`NTC 10K 3950`) · ~2 € {#ntc buy}
  Motor temperature, to the VESC's temperature input. The second is a spare.
- [~] 100 nF ceramic capacitors ("104"), assorted · ~3 € {#caps-100n buy}
  One next to every sensor, between VCC and GND.
- [~] Double-sided perfboard 9×15 cm ×2 · ~4 € {#perfboard buy}
  The 7×9 one is too small: the layout takes 112×86 mm. The second is a spare.
- [~] Pin headers 2.54 mm: female 1×40 ×3, male 1×40 ×1 · ~3 € {#headers buy}
  Sockets for the ESP32, the SD module (stands upright) and the IMU (1×8, on the VCU board).
- [~] Screw terminals 5.08 mm: 1 two-pole, 4 three-pole · ~3 € {#terminals buy}
  The edge connectors: a screwed wire does not shake loose.
- [~] Bare tinned copper wire 0.6 mm · ~2 € {#bus-wire buy}
  Only for the GND, +5 V and +3.3 V buses.
- [~] Solid insulated wire 22 AWG, colour kit · ~6 € {#wire-22awg buy}
- [~] Dupont cable female–female 10 cm, strip of 40 · ~2 € {#dupont buy}
  From the CAN module to the board: a strip of 7 wires, a drop of hot glue at each end.
- [~] Nylon M3 standoffs 10 mm, kit · ~4 € {#standoffs buy}
  CAN module above the board, board inside the box.
- [~] Shielded 4-core cable, 1 m {#shielded-cable buy}
  For the front wheel Hall (DEC-008). Shield to ground at the VCU end only.
- [~] Sealed ABS box ~150×110×70 mm · ~8 € {#abs-box buy}
  At least 60 mm tall inside. Bolted rigidly near the middle of the quad, no rubber: the IMU is inside.

### EMC parts (DEC-008)

- [~] Ceramic capacitors 10 nF, 100 V, X7R ×10 · ~2 € {#caps-10n buy}
  Two for the bond VESC ground → chassis, three for the rotor Halls, the rest spare.
  100 V, not 50 V: the bond sees the pack.
- [~] Ceramic capacitors 1 nF ×5 · ~1 € {#caps-1n buy}
  C9, the wheel input filter, and spares.
- [~] Resistors 1 MΩ ×2 and 4.7 kΩ ×4 · ~1 € {#resistors buy}
  1 MΩ across the bond capacitors (bleeds static). 4.7 kΩ: IMU pull-ups, only if the new module has none.
- [~] TVS diode SMBJ16A ×2 · ~2 € {#tvs buy}
  At the 12 V input of the VCU, against spikes on the 12 V wiring.
- [~] Optional: clamp-on ferrite, material 31, ~10 mm cable · ~4 € {#ferrite buy}
  Only for the A/B test of EXP-004. It stays only if the measurement improves.

### Borrow, don't buy

- [ ] Two identical bathroom scales {#scales}
  Load per axle and height of the centre of gravity (section 4).
- [ ] Long tape measure, 10 m {#tape}
  For the roll-out (section 4).

## 2 · Paperwork you owe {#debt}

- [ ] Write the C02 close {#c02-close}
  `01_plan/cycles/closed/C02.md`: result, what I learned, what went wrong.
- [x] C03 plan written {#c03-plan}
  `01_plan/cycles/C03.md`.
- [ ] Close mistake #4: why PWM and not a resistor {#mistake-4}
  Open in `02_knowledge/mistakes.md`.
- [ ] Put R_int = 0.18 Ω into the model {#r-int}
  Measured on 31 Oct, still missing from `04_model/params/`.

## 3 · Get the logger recording again {#logger}

When the parts arrive. Order matters: card first, then the board.

- [ ] Format the new card (FAT32) and record with the front wheel spun by hand {#first-record}
  Check the file for `#wheel` and `#wstat` lines: wheel speed is loaded on the ESP32 but has
  **never been seen on a card**.
- [ ] Check the old Kodak card in the reader {#kodak-check}
  Not seen = dead chip. Seen but won't format = locked read-only. Formats fine = check the SD module.
- [ ] Build the logger on the perfboard {#perfboard-build}
  ESP32 and modules in sockets, short wires, away from the VESC and the phases: that is what
  removed the noise, not the firmware. Then record with throttle and confirm 0 corrupted frames.
  Layout: [perfboard, rev C](https://claude.ai/artifact/FaUSu6HwdwUUkRSe6dvWig).
- [ ] Solder the new IMU on the VCU board {#imu-solder}
  Pins pushed into the breadboard while soldering, fine tip, short time. I2C on GPIO 21/22,
  100 kHz. Check the module's pin order and whether it has its own pull-ups (if not, 4.7 kΩ).
- [ ] NTC on the motor case {#ntc-fit}
  Kapton tape or thermal epoxy, to the VESC's temperature input. The Hall cable has no
  temperature wire (seen 6 Nov), so it needs its own wire. In VESC Tool: type NTC and the beta
  of the part. Re-enables the 85/100 °C limits.

## 4 · Measurements without software {#measure}

Numbers the model marks as assumed or missing. None needs code.

- [x] Open the motor: rotor, magnets and Hall sensors {#open-motor}
  Done 6 Nov: 9 slots, 6 poles, star, inset magnets (iron between them, so Lq > Ld is real),
  Halls in a fixed cage. The 19° Hall spread did not change. Detail in `03_hardware/motor-parameters.md`.
- [x] Motor photos sent {#motor-photos}
  6 Nov: twelve photos in `09_reviews/assets/photos/`.
- [x] Chain refitted {#chain}
  Done 6 Nov, one link longer: starts at ~3 A, chain drag ≈ +1.5 A of iq (EXP-003). Sag not measured.
- [x] Brakes {#brakes}
  Normally open: continuity only when braking. Only the front switch is wired (GPIO 32); the
  rear one fails, GPIO 33 stays reserved.
- [ ] Roll-out over 10 m → real rolling radius {#rollout}
  With you on it, count magnets (or turns) over 10 measured metres. Replaces the assumed
  `r_roll` and decides whether the VESC's wheel diameter is 0.30 or 0.31 m. Every speed channel
  depends on this number.
- [ ] Load per axle and centre-of-gravity height {#cg}
  Scale under each axle on level ground, with and without you. For the height, lift one axle a
  known amount and see how much weight moves to the other. **Derive the formula yourself before
  measuring**: it is a moment balance.

## 5 · Wiring against noise (EMC) {#emc}

Why and the numbers: `03_hardware/emc-study.md`. Plan approved 6 Nov: DEC-008.

### Free: do it while wiring

- [ ] Battery + and − together along the whole 40 cm run {#emc-dc-pair}
  Zip-tied every 5 cm, or twisted.
- [ ] The three phases in one tight bundle, as short as the layout allows {#emc-phases}
- [ ] Every low-voltage signal twisted with its own return {#emc-twist}
  Throttle, brake, wheel Hall, 12 V supply. They cross power cables at 90°, never alongside.
- [ ] Low-voltage box under the chassis plate {#emc-lv-box}
  Its cables leave on the side away from the VESC's.

### Build

- [ ] Rotor Halls: three 10 nF to Hall GND, at the VESC's Hall plug {#emc-hall-caps}
- [ ] Aluminium box for the VESC (you make it) {#emc-vesc-box}
  1.5–2 mm, bolted to the chassis plate on **bare** steel (scrape the paint, toothed washer,
  protect the joint afterwards). Power cables out one side, CAN and Halls out the far side.
- [ ] Wheel Hall on the shielded cable {#emc-wheel-hall}
  Shield to VCU ground at the VCU end only. Filter 10 kΩ + **1 nF** (C9), not 100 nF.
- [ ] VCU input filters and TVS {#emc-vcu-inputs}
  Throttle RC 1 kΩ + 100 nF, brakes 10 kΩ + 100 nF, 100 nF at every module, SMBJ16A on the 12 V input.
- [ ] CAN: twisted pair plus a GND wire, then measure 60 Ω {#emc-can}
  Measure CAN-H to CAN-L with everything off. The 88 Ω reading is still unexplained.
- [ ] High-frequency bond: 2 × 10 nF + 1 MΩ, VESC power ground → chassis {#emc-bond}
  Leads under 2 cm. **Never a wire**: a wire turns a chafed positive cable into a pack short.

### Test

- [ ] Write the number in REQ-VCU-02 {#req-vcu-02}
  How many mV of throttle noise you accept at 40 A, and why. Before EXP-004.
- [ ] EXP-004: one change at a time, at 5, 20 and 40 A, wheels in the air {#exp-004}
  Baseline → throttle RC → Hall capacitors → bond → ferrite. Record throttle ADC peak-to-peak,
  CAN errors, Hall errors in VESC Tool and resets.

## 6 · Tests that give information {#tests}

Each test answers a question of the model. VESC signals over CAN: motor and battery current,
erpm, duty, voltage. Plus wheel, IMU and NTC once fitted.

- [ ] A · Motor constant, wheel in the air (C04) {#test-a}
  Throttle in held steps. If the model is right, duty × voltage against electrical speed is a
  straight line whose slope is λm. Compare with the C00 back-EMF. **Predict first** whether the
  line goes through zero, and why not quite.
- [ ] B · Resistance against temperature (C04, needs the NTC) {#test-b}
  Short loaded runs, writing down motor temperature. Copper resistance rises ~0.4 % per degree.
- [ ] C · Coast-down: rolling and air drag (C05) {#test-c}
  From top safe speed, release the throttle and let it roll to a stop. Fit `a + b·v + c·v²`
  (SAE J2263). Level ground, no wind, **both directions**, three runs each, same tyre pressure.
- [ ] D · Full-throttle acceleration (C05) {#test-d}
  From standstill. Current and speed give wheel force; the IMU gives acceleration. The C01 model
  must predict the curve. Above 9 km/h it sits at 40 A of battery: the BMS limit.
- [ ] E · Slip {#test-e}
  Rear wheel (erpm ÷ 3 ÷ 8.364) against the front (Hall). Straight, no wheelspin: the
  difference is the radius error. The base of traction control.
- [ ] F · Halls against the observer, under load {#test-f}
  With you on it, gentle and full starts, logging id, iq, erpm and duty. Pass: id ripple
  < 0.5 A above 2000 erpm and no jerk through 1000–2000. If it fails, raise the handover 500 erpm
  at a time, one change at a time.
- [ ] G · Throttle noise under load (REQ-VCU-02) {#test-g}
  On the bench at 5 A with no filter the throttle jumped up to +80 mV. Repeat under load with the
  RC filter fitted, logging the raw ADC.

## 7 · Vehicle control unit v0 (Dec–Jan) {#vcu}

The ESP32 reads the throttle and sends the current command to the VESC over CAN. No control yet:
only pass the command on, with protections.

- [x] CAN timeout in the VESC {#vcu-can-timeout}
  5 Nov: 100 ms, measured 105–121 ms with the wheel in the air (REQ-VCU-03 verified). Never disabled.
- [x] Throttle on the ESP32, on the bench {#vcu-throttle-bench}
  5 Nov: powered from 3.3 V, no divider, GPIO 35. Outside 600–2800 mV → zero torque.
- [ ] Throttle on the board, with the RC filter and the 100 kΩ {#vcu-throttle-board}
- [ ] Brake input: front brake on GPIO 32; brake + throttle → zero torque {#vcu-brake}
  From v0. It is normally open, so a cut wire reads as "not braking": think about what that means.
- [ ] Ground loop check with the ESP32 commanding torque {#vcu-ground-loop}
  EXP-001 matters again.

## 8 · Decisions that are yours {#decide}

- [ ] The VCU's emergency stop: what it is and where it goes {#dec-estop}
- [ ] Front wheel locks under hard braking: what happens to the speed reference? {#dec-wheel-lock}
  Half answered on 1 Nov: mistake #11, asked again on Saturday 7 Nov.
- [ ] `l_in_current_max`: stay at 40 A (the BMS limit) or go lower {#dec-battery-limit}
- [x] Grounding plan {#dec-grounding}
  Decided 6 Nov: DEC-008 (floating at DC, 20 nF bond at the inverter, IMU on the VCU board).

## Later {#later}

Not now. Listed so they are not in your head.

- [ ] IMU and wheel on the card, filter chosen on the PC from real data {#later-imu-wheel}
- [ ] Traction control: first in Simulink, then on the ESP32 {#later-traction}
- [ ] End of 2026: model validated against the vehicle {#later-validated}

## Safety, every test with current {#safety}

Not tasks: rules. 13S5P Li-ion pack, BMS cuts at 40 A continuous.

1. Current limit set in the VESC before starting.
2. Pack temperature by hand when you finish.
3. Never charge unattended.
4. Wheels in the air first; on the ground only once that works.
