# EMC on the quad: where the noise comes from and how to keep it out

> 2026-11-06. **The short version:** EMC is not black magic. It is the currents you did not draw.
> Every current goes back to where it came from. At high frequency it takes whatever path has the
> least inductance, and that includes capacitors you never fitted. On your quad the main risk is
> not radiation. It is the **common-mode current** that the VESC's switching edges push into the
> steel chassis. Today the only way back to the VESC runs **through your 12 V electronics and the
> CAN ground wire**. The fix is to give that current a short, deliberate path home, right at the
> inverter, and to keep every signal wire next to its own return. Ferrites are a legitimate tool,
> not the first one. Your IMU needs no filter: it needs **no cable**.
>
> **Decided 2026-11-06:** you approved this plan. It is [DEC-008](../08_decisions/DEC-008-grounding-and-emc.md):
> floating at DC, 20 nF bond at the inverter, IMU on the VCU board, shielded cable to the wheel Hall.
> The VCU drawings are at revision C. Tasks and parts: [tareas-quad](../01_plan/tasks/tasks.md), section EMC.

Numbers in this page are tagged like the baseline: **MEASURED** on your quad, **CALC** (worked out
here from known physics), **ESTIMATE** (typical value, not yours, to be measured) and **CHECK**
(something you look at with a multimeter before deciding). Sources are at the end. The research
behind this found little that was specific to the Flipsky board. Treat any board-specific claim as
CHECK.

## 1. Fundamentals: why a VESC makes noise

### The source: fast edges, not 30 kHz

Each half-bridge in the VESC slams its output (the "switch node") between 0 V and the pack
voltage, 30 000 times a second per phase. The 30 kHz is not the problem. **The speed of each edge
is.**

- Edge: 54 V in roughly 20–50 ns → **dV/dt ≈ 1–3 V/ns** (ESTIMATE; measuring it needs a probe of
  200 MHz or more on the switch node, which is not a beginner measurement).
- A trapezoidal wave's spectrum is flat up to `1/(π·τ)` (τ = pulse width ≈ 17 µs at 50 % duty →
  **≈ 19 kHz**). It then falls 20 dB per decade up to `1/(π·t_rise)` (25 ns → **≈ 13 MHz**) and
  40 dB per decade after that (CALC).
- So the energy that causes trouble sits between **1 and 100 MHz**. On top of that, the stray
  inductance of the power loop (~10 nH) rings with the MOSFET capacitance (~1 nF). That puts a
  ringing at `1/(2π√LC)` ≈ **50 MHz** (ESTIMATE, order of magnitude).

The edge frequencies are what an RC filter, a ferrite or a shield has to stop. A 30 kHz filter
is not enough on its own.

### Four ways noise reaches a victim

Noise always needs three things: a **source**, a **coupling path** and a **victim**. Remove any
one and the problem goes away. The paths:

| Path | What couples | Grows with | Typical victim on your quad |
|---|---|---|---|
| **Conducted** | shared wires (supply, ground) | shared impedance × current | a ground wire that two circuits share |
| **Capacitive** (electric field) | a voltage that jumps, near a wire | `C · dV/dt` | high-impedance inputs: **Hall lines next to the phases** |
| **Inductive** (magnetic field) | a current that jumps, near a loop | `M · di/dt`, loop area, 1/distance | a sensor wire whose return runs elsewhere |
| **Radiated** | a cable acting as an antenna | only when the cable is ~λ/2 | barely: 1 m of cable resonates near 150 MHz |

At 10 cm from the inverter and below ~100 MHz, everything on your quad is **near field**. The
far-field boundary `λ/2π` is 1.6 m at 30 MHz (CALC). That is good news. Near-field coupling is
geometry, and geometry is something you control.

### The phases make an electric field, the battery leads a magnetic one

This is first principles, from your own motor:

- **Phase cables: the voltage jumps, the current does not.** The phase current has to go through
  the motor inductance (L ≈ 105 µH, VESC_ESTIMATE). It ramps at most `V/L` = 54 V / 105 µH ≈
  **0.5 A/µs** (CALC). That is slow. Their voltage, though, jumps 54 V in tens of ns. So the phase
  cables are mainly an **electric-field (capacitive) aggressor**.
- **Battery leads: the current jumps.** At every edge the DC-link current switches between 0 and
  the phase current. The VESC's capacitors supply most of that locally. Whatever they do not
  supply runs down the battery leads at 30 kHz with fast edges. So the battery leads are mainly a
  **magnetic-field aggressor**, and their loop area is what matters.

### Common-mode current: the one that causes real trouble

Every conductor that jumps in voltage has a stray capacitance to nearby metal. For that
capacitance, current is `I = C · dV/dt`:

- Motor winding → motor frame: ~0.2–2 nF is typical for a motor this size (ESTIMATE). **Yours:
  not measured.** The first readings were on the Hall wires by mistake. On the phases, the ANENG
  681 reads ~0 nF, which is either below what it resolves or a poor contact (section 4). The
  design below does not depend on it.
- With 1 nF and 2 V/ns: **I ≈ 2 A peak** for ~25 ns at every edge (CALC). That is 6 edges per
  PWM period, 30 000 periods per second.

That current flows into the motor frame, then into the **chassis**, because the motor is bolted
to it (**CHECK** continuity). It then has to get back to the VESC, which is where it started.
**A floating pack does not stop it. It only means that you have not chosen its way home.** It
then returns through whatever stray capacitances are available, and on your quad one of them
leads through the 12 V electronics and the CAN ground wire.

<figure class="esquema">
<svg viewBox="0 0 640 320" role="img" aria-label="Common-mode current loop on the quad: from the VESC switch node through the phase cables, the motor winding capacitance and the chassis. Today it returns through the VCU and the CAN ground wire; with a 10 nF bond at the inverter it returns locally">
<text class="tit" x="20" y="24">WHERE THE SWITCHING CURRENT GOES HOME</text>
<rect class="relleno" x="40" y="50" width="180" height="60"/>
<text x="56" y="76">VESC</text>
<text class="dim" x="56" y="96">edges 1–3 V/ns</text>
<rect class="relleno" x="440" y="50" width="170" height="60"/>
<text x="456" y="76">MOTOR</text>
<text class="dim" x="456" y="96">frame on chassis?</text>
<line class="trazo" x1="220" y1="80" x2="440" y2="80"/>
<text class="dim" x="232" y="70">phases + Halls, one sleeve</text>
<line class="peligro" x1="525" y1="110" x2="525" y2="140"/>
<line class="peligro" x1="508" y1="140" x2="542" y2="140"/>
<line class="peligro" x1="508" y1="148" x2="542" y2="148"/>
<line class="peligro" x1="525" y1="148" x2="525" y2="180"/>
<text class="t-peligro" x="500" y="134" text-anchor="end">winding→frame</text>
<text class="t-peligro" x="500" y="149" text-anchor="end">~1 nF, 2 A peaks</text>
<line class="suelo" x1="150" y1="180" x2="620" y2="180"/>
<text class="dim" x="330" y="198">steel chassis (floating today)</text>
<line class="peligro" x1="300" y1="180" x2="300" y2="215"/>
<line class="peligro" x1="284" y1="215" x2="316" y2="215"/>
<line class="peligro" x1="284" y1="223" x2="316" y2="223"/>
<line class="peligro" x1="300" y1="223" x2="300" y2="260"/>
<line class="peligro" x1="300" y1="260" x2="190" y2="260"/>
<text class="t-peligro" x="312" y="245">stray C to your electronics</text>
<rect class="relleno" x="40" y="230" width="150" height="60"/>
<text x="56" y="256">VCU · 12 V side</text>
<text class="dim" x="56" y="276">ESP32, CAN, sensors</text>
<line class="peligro" x1="60" y1="230" x2="60" y2="110"/>
<text class="t-peligro" x="68" y="202">CAN GND:</text>
<text class="t-peligro" x="68" y="217">today's way back</text>
<line class="bien" x1="170" y1="110" x2="170" y2="138"/>
<line class="bien" x1="155" y1="138" x2="185" y2="138"/>
<line class="bien" x1="155" y1="146" x2="185" y2="146"/>
<line class="bien" x1="170" y1="146" x2="170" y2="180"/>
<text class="t-bien" x="196" y="140">20 nF bond (DEC-008)</text>
<text class="t-bien" x="196" y="155">at the inverter</text>
</svg>
<figcaption>Red: the loop today. The switching edge charges the motor's stray capacitance, the current
crosses the chassis and finds its way back through your 12 V electronics and the CAN ground wire.
Green: a capacitor from the VESC ground to the chassis right at the inverter gives it a path 5 cm
long instead of a metre, and that path keeps it out of the VCU.</figcaption>
</figure>

### Loop area: the one rule that explains almost everything

A current makes a magnetic field in proportion to the **area of the loop** formed by its way out
and its way back. A victim picks up voltage in proportion to **its own loop area**. Both effects
fall off with distance.

Worked example (CALC): a sensor wire 30 cm long, with its return 1 cm away (loop of 30 cm²). It
sits 5 cm from a battery lead whose current changes 20 A in 1 µs:

- Field at 5 cm: `B = μ₀I / 2πr` → 4 µT per amp.
- Mutual inductance: `M ≈ 4 µT/A × 0.003 m²` ≈ **12 nH**.
- Picked-up voltage: `V = M · di/dt` = 12 nH × 20 A/µs ≈ **0.24 V**. Move the wire to 1 cm and it
  becomes ~1.2 V. That is a full logic level on a high-impedance input.
- **Twist the wire with its return** and the loop area drops to almost zero. Each twist cancels
  the next, and the pickup falls to millivolts.

<figure class="esquema">
<svg viewBox="0 0 640 230" role="img" aria-label="Loop area: battery leads apart form a large loop, together they cancel; a sensor wire with its return elsewhere forms a large loop, twisted with its return it picks up almost nothing">
<text class="tit" x="20" y="24">SAME WIRES, DIFFERENT LOOP AREA</text>
<text class="dim" x="20" y="56">battery leads</text>
<rect class="peligro" x="140" y="45" width="170" height="50"/>
<text class="t-peligro" x="150" y="115">apart: the loop is an antenna</text>
<line class="bien" x1="400" y1="62" x2="600" y2="62"/>
<line class="bien" x1="400" y1="70" x2="600" y2="70"/>
<text class="t-bien" x="400" y="115">together: the fields cancel</text>
<text class="dim" x="20" y="156">sensor wire</text>
<path class="peligro" d="M140 145 H310 V195 H140 Z"/>
<text class="t-peligro" x="150" y="215">return elsewhere: ~1 V pickup</text>
<path class="bien" d="M400 160 q12 -14 25 0 t25 0 t25 0 t25 0 t25 0 t25 0 t25 0 t25 0"/>
<path class="bien" d="M400 160 q12 14 25 0 t25 0 t25 0 t25 0 t25 0 t25 0 t25 0 t25 0"/>
<text class="t-bien" x="400" y="215">twisted with its return: mV</text>
</svg>
<figcaption>The current and the copper are the same in both columns; only the area between the way out
and the way back changes. Each twist of a pair reverses the pickup of the one before it.</figcaption>
</figure>

Loop area and distance both act linearly. Twisting is free and divides the problem by 10–100.
That is why "twist every signal with its return" comes before shields, boxes and ferrites.

### Why the experts call it black magic, and why it is not

**What is predictable:** dV/dt, di/dt, loop areas, the order of magnitude of stray capacitance,
skin depth, the frequency of a ringing. Everything in this section.

**What is not predictable from the drawing:** the real stray capacitances and inductances of your
wiring, the resonances of a tubular chassis and its cables, and which way the return current
actually takes. Nobody draws those, so the circuit "should" work and does not.

**The professional answer is a method, not a simulation:** cut the source, shrink the loops, give
every current a deliberate return, then **measure before and after one change at a time**. You
already did exactly this in EXP-002. The noise entered through the breadboard SPI wiring, not
through CAN. The bus showed 0 errors at 49 A while single-ended, long, high-impedance wires
failed. That is the whole of EMC in one experiment of yours.

## 2. Your quad, as it is today

### The architecture, seen as an EMC engineer

From [baseline](baseline.md), [DEC-004](../08_decisions/DEC-004-non-isolated-can-floating-logger.md)
and [DEC-005](../08_decisions/DEC-005-vcu-architecture.md):

| Domain | Contents | Tied to the chassis? |
|---|---|---|
| 48 V | 13S pack, BMS, VESC (bare board, held by a zip tie on painted steel), motor, rotor Halls | No (floating). The motor's aluminium case sits on a painted steel bracket bolted to the chassis: probably connected, continuity not yet measured |
| 12 V | 12 V battery, DC-DC to 5 V, ESP32 VCU, MCP2515/TJA1050, throttle, brakes, wheel Hall, IMU | No: the negative never goes to the chassis (by design, Pol 2026-11-06) |
| Link between them | **CAN-H, CAN-L and CAN GND**, nothing else | — |

**What is already right**, and why:

1. **One galvanic link between the domains.** One link means no DC ground loop. That is the
   lesson of the destroyed ESP32 (EXP-001), already applied.
2. **Throttle moved off the VESC's ADC.** If it were tied to both, there would be two ground paths.
3. **CAN is differential.** The TJA1050's receiver works with each bus wire anywhere between
   **−12 V and +12 V** relative to its ground (datasheet test window). Noise that hits both wires
   equally cancels. EXP-002 confirms it: 0 bus errors.
4. **Separate 12 V battery.** No DC-DC from the pack, so no shared supply current.

**What is weak:**

1. **The common-mode current has no chosen path home.** See the figure in section 1.
2. **The rotor Halls share a sleeve with the phases.** Each Hall wire sits a few millimetres from
   wires that jump 54 V in tens of ns. More in section 3.
3. **The VESC is a bare board 10 cm from the LV electronics.** The capacitive coupling from its
   switch nodes falls off with distance, and 10 cm is not much distance.
4. **The perfboard VCU, the IMU cable and the wheel-sensor run** are single-ended, high-impedance
   lines. That is the kind of wire that failed in EXP-002.

### The mistake to avoid: a hard bond of the pack to the chassis

**Safety first, stated plainly.** Do not connect the pack negative to the chassis with a wire or
a bolt. Today the chassis floats, so a chafed **positive** cable touching the frame does
nothing. It is a single fault and it is harmless. With the negative bonded, that same chafe is a
**dead short of a 13S5P pack through the frame**: hundreds of amps, and the BMS may or may not
open in time. 54.6 V is below the 60 V DC limit where shock becomes the concern, so the risk here
is **fire, not shock**. Floating is a safety feature. Keep it, and bond for high frequency only
(next section).

Automotive 48 V systems are not a counter-example. They are designed with fused, insulated
returns and with isolation in mind; they do not just bolt the negative to whatever metal is
nearby.

## 3. What to do, part by part

### Grounding: the plan in five rules

1. **The 48 V pack stays floating at DC.** No wire from pack negative to chassis.
2. **High-frequency bond at the inverter:** two **10 nF, 100 V ceramic (X7R) capacitors in
   parallel** from the VESC's power ground to the chassis plate under it, leads under 2 cm, plus a
   **1 MΩ** resistor across them so the chassis cannot float up with static. Why 10 nF: it has to
   be a much lower impedance than the stray capacitance it short-circuits (~1 nF). At 10 MHz,
   20 nF is ~0.8 Ω (CALC). A capacitor blocks DC, so a chafed positive cable still shorts
   nothing.
3. **The 12 V side stays floating from the chassis.** If you bonded it too, the high-frequency
   loop "VESC ground → 10 nF → chassis → 12 V negative → CAN GND → VESC" would carry the
   common-mode current through the CAN ground wire again. **CAN GND remains the only link**,
   carrying almost no current, which is what a reference wire should do.
4. **The motor frame stays bolted to the chassis**, as it is. That is what makes the chassis the
   return path in rule 2, and the loop then closes 5 cm from where it started. Your motor sits on
   a **painted** bracket, so the bolts may or may not make contact. If the continuity check
   fails, add a short braided strap from the motor case to bare chassis steel. Without it, the
   path from motor to chassis is only a capacitance, and rule 2 loses most of its effect.
5. **Write it down as a drawing:** sheet 1 of the VCU drawings already shows the two domains. Add
   the chassis and the 10 nF bond to it so that whoever wires the quad (you, in six months) does
   not undo it.

If you ever replace the 12 V battery with a DC-DC fed from the pack, the architecture changes. A
non-isolated DC-DC is a second link between the domains. It would have to be an **isolated** one.
That decision goes to `08_decisions/` before you buy anything.

### The inverter box: aluminium, bonded, the plate doing double duty

Your plan is right, with three details.

- **Aluminium, 1.5–2 mm.** Skin depth is **0.49 mm at 30 kHz and 27 µm at 10 MHz** (CALC,
  `δ = 1/√(π f μ σ)`). At the frequencies that matter, 2 mm of aluminium blocks the electric field
  completely. Steel blocks low-frequency magnetic field better (δ ≈ 0.1 mm at 30 kHz). It is also
  heavier and worse for heat, and the magnetic field at 30 kHz is not your problem.
- **The leak is never the wall. It is the holes and the cables.** A cable that passes through the
  wall carries the noise straight out. So bring the battery and phase cables out **through the
  same side**, bundled, and the CAN and Hall cables out as far away from them as the box allows.
- **Bare metal contact.** Scrape the paint where the box meets the chassis plate, use a toothed
  washer and a bolt, and protect the joint against corrosion afterwards (paint or grease over the
  finished joint). One square centimetre of bare metal beats any length of wire. A wire
  ("pigtail") has ~1 nH per mm, so 5 cm is ~31 Ω at 100 MHz (CALC).
- **Heat.** Look at how the Flipsky plate is cooled before closing it in. The box bottom can serve
  as the heatsink with a thermal pad, if the plate is **isolated** from the board's ground.
  **CHECK** with the multimeter: is the VESC's aluminium plate connected to its power ground? If it
  is, it must not touch the box directly: it would be the DC bond rule 1 forbids.
- **The steel chassis plate is your best shield, and it costs nothing.** Inverter on top, LV box
  underneath: the plate is a metal wall between the aggressor and the victims. Do not waste it.
  Keep the LV wiring from going around its edge next to the VESC's cables.

### The rotor Halls in the phase sleeve

You cannot separate them. So you work on the victim and on the common-mode current:

- **Why they get hit:** wire-to-wire capacitance is ~20–50 pF per metre (ESTIMATE). Your
  **50 cm** of shared sleeve, motor to inverter (Pol, 2026-11-06), gives ~15 pF. At 2 V/ns that
  injects **~30 mA spikes** into a Hall line (CALC). A Hall output that is "off" is held high only
  by a pull-up: **2.2 kΩ** in the official VESC 6 schematics (R42–R44, versions 6.4 and MK5).
  That is a high-impedance node, and a 30 mA spike moves it easily.
- **The fix that works:** a small **capacitor from each Hall line to ground at the VESC's Hall
  connector**. The 30 mA × 25 ns charge (0.75 nC) into 10 nF moves the line by only **75 mV**
  (CALC). In the official schematics I could read the component list but not the drawing, and
  that list shows **no filter capacitor on the Hall lines**. Flipsky does not publish its own
  layout, so your board may differ. Either way the fix is the same: fit them on the plug side,
  three 10 nF ceramics from H1, H2 and H3 to the Hall GND pin, soldered inside the connector
  housing or on a small adapter. Values used in practice run from 1 to 22 nF. Keep the corner frequency well above
  your Hall edge rate: at top speed your motor runs at **~290 Hz electrical** (CALC: `(Vbus/√3)/λ`
  = 31 V / 16.855 mWb). With 2.2 kΩ and 10 nF the delay is 22 µs, about **2.3° electrical at top
  speed**. That is acceptable, and it is the reason not to go to 100 nF.
- **A ferrite on the whole sleeve** (phases and Halls through the same ring) is the textbook
  common-mode fix for a motor cable. See the ferrite card below before dismissing it.
- **Symptoms to watch** in VESC Tool: Hall errors, rough low-speed running, and noise in the
  phase current that is worse in sensored mode than in sensorless mode. Before blaming noise,
  check the wiring order after detection. Many reported "Hall errors" are wiring, not EMC.

### The IMU: the fix is no cable

You expect the IMU to be the most vulnerable part. You are right, but the reason changes the
fix. I2C is open-drain: every rising edge is a pull-up resistor charging the cable capacitance.
That is slow, single-ended and high-impedance. Noise does not make the readings noisy. It
**corrupts bits or locks the bus**: a glitch on the clock leaves the IMU in the middle of a byte,
holding SDA low indefinitely. An RC filter does not fix that, and a shield only reduces it.

1. **Put the IMU on the VCU board**, inside the LV box, which is bolted rigidly to the chassis
   near the middle of the quad. No cable means no antenna. The box is close to the centre of
   gravity, which is where you want an IMU anyway. Mount the box rigidly, with no rubber, or you
   will measure the box's vibration rather than the quad's.
2. **Pull-ups of 4.7 kΩ to 3V3, not 10 kΩ**, and the bus at 100 kHz. **CHECK** whether the new
   module already carries pull-ups; if it does, the two sets sit in parallel.
3. **In firmware:** bus-lockup recovery (up to 9 clock pulses until SDA goes high, then a STOP),
   plus a counter of I2C errors written to the log. Then you will know, rather than guess.
4. If the IMU ever has to go far away, use the LSM6DS3's **SPI** mode or a differential
   extender. Do not use a longer I2C cable.

The shielded 4-wire cable you bought is then free for a better job: the **front wheel-speed Hall**,
the longest signal run on the quad.

### CAN, the shielded cables and the VCU inputs

- **CAN:** twisted pair **plus the GND wire, twisted together**, as short as possible. Measure
  60 Ω between CAN-H and CAN-L with everything off. Your 88 Ω reading is still unexplained: two
  120 Ω terminations give 60 Ω. A TVS diode for CAN (e.g. PESD1CAN) costs cents. A common-mode
  choke (ACT45B type) only if a measurement asks for it: leave room for it on the board.
- **Shields: one end only, and to the side of the source.** CAN cable shield to the inverter box.
  Wheel-sensor shield to VCU ground at the VCU. Never use the shield as the signal return. Bond
  it with as short a connection as possible, because a long pigtail cancels the shield at high
  frequency.
- **Every signal twisted with its own return**: throttle (3 wires), brakes, wheel Hall, 12 V
  supply.
- **RC filters, sized to the signal** (CALC):

| Input | Signal it must pass | Filter | Corner | Note |
|---|---|---|---|---|
| Throttle (GPIO 35) | < 10 Hz | 1 kΩ + 100 nF | 1.6 kHz | already designed, fit it |
| Brakes (32, 33) | < 10 Hz | 10 kΩ + 100 nF | 160 Hz | already designed |
| Wheel Hall (34) | ~115 pulses/s at 40 km/h | 10 kΩ + **1 nF** | 16 kHz | do **not** use 100 nF: 1 ms edges would blur pulse timing |
| Rotor Halls (on the VESC) | ~1.7 kHz edges at top speed | 1–10 nF to GND | depends on the board's pull-up | CHECK what is fitted |

  The capacitor goes **at the pin**, with its ground on the same point as the ESP32's ground. The
  spike current then circulates in a loop a few millimetres long.

- **VCU supply:** TVS on the 12 V input (SMBJ16A class; a lead-acid battery on charge reaches
  14.4 V), reverse-polarity protection, and 100 nF + 10 µF at each module. Record
  `esp_reset_reason()` at every boot (you already do this in `boot.txt`), so that a brownout is
  never mistaken for EMC.

### Cable layout in a cramped chassis

1. **Battery + and − together**, zip-tied every 5 cm or twisted, from pack to VESC. A gap between
   them is a loop antenna carrying the 30 kHz ripple.
2. **The three phases bundled tight**, as short as the layout allows.
3. **Low-voltage cables cross power cables at 90°**, never parallel. Where they have to run
   together, keep the largest gap you can, and keep the chassis plate between them.
4. **Short battery leads** to the VESC. Long leads add inductance in series with the DC-link
   capacitors and raise the voltage spikes on the board. If the leads are long, the usual VESC
   practice is an extra low-ESR capacitor at the board end.
5. **LV box under the plate, cables leaving it on the side away from the VESC's cables.**

### Ferrites: an honest verdict

Your instinct is half right.

- **At 30 kHz a ferrite does nothing.** It is a few ohms. If the goal were to filter the PWM, it
  would be dead weight.
- **It is not meant for 30 kHz.** A clamp-on ferrite is a resistor that only common-mode current
  sees (current flowing the same way in every wire of the bundle). It works between ~10 and
  300 MHz, which is exactly where your switching edges and cable resonances sit. Typical clamp:
  100–250 Ω at 100 MHz with one pass, ×4 with two turns (ESTIMATE; material 31 for 1–300 MHz,
  43 for 20–300 MHz). Signal current goes out and back through the same ring, so it cancels and
  passes untouched.
- **Weight: 20–40 g** for a clamp on the phase sleeve, against a 38 kg vehicle (0.1 %).
- **When it is the right engineering:** when you cannot change the source or the routing. That is
  exactly your Hall-in-the-phase-sleeve case. It is also a 2-minute A/B test: clip it on, measure,
  and remove it if nothing improves.
- **When it is bad engineering:** as the first fix, to hide a loop you could have closed. That is
  probably what you have seen on chargers.

## 4. Before deciding: checks and a test plan

### Fifteen minutes with the multimeter (CHECK)

Status 2026-11-06, from Pol's answers. All with the pack disconnected:

| # | Check | Status |
|---|---|---|
| 1 | Motor case ↔ chassis, continuity (beep) | **Done: continuity.** The bracket bolts bite through the paint. No strap needed |
| 2 | Motor case ↔ a phase: must read open (MΩ). Then phase ↔ case on the **capacitance** range | **Insulation done, capacitance unresolved.** Phases A–B–C: continuity. Phase ↔ case: open (insulation good). The first readings (0.04–0.28 nF) were taken on the **Hall wires** by mistake. On the phases, the capacitance to the bare aluminium case and to the shaft reads **~0 nF**, against an expected 0.1–0.5 nF. Either the meter cannot resolve it or the contact is poor. **Not blocking:** the 20 nF bond is sized for anything up to ~2 nF. Last try, if you want it: phase → a point that beeps with the chassis (a screw head) |
| 3 | VESC aluminium plate ↔ VESC power ground (battery negative pad) | **Done: open.** The plate is isolated from the DC bus, so it can sit on a box bolted to the chassis |
| 4 | 12 V negative ↔ chassis | **Done: open** |
| 4b | Pack negative ↔ chassis | **Done: open.** Both domains float, as designed |
| 5 | Shared Hall/phase sleeve length | **Done: 50 cm.** DC leads, inverter to battery: ~40 cm |
| 6 | Capacitors on the VESC's Hall inputs | **Done, from the schematic:** the VESC 6 reference has 2.2 kΩ pull-ups and no capacitors. Flipsky's layout is not public |

### The test, systems-engineering style

You already have a baseline: **throttle spikes of +80 mV at 5 A with no RC** (MEASURED
2026-11-05), and 0 CAN errors at 49 A (EXP-002). Use it:

1. **Requirement first, written by you:** something like "with battery current at 40 A, the
   throttle reading varies by at most X mV at rest, and the CAN error counters, I2C error counter
   and resets all stay at 0." Pick X yourself and say why (hint: what fraction of the throttle span
   is an acceptable torque error?).
2. **One change at a time**, measured at 5, 20 and 40 A with the wheels in the air: baseline →
   throttle RC fitted → 10 nF bond → Hall capacitors → ferrite on the sleeve.
3. **Measure what you can:** throttle ADC peak-to-peak and CAN errors (logger), Hall errors (VESC
   Tool). With the scope, use its FFT and a home-made near-field probe: 2–3 cm of coax bent into a
   loop at the 50 Ω input. It gives relative readings only, which is enough for before/after. An AM
   radio tuned between stations also "hears" the PWM and the DC-DC, crudely.
4. **Scope safety (EXP-001):** the scope ground clip is mains earth. Never clip it to anything in
   the 48 V domain. In the 12 V domain, use a laptop without its charger, as DEC-004 says.

This becomes **EXP-004** in `07_experiments/` when you decide to run it.

### Exercise for you

Answer in your own words, in the app or in chat. I grade.

1. The pack is floating. Why does the common-mode current still flow, and where does it go today?
2. Why a **capacitor** from the VESC ground to the chassis, and not a wire? Give the safety reason
   and the EMC reason.
3. Your phase cables carry 120 A. Why are they mainly an *electric*-field problem for the Halls,
   and the battery leads a *magnetic*-field one? Use your motor's inductance.
4. Someone tells you to bond the 12 V negative to the chassis "for a better ground". Draw the
   loop that this creates and say which wire would carry the noise.
5. The wheel Hall gets 10 kΩ + 100 nF "to be safe". What breaks, at what speed?

## Sources

- Henry W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009: grounding, shielding,
  cable coupling. Reference text. Chapter numbers not verified here. Slides:
  [IEEE EMC Society, Ott](https://resourcecenter.emc.ieee.org//member-resources/knowledge-platform/emc_mem_kno_ott_010101_sld)
- Common-mode EMI in inverter drives, review: [IEEE Access 2021 (DOAJ)](https://doaj.org/article/16b218f429ac49998c3f303ee9447466) ·
  [motor cable effect on common-mode current](https://pub.pg.edu.pl/pl/download/117382-motor-cable-effect-on-the-converter-fed-ac-motor-common-mode-current)
- `I = C·dV/dt`, chokes and filters in drives: [PG&E, VFD EMI problems](https://PGE.com/assets/pge/docs/contact-us/report-an-issue/VFD-EMI_problems.pdf)
- TJA1050 receiver window −12/+12 V, bus pins −27/+40 V: [TJA1050 datasheet copy](https://manualmachine.com/datasheets/tja1050/5140383-datasheets-philips). Confirm on NXP's current revision
- Hall line filter, 22 nF and phase lag, ferrite on the phase bundle: [ODrive forum, Hall sensor noise](https://discourse.odriverobotics.com/t/hall-sensor-noise/11732) ·
  [endless-sphere, Phaserunner Hall problem](https://endless-sphere.com/sphere/threads/grin-phaserunner-with-cyclone-3000-hall-sensor-problem.97905/latest) ·
  [VESC forum, Hall noise in sensored mode](https://vesc-project.com/node/442)
- Hall errors that were wiring, not noise: [esk8 builders](https://electric-skateboard.builders/t/hall-sensor-detection-failure-vesc-4-12/108751) ·
  [endless-sphere](https://endless-sphere.com/sphere/threads/hall-sensor-error-but-tested-ok-with-a-multimeter.128093/)
- CAN wiring in VESC builds, shields one end vs both: [esk8.news, 4WD over CAN](https://forum.esk8.news/t/hows-everyone-wiring-4wd-over-can-these-days/90988)
- I2C rise time, capacitance and pull-ups: [NXP UM10204, I2C specification](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)
- CAN physical layer, split termination: [TI SLLA270](https://www.ti.com/lit/an/slla270/slla270.pdf)
- VESC 6 reference schematics, Hall pull-ups R42–R44 = 2.2 kΩ: [vesc-project.com, schematics page](https://vesc-project.com/node/311)
  ([VESC 6.4](https://vesc-project.com/sites/default/files/Benjamin%20Posts/VESC_6.pdf),
  [VESC 6 MK5](https://vesc-project.com/sites/default/files/Benjamin%20Posts/VESC_6_mk5.pdf)).
  Flipsky's Mini 6.7 Pro is "based on VESC 6.6" ([Flipsky](https://flipsky.net/products/mini-fsesc6-7-pro-70a)); its own schematic is not published
- Your own evidence: [EXP-001](../07_experiments/EXP-001-ground-loop-vesc-pc.md),
  [EXP-002](../07_experiments/EXP-002-spi-noise-can-logger.md), [VCU pinout](../05_firmware/vcu-design/vcu-pinout.md)
