# Shopping list — pending hardware

Updated 2026-11-06: **everything below is ordered and on its way** (Pol). Tick arrivals on
[Quad Tasks](https://claude.ai/artifact/4hkig3fuuywMzBDRh6fefu), section 1; the Sunday sync marks
them here and moves them to the inventory in `baseline.md`.
`[~]` ordered · `[x]` arrived.

## For the logger mounted on the quad (~55 €)

- [~] **microSD card 16–32 GB, branded (SanDisk or Samsung)** · ~6 €
  Search: `microSD SanDisk 32GB`
  The 16 GB Kodak died on 2026-11-01: it answers but keeps nothing written to it (not even a
  format). Without a card the logger records nothing. Over 32 GB comes as exFAT and must be
  reformatted to FAT32.
  When the reader arrives, check the old one on the PC: not seen = dead chip; seen but won't
  format = locked read-only; formats fine = check the SD module.
  It got warm while idle: internal failure. Likely causes: power cuts while recording (many
  resets that day), inserting or removing it powered, static.

- [~] **IMU GY-LSM6DS3 ×2** · ~5 € each
  Search: `GY-LSM6DS3`
  The one in stock broke while soldering (the SDA resistor came off). Soldering the new one:
  pins in the breadboard first, fine tip, short time.

- [~] **Ceramic capacitors 100 nF ("104"), assorted** · ~3 €
  Search: `condensador ceramico 100nF 104 pack`
  One next to each sensor (Hall, IMU), between VCC and GND. The 220 µF in stock does not filter
  fast noise.

- [~] **NTC thermistor 10 kΩ with lead ×2** (one spare) · ~2 €
  Search: `NTC 10K 3950 termistor cable`
  Motor temperature, to the **VESC's** temperature input (not the VCU). The motor's Hall cable
  has no temperature wire (seen 2026-11-06), so it needs its own. Stuck to the case with kapton
  tape or thermal epoxy. In VESC Tool: type NTC and the beta of the part bought (3950 or 3380).
  Re-enables the 85/100 °C limits and gives `R(T)` to validate the model
  ([DEC-005](../08_decisions/DEC-005-vcu-architecture.md)). Decided by Pol on 2026-11-01.

- [~] **USB microSD card reader ×1** · ~5 €
  Search: `lector tarjetas microSD USB`
  The PC has no SD slot. Downloading over the ESP32's USB works but corrupts big files (each
  one had to be downloaded three times). With a reader: seconds and no errors.

### The logger board (~20 €)

Layout: [`05_firmware/vcu-design/perfboard-layout.html`](../05_firmware/vcu-design/perfboard-layout.html)
(artifact https://claude.ai/artifact/FaUSu6HwdwUUkRSe6dvWig, sheet 3). The breadboard with dupont
wires does not survive the quad's vibration, and the long SPI wires were where the noise got in
(EXP-002): soldered and short, with the ESP32 and the modules pluggable.

- [~] **Double-sided perfboard 9×15 cm (plated holes)** ×2 · ~4 €
  Search: `placa perforada 9x15 doble cara`
  The 7×9 one is too small: the layout takes 44×34 holes (112×86 mm). The second is a spare.
  The IMU no longer needs its own small board: it plugs into the VCU board.
- [~] **Female pin headers 2.54 mm, 1×40** ×3 · ~2 €
  Search: `tira pines hembra 2.54 40`
  Sockets for the ESP32 (2×19), the SD module (1×6, it stands upright in it) and the IMU
  (1×8, on the VCU board).
- [~] **Male pin header 2.54 mm, 1×40** ×1 · ~1 €
  For the CAN cable board (1×7).
- [~] **Screw terminals, 5.08 mm pitch, 2 and 3 poles** · ~3 €
  Search: `borne tornillo 5.08 2P 3P`. Needed: 1 two-pole (J1; the IMU terminal J6 is gone)
  and 4 three-pole (wheel, throttle, brakes and CAN to the VESC). Buy a pack.
- [~] **Bare tinned copper wire 0.6 mm** · ~2 €
  Search: `hilo cobre estañado 0.6mm`. Only for the GND, +5 V and +3.3 V buses.
- [~] **Solid insulated wire 22 AWG, colour kit** · ~6 €
  Search: `cable rigido 22AWG kit colores`. Everything else: it may cross over another wire.
- [~] **Dupont cable female–female 10 cm (strip of 40)** · ~2 €
  From the CAN module to the board: its pins point up, so it does not plug in. Peel off a strip
  of 7 wires that stay together, with a drop of hot glue at each end.
- [~] **Nylon M3 standoffs 10 mm with screws (kit)** · ~4 €
  Search: `separadores nylon M3 kit`. The CAN module above the board, the board inside the box.
- [~] **Shielded 4-core cable, 1 m**
  For the front wheel Hall (DEC-008), shield to GND at the VCU end only.
- [~] **Sealed ABS box ~150×110×70 mm** · ~8 €
  Search: `caja estanca ABS 150x110x70`
  Dust and mud. At least 60 mm tall inside: the SD stands upright (42 mm) and the CAN module
  sits on standoffs. Plastic: an aluminium one would need grounding with care. Bolt it
  **rigidly** to the chassis, no rubber: the IMU is inside now.

## EMC parts (DEC-008) · ~10 €

Small parts for the grounding plan.

- [~] **Ceramic capacitor 10 nF, 100 V, X7R** ×10 · ~2 €
  Search: `condensador ceramico 10nF 100V X7R`. Two for the bond VESC ground → chassis, three for
  the rotor Halls at the VESC plug, the rest spare. **100 V, not 50 V**: the bond sees the pack.
- [~] **Ceramic capacitor 1 nF** ×5 · ~1 €
  C9, the wheel input filter, and spares.
- [~] **Resistor 1 MΩ** ×2 and **4.7 kΩ** ×4 · ~1 €
  1 MΩ across the bond capacitors (bleeds static). 4.7 kΩ: IMU pull-ups, only if the new module has none.
- [~] **TVS diode SMBJ16A** ×2 · ~2 €
  At the 12 V input of the VCU, against spikes on the 12 V wiring.
- [~] *Optional:* **clamp-on ferrite, material 31, for ~10 mm cable** ×1 · ~4 €
  Only for the A/B test of EXP-004 on the phase sleeve. Kept only if the measurement improves.

The aluminium box for the VESC is not on the list: you make it yourself.

## Already in stock — do NOT buy

- ESP32 ×2 spare (no. 2 is the logger)
- MCP2515 + TJA1050, microSD module (the card is dead), 12 V battery + DC-DC to 5 V
- Hall sensors 3144 (one fitted on the front wheel, the rest spare) + magnets; the 5 V Hall throttle
- Breadboard, dupont wires, resistors, oscilloscope, multimeter, soldering iron

## When the vehicle control unit comes

Pinout decided: [`05_firmware/vcu-design/vcu-pinout.md`](../05_firmware/vcu-design/vcu-pinout.md).
The resistors (10 k, 12 k) come from stock and the capacitors from the 100 nF assortment above.
The only thing left to decide is the emergency stop.

## Dropped or postponed

- **Isolated CAN module ISO1050:** dropped on 2026-10-31. The logger floats on its own battery;
  see [DEC-004](../08_decisions/DEC-004-non-isolated-can-floating-logger.md). Revisited if the
  ESP32 ends up commanding torque to the VESC.
- **USB isolator ADUM3160:** postponed. It was for diagnosing the VESC's USB dropping out under
  load; the logger already records under load without USB.
- **120 Ω resistors:** postponed. The MCP2515 has its own (jumper J1) and the bus runs with 0 errors.
- **ESP32-WROOM-32 no. 1:** destroyed on 2026-09-07. Internal short. Marked and kept apart so
  it is not mistaken for a good one.
