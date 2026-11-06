# EXP-001: Ground loop between the VESC and the PC

**Status:** not measured yet. Opened on 2026-09-07 after destroying an ESP32.

## Question

How much common-mode voltage is there between the VESC ground (referenced to the 13S battery,
floating) and the PC ground (referenced to mains earth), and how much current flows when the
two are joined through the CAN bus ground wire?

## Why this experiment exists

On 2026-09-07 an ESP32-WROOM-32 was destroyed while fitting the first CAN sniffer.
See the [incident](#incident-2026-09-07) below.

This **was already anticipated** in `03_hardware/open-questions.md`, Risk 2:

> "Ground loops between the PC ground and the VESC's (referenced to the battery) as soon as
> current flows. It can kill a regulator."

And in `01_plan/backlog.md`: *"30 min of oscilloscope before building anything, to avoid it"*.
It was fitted without taking that measurement. Cost: one board.

## Hypotheses

**H1.** With the VESC off, the potential difference between its ground and the PC's earth is
small (< 1 V DC, < 5 V AC). Joining them does nothing.

**H2.** With the VESC power stage switching, the battery + VESC + motor assembly swings in
potential relative to earth at high frequency, through capacitive coupling between the motor
phases and the chassis. The amplitude exceeds the ±7 V common-mode range a non-isolated CAN
transceiver can take.

**H3.** When both grounds are joined, that swing pushes current through the joining wire
according to `I = C · dV/dt`. That current is what degrades the pins and the 3.3 V rail.

If H2 and H3 are confirmed, the conclusion is that **any non-isolated connection between the
loaded VESC and mains-referenced equipment is unsafe**, whatever the wiring. It is not an
assembly mistake: it is a property of the system.

## Method

Three measurements, from least to most risk. **Don't skip steps.**

### M1 — Static potential (multimeter, safe)

Multimeter between the **battery negative** and the **PC earth** (chassis screw or the shell of
a metal connector). Nothing else connected between the two systems.

Measure DC and AC, in three states:

| State | V DC | V AC |
|---|---|---|
| VESC off | | |
| VESC on, motor stopped | | |
| Motor turning at light load | | |

> [!warning] Mains voltage may show up
> If the PC's power supply leaks through its Y capacitors, tens of volts AC can be read. It is
> high impedance and low current, but **don't touch the probe tips with your skin**.

### M2 — Loop current (multimeter, safe)

Join the two grounds **through a 1 kΩ resistor**, not directly. Measure the voltage drop across
the resistor. `I = V / 1000`.

Same three states as M1. The resistor limits the current to a harmless value and turns the
problem into a voltage reading.

### M3 — Waveform (oscilloscope)

> [!danger] How NOT to do it
> **Do not clip the oscilloscope ground to the VESC.** The scope's ground clip is tied to mains
> earth. Clipping it to the VESC creates exactly the short being measured, through the scope's
> own cable.

The right way:

- Ground clip → **PC earth / chassis** (where it is already referenced).
- Probe tip (×10) → **VESC battery negative**.

The probe is 1 MΩ, so it does not really join the grounds: it measures the potential without
letting any significant current through. Capture during a load ramp.

What to look for: high-frequency spikes synchronised with the switching. Note peak-to-peak
amplitude and frequency.

### M4 — Bisection (optional, if M1–M3 are inconclusive)

Repeat M2 with clip-on ferrites on the joining wire.

- Clear improvement → the dominant mechanism is high-frequency conducted EMI.
- No change → it is a low-frequency ground loop.

## Decision criterion

| Result | Conclusion |
|---|---|
| M3 shows spikes > ±7 V | H2 confirmed. Galvanic isolation mandatory, not optional. |
| M2 gives > 10 mA under load | H3 confirmed. It quantifies the damage. |
| Everything < 1 V and < 1 mA | Hypotheses refuted. Look for another cause of the 07-Sep failure. |

## Data

Pending. → `06_data/`

## Conclusion

Pending.

## Limitations

- The multimeter is not true-RMS at high frequency: M1 in AC is indicative, not exact.
- The phase→chassis capacitive coupling is not measured directly, only its effect.
- The result depends on this PC and this electrical installation. With another wall socket the
  numbers can change.

---

## Incident 2026-09-07

**Setup:**

```
PC (mains earth) --USB--> ESP32 --3V3--> MCP2515/TJA1050 module --CAN-H/L--> VESC (13S, ~54 V)
                                                                 --GND-----> VESC
```

The VESC was **on** with the battery fitted. It was **not** connected to the PC over USB (a
ground loop through two USB cables was ruled out by the user).

**Sequence:**

1. Wired as above. CAN module powered from the ESP32's 3V3 pin.
2. First firmware upload attempt: fails with `No serial data received`.
3. The ESP32 heats up until a finger cannot stay on it.
4. The module's VCC is removed. The module's LED **keeps blinking** → the module was being
   powered through the SPI pins (current coming out of the ESP32's GPIOs).
5. The COM port disappears from the system.
6. With everything disconnected and only USB, the board **keeps heating** and does not respond
   to `esptool`, not even with BOOT + EN.

**Diagnosis:** internal short in the ESP32. The USB-serial converter chip still enumerates
(Windows plays the connection sound) because it is a separate part powered by USB's 5 V — that
does **not** mean the ESP32 is alive.

**Design fault identified:** powering the CAN module from the ESP32's 3.3 V rail puts that
rail in direct electrical contact with the transceiver's CAN side, which faces a switching 54 V
system. There is nothing in between. Even with a perfect pinout, the setup was already
vulnerable.

**Not confirmed:** that the exact mechanism was the ground loop. It is the hypothesis most
consistent with the data, but **unmeasured it is not a fact**. That is what this experiment
is for.

## Rules that come out of this

1. Never connect the VESC to anything mains-referenced without galvanic isolation.
2. Always wire with everything off. When connecting: GND first, VCC last. When disconnecting,
   the reverse.
3. Power peripheral modules from their own supply, not from the microcontroller's 3.3 V pin.
4. Test the firmware against a toy CAN node before going near the VESC.
5. Before fitting new hardware, reread `open-questions.md`. The warning was written.
