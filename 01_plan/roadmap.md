# Roadmap by cycle

Rule: **only the active cycle is planned in detail.** The next ones exist as direction, not as
a plan. They become concrete when they open. If this list starts growing downwards with detail,
that is the sign I am looking for the perfect plan again.

Budget: ~14 h per cycle (1 h a day since 20 Oct; before, 2 h a day).

## Real calendar

> [!warning] Holidays 10 → 27 September
> No computer. **No work is planned inside that gap.** A project that demands working on
> holiday in its first month does not reach month twelve.

| Cycle   | Dates           | Goal                                           | Review            |
| ------- | --------------- | ---------------------------------------------- | ----------------- |
| **C00** | 2 → 9 Sep       | Kickoff with mentors + first measurements      | Tue 8 or Wed 9 Sep |
| —       | 10 → 27 Sep     | *Holidays*                                     | —                 |
| **C01** | 28 Sep → 11 Oct | Longitudinal model before data (pivot 8 Oct) — **done** | Fri 9 Oct |
| **C02** | 20 → 30 Oct     | Motor + inverter: **model it and be able to explain it**. No validation. See [C02](cycles/C02.md) | **Fri 30 Oct** (cancelled, merged into C03) |
| **C03** | 31 Oct → 13 Nov | dq model (L3), first control (open/closed loop, PI) and the motor in Simulink (L4). See [C03](cycles/C03.md) | Fri 13 Nov        |
| **C04** | 14 → 27 Nov     | Direction (1 Nov): validate the motor model with the CAN logs | Fri 27 Nov        |
| **C05** | 28 Nov → 11 Dec | Direction: vehicle validation (coast-down, acceleration) with the logger | Fri 11 Dec        |
| **C06** | 12 → 25 Dec     | Direction: close the validated model; control unit v0 if it fits. Christmas: probably moves | Fri 25 Dec |

## Skill gates — a cycle does not close without its gate

Since 2026-11-04 ([DEC-007](../08_decisions/DEC-007-skill-gates-and-ros2-telemetry.md)). Pol's
request: *"I note things down and never do them"*. So the software and systems skills are
**blocking points**: if a cycle's gate is not done, there is no deck and no review, and the
next cycle does not open. Each gate fits inside the cycle's 14 h (1–3 sessions); it is not a
side course. Method for every code gate: skill `software-con-ia` (Pol writes the contract and
the acceptance test with a number, the AI writes the code, one C trap per change).

| Cycle | Gate (done = the evidence exists in the repo) | Skill it builds |
|---|---|---|
| **C03** · 13 Nov | First `REQ-MOD` in `00_system/`: the motor model's acceptance criterion **with a number**, written before C04 measures it | Systems engineering, sim-to-real |
| **C04** · 27 Nov | **Python on data:** Pol writes the contract and acceptance test of the model-vs-CAN-log comparison; the AI writes it; Pol explains its output. **Reading C #1:** Pol explains, in his words, how `can_logger` decodes a VESC frame (traps 4 types/scales and 5 byte order) | Python on real data · reading C |
| **C05** · 11 Dec | **Reading C #2:** how `can_logger` keeps time and writes to the SD without losing frames (traps 1 overflow, 3 interrupts, 8 blocking). Coast-down fit script with its own acceptance test | Reading C · real time |
| **C06** · 25 Dec | **VCU contract before any VCU code:** `REQ-VCU` with numbers, module contracts, and the safe state when something fails (traps 9 state machines, 10 watchdog) | Real-time C architecture · safety |
| **VCU** · Q1 2027 | Every VCU release passes steps 4 and 5 of the verification ladder (a number, and 30 min with provoked faults, error counters at 0) | Real-time C · validation |
| **Telemetry** · after VCU v0 | **ROS 2 on a Raspberry Pi:** `REQ-TEL` (rate, latency, frame loss, range) before choosing the radio; a node that reads the VCU's CAN, records (rosbag) and shows it live on the PC | ROS 2 · Linux · communications |

A gate can move to the next cycle **only once**, and only with a line in the cycle log saying
why. Twice is the signal the plan is wrong, not Pol.

**Sequence decided on 20 Oct:** motor + inverter model → data logger → validation (coast-down,
model ↔ vehicle correlation). No logger, no data; no data, no validation.

**Updated 1 Nov:** the CAN logger came early and works (31 Oct, EXP-002), so the data link is
in place. Order agreed with Pol:

1. **C03 unchanged:** dq model and PI loop in Simulink. Inverter and motor.
2. **Validate the motor with the logs:** the VESC's current, erpm, duty and voltage against the
   model (e.g. duty × voltage against erpm must give λm).
3. **Control unit v0** (Dec–Jan): throttle and brake → ESP32 → current command over CAN → VESC.
   No control, with the protections in the code (brake + throttle = zero torque, CAN timeout in
   the VESC). Architecture and sensors in [DEC-005](../08_decisions/DEC-005-vcu-architecture.md);
   review DEC-004 first.
4. **IMU and wheel speed** recorded on the SD.
5. **Traction control:** first in Simulink, then on the ESP32.
6. **Telemetry over ROS 2** (2026-11-04, DEC-007): a Raspberry Pi above the VCU, reading its
   CAN and sending it to the PC over a radio link. ROS 2 never runs inside the VCU, which stays
   real-time C. No autonomy: there is no need for it on the quad.

**Out, by Pol's decision:** the BMS over CAN (the VESC already gives pack voltage and current;
the focus is motor and inverter) and the pack temperature probe (DEC-005, 1 Nov). Reminder: the
control unit teaches vehicle control and embedded C, not the inverter; the inverter is learned
in the model.

**End of 2026: model validated against the real vehicle.** That is the goal of the year.

After C06 (not before): traction control, launch control, and **then** MPC — which needs
exactly what C06 produces, a validated model.

### Long horizon — one line per quarter, and nothing more

Deliberately vague. Making it concrete now would be looking for the perfect plan.

| Quarter | Direction |
|---|---|
| **Q4 2026** (C01–C06) | From measured hardware to a validated model |
| **Q1 2027** | Control implemented: from the model to the ESP32. Firmware gets serious here |
| **Q2 2027** | Vehicle functions: traction, launch. Telemetry over ROS 2 on a Raspberry Pi. And MPC if the model holds |
| **Q3 2027+** | The quad is a platform: a learned controller validated against the classic one (if it meets a requirement); an autonomous drone is a separate project |

## How a cycle works

The cycle is the engine of the project. Without a ritual, it is just a folder name.

> [!todo] Opening — 1 session, the day after the review
> 1. Read the previous cycle's close. What went wrong is carried over, not forgotten.
> 2. Pick **one** goal. One. If it needs an "and", it is two cycles.
> 3. Define the deliverable: what is shown on review day.
> 4. Write the daily plan.
> 5. Everything that does not fit → `backlog.md`.

> [!tip] During — every session
> Close by writing **one line** in the log: what I did, what I learned, what is left.
> It is the cheapest and most valuable habit in the system. Without it, every session starts blind.

> [!success] Close — the last sessions before the review
> 0. **Skill gate done?** (table above). If not, it is done now, before anything else. No
>    gate, no deck.
> 1. Fill in Result / What I learned / What went wrong.
> 1b. **Update the V** (`00_system/verification.md`, 10 min): which requirements were closed
>    and with what data, and the new requirements the cycle brought up. In the review, one
>    slide: what is verified and what is not. Skill `ingenieria-sistemas`.
> 2. **Cycle exam** (in ePWT Bench): Claude asks, I answer from memory, a verdict per answer.
>    **My graded answers are the deck's script.**
> 3. Agree the slide list **before** anything is built (lesson from C01).
> 4. Deck with the `review-deck` skill: `_check.py` and `_audit.py` at zero before presenting.
> 5. Rehearse out loud with the likely question for each slide (speaker notes).
> 6. If I can't explain it without notes, **it is not finished**.

### The review, in 45 minutes

The mentors are combustion engine engineers: they cannot validate FOC, but they can validate
the engineering reasoning. The format uses what they do know:

| Time | What |
|---|---|
| 5 min | What I said I would do |
| 15 min | What I have done, with data |
| 10 min | **What I don't understand** — the most valuable part |
| 10 min | Critique: does the reasoning hold? |
| 5 min | Goal of the next cycle |

The 10 minutes of "what I don't understand" are the core. Showing only what works turns the
review into theatre and wastes two PhDs.

## How I measure whether this works

The goal is "be a better engineer", which cannot be measured. These four indicators can, and
they are reviewed **every 3 cycles**, not every week:

1. **Can I explain something today that I couldn't 6 weeks ago?** Without notes, to someone
   who doesn't know the subject. It is the only indicator that really matters.
2. **Does the model predict better?** From C06 on, the correlation error is a number that goes
   down or doesn't. It admits no self-deception.
3. **How many cycles have I closed on time?** It measures the system, not the knowledge. If
   two in a row fail, the problem is the plan, not me.
4. **How many decisions do I have written down with their why?** It measures whether I am doing
   engineering or just touching things.

> [!warning] What is NOT measured
> Hours spent, files written, lines of code, commits. All of that can go up without learning
> anything. Optimising a false indicator is worse than not measuring.

## Why this order

Each cycle consumes the output of the previous one. C02 cannot start without C01's numbers.
C04 means nothing without C03's machine. MPC cannot be implemented without C06.

It is not an arbitrary sequence: it is the real dependency chain. Skipping a link produces a
system that seems to work and cannot be debugged, because you don't know which layer is lying.

## The data logger: why it does NOT go first, and the exception

> [!note] History
> Written before building it. The logger exists since 31 Oct 2026 and records under load
> without depending on the VESC's USB: what follows is the reasoning at the time.

**The real problem:** today I can only record with the motor unloaded. With the vehicle
running, the VESC's USB drops out under load. Logs under load would need a custom ESP32 data
logger — which does not exist yet.

**So should it be built first?** No, for two reasons:

1. **C01 doesn't need it.** Phase R, pole pairs and back-EMF are measured with the motor
   stopped or turned by hand. Multimeter and oscilloscope. Zero software.
2. **I don't know yet what to measure.** A logger is designed from the signals the model asks
   for. Building it before the model is guessing which channels, at what rate and with what
   resolution — and guessing wrong costs weeks of embedded work.

**The exception that does deserve to come early (30 minutes):** diagnose the USB dropout. The
symptom is "under load" → it points to EMI from phase switching or to a ground loop. But one
detail changes the calculation: **a coast-down test is, by definition, torque-free** —
accelerate, release, and let the vehicle slow down by itself. With almost no phase current,
it is plausible that the USB does **not** drop out.

And the coast-down is exactly the validation test C02 needs.

So, before assuming the logger is needed: try a coast-down recording over USB. If it works,
**C02 is validated without building anything** and the logger stays where it is, in C05. If it
doesn't, I have the fact for certain instead of an assumption — and I know the logger is a
real blocker.

Half an hour of oscilloscope on D+/D- and on the 5 V rail during a load ramp completes the
diagnosis. See `03_hardware/open-questions.md`.

## What changes now that I know which toolboxes I have

Verified on 2026-09-01: the student licence includes **all 40 toolboxes**, including Motor
Control Blockset, Simscape Electrical, Vehicle Dynamics Blockset, Powertrain Blockset, MPC
Toolbox and Embedded Coder. See `08_decisions/DEC-002-technical-environment.md`.

This does not speed up the roadmap. It makes it **more dangerous**, and it is worth saying
clearly:

Motor Control Blockset ships a finished FOC for PMSM. Dragging that block in gives a quad that
works and an engineer who has learned nothing. The declared goal of the project is to
understand FOC, not to use it.

**Rule for the whole roadmap:** first I build it from the equations, then I compare it against
the reference implementation. The difference between my version and theirs is the learning
content — that is where what I didn't know I didn't know lives.

Two concrete consequences:
- **C03/C04:** build Clarke, Park and the current loops by hand before opening any MCB example.
- **MPC (post-C06):** stops being out of reach. MPC Toolbox is there. It still needs C06's
  validated model, so the sequence does not change — it just stops being a distant horizon and
  becomes a real goal ~6 months out.

## What is NOT in this roadmap, on purpose

Mechanical redesign, battery mounting, brackets, chassis. The hardware is the plant and the
validation bench, not the object of the work. Hardware changes, yes — when the model or the
data ask for them, not on my own initiative.
