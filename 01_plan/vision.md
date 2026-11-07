# Vision — ePWT

Captured on 2026-08-31 from the complete strategic braindump.
**This file is not executed.** It exists so that nothing is lost and so that the active cycle
can ignore it in peace. It is reviewed every ~3 months, not every week.

---

## Goal 0 — The only one that is not negotiable

Become a technically solid engineer, able to work on electrical and electronic systems,
control, software and electric motors. Everything else is subordinate to this.

**Professional context:** ~2 years of experience, automotive engineering (combustion engine
calibration). Move to Israel planned (date open; the project continues there without
interruption). Target sectors: robotics, semiconductors, defence, drones, electric motors,
electronics, control.

**An advantage I already have and must not treat as zero:** calibrating an electric motor
(current maps, torque curves, field weakening) is conceptually close to calibrating a
combustion one (injection, ignition). The craft transfers; the domain doesn't.

---

## The four layers

### Layer 1 — The substrate: the quad
Physical learning platform. The hardware **already exists and works** (motor, VESC, 13S5P
battery, BMS, ESP32). It is not a mechanical fabrication project.

Role of the hardware in this project: **source of measured parameters and validation bench**,
not an object to redesign.

Technical areas to develop: control (classical, PID, electric motors, stability, dynamic
response, traction control, launch control), power electronics (inverters, sensors, batteries,
BMS, communications, embedded), software (architecture, modularity, interfaces, Git/GitHub,
PRs, maintainable code).

#### Knowledge areas to develop

Starting point: automotive engineering, mechanical base. The expansion goes towards
electronics, software, control and electrical systems. From fundamentals to advanced.

**Control** — classical control, PID, MPC, electric motor control, strategies, stability,
dynamic response, system modelling, constrained control, traction control, launch control.
Don't implement without understanding the mathematics and physics underneath.

**Electrical and electronic systems** — motors, inverters, power electronics, sensors,
actuators, batteries, BMS, communications, microcontrollers, embedded systems, electronic
architecture.

**Software** — the Python base for analysis is reasonable; the discipline of a software
engineer is not. Historically this part was delegated to teams. That is why it matters
especially: architecture, how to structure a project, separate responsibilities, organise
modules, design interfaces, manage dependencies, maintain a large project, maintainable code,
Git, GitHub, Pull Requests, branches, code review, documentation. **The goal is not knowing how
to program: it is knowing how to build software with the right architecture.**

### Layer 2 — The method
- **Two-week cycle with mentors.** The engine of the project. External deadline, real critique,
  and the obligation to explain. It solves procrastination, overload and checking understanding
  at the same time.
- **Learning by doing:** build, experiment, get it wrong, analyse, explain, rebuild. No passive courses.
- **Explaining as a test of understanding.** If I can't explain it simply, I don't understand it.
- **First principles, rationed.** Deep in the core (Clarke/Park, inverter, electric machine,
  longitudinal dynamics). Copy without shame everywhere else.

### Layer 3 — The infrastructure
Git repository as the single source of truth. Short `CLAUDE.md`. Skills and agents **only when
they encode a process I have already done three times.**

### Layer 4 — Frozen (see `backlog.md`)
Personal brand, content, company, second brain, information agents. Recognised as valuable.
Postponed by explicit decision, not discarded.

---

## Personal problems the system must attack

These are not decoration: they are the reason the system has the shape it has.

| Problem | How the system attacks it |
|---|---|
| Without a deadline, I procrastinate indefinitely | Two-week cycle with a deliverable to mentors |
| I get overwhelmed seeing everything pending | Only the active cycle exists; the rest lives in `backlog.md` |
| I look for the perfect plan instead of executing | Detailed planning only for the current cycle; the next ones, in one line |
| I say "yes, I understood" under pressure without having understood | Obligation to explain at every review; the examiner agent |
| Ideas scattered between paper, WhatsApp and nowhere | `backlog.md` as the single destination |
| I understand but explain badly | Fortnightly presentations, in English |
| Social shyness / public speaking | Presentations now; video later |

---

## Philosophy of AI use

**Don't delegate cognition: augment it.** The AI must not give me conclusions I should reach
myself. It should extract what is relevant, explain fundamentals, generate counter-arguments,
find errors in my reasoning and **examine me**.

Practical corollary: an agent that hands me a synthesis to accept has negative value. An agent
that asks me "why do you think that?" has high value.

**Examiner agent (approved, not built yet):** fed with real textbooks of the domain, with the
role of questioning me and checking whether I master the theory before a review. It gets built
when there is material and a routine to encode. One, not ten.

**Discarded:** a fleet of 10+ "expert" agents. A subagent is the same model with another
prompt: it simulates peer review without bringing its epistemic value.

**Discarded:** an architecture portable between models. Decision: Claude Code, no migration
plan. Portability is a problem you earn, not one you prevent.

### Harness engineering — what does apply

Pol has studied prompt engineering, context engineering and harness engineering, and did a
Claude Code course. The methodological reference is the philosophy of Boris, the creator of
Claude Code. He wants to apply it for real, not have a long conversation with an LLM.

What is already implemented and works:
- Short `CLAUDE.md` at the root, with its own `CLAUDE.md` per area (`04_model/`, `05_firmware/`).
- The repository **is** the external memory. Each session gets pointers, not dumps.
- Context bounded by folder. One session = one task with a checkable goal.

What is pending and **only comes in when there is real friction**:
- Skills that encode repeated tasks (criterion: having done them by hand 3 times).
- Explicit verification loops: goal → execute → check → correct → repeat.
- Agents in parallel (one researches, another implements, another validates). Attractive idea,
  no value shown yet in a one-person project.

**Guiding principle: fewer prompts, more tools.** Prefer scripts, skills and structured context
to explaining the same thing every time. But build the tool *after* having done the task by
hand, never before.

---

## Mindset: learning from the best

Two ideas Pol wants to guide the project, which in practice contradict each other unless rationed:

**Don't reinvent the wheel.** The companies that already work have spent huge amounts
developing strategies, products and processes. Studying what works and adapting it is smarter
than deriving everything from scratch.

**First principles.** Understand the real physics, question assumptions, rebuild the solution
from the fundamentals.

**The rule that reconciles them:** first principles in the core he wants to master (motor,
inverter, control, vehicle dynamics). Copy without shame everywhere else (build systems,
protocols, libraries, tooling).

A corollary that has already come up in practice: Motor Control Blockset ships FOC already
implemented. Using it directly would give a quad that works and an engineer who has learned
nothing. **First build it from the equations, then compare it with the reference
implementation.** The difference between the two versions is the learning.

**Israel and the startup culture.** One of the reasons for the move is to learn from that
ecosystem: try, fail, learn, iterate, don't give up. There is no startup idea yet, and that is
fine — first knowledge, experience and spotting real problems. Don't force an idea.

## Why depth, and not a "generalist orchestrator"

Added on 2026-09-06 after reviewing the dominant discourse about the future of engineering.
It is the decision criterion for choosing where to spend the hours.

**The discourse going around:** "specialising matters less and less; what matters is
understanding a bit of everything, framing problems well and letting AI agents solve them."

**Why it is bought so easily:** the voices spreading it live off a generalist audience. "You
don't need to go deep" sells far better than "spend 200 hours with the machine's equations".
Source bias, not evidence.

### The technical argument that takes it apart

> If generating is free, **the bottleneck becomes verifying.**
> And you can only verify what you truly understand.

An agent writes a complete FOC in 30 seconds. The question that separates a senior from a
prompt operator is: *is it right?* Is the current loop bandwidth consistent with the motor's
electrical time constant? Does the anti-windup hold under voltage saturation? Why does it
vibrate at 200 rpm? That is not orchestrated. It is known.

It is the same thesis as Karpathy's on jagged entities: models shoot ahead in verifiable
domains and stall where verification is hard or absent. The human who knows how to verify is
the scarce resource.

### What is true in the discourse

Breaking problems down precisely, designing context and knowing when to use the simple tool
**are** new and valuable skills. But they don't replace the domain: they multiply it. Breadth
without depth does not produce an architect; it produces a project manager unable to audit anyone.

The real career pattern is a **T**: generalist at the start — shipping whole systems alone,
which is exactly what ePWT is — and specialist from senior on. Not "generalist forever". 2026
hiring reports suggest the market pays for depth (gaps of 30–50 %), though they are recruiting
sources and should be taken as direction, not hard data.

### Operational consequences

1. **Verification rule.** What an agent generates in the core (motor, inverter, control,
   dynamics) must be explainable without looking at it. If not, it is not done.
   Build systems, protocols and glue code: copy without shame.
2. **The digital twin is the verifier.** Model + real bench = *ground truth*. It lets you
   **check** instead of believe. Almost no candidate has that.
3. **Deliberate practice per session.** One isolated skill per session, not the whole system at
   once. Less cognitive load, more retention.
4. **Breadth comes by itself.** Once a control loop is truly mastered, extending it to state
   estimation, batteries or perception is transfer, not starting from scratch.

**Target identity — the sentence to be able to say in an interview:** not "AI agent architect",
but *a powertrain control engineer who verifies with models and real data, and who works with
agents*. The second profile is scarce; the first, in 2027, everyone will have.

### Reading of the Israeli market (review on arrival)

Consistent signal in job posts: motor control in bare-metal C/C++ on TI C2000, embedded, and
bring-up / integration / validation of autonomous systems and physical robotics. It is an
economy of hardware, defence and autonomy, not of SaaS. More than half of the startups linked
to the DDR&D work on UAVs.

**Consequence:** the quad does not have to become a drone. The machine is the same — a PMSM
with FOC — and the transferable core is identical: FOC + embedded + validated model. The
adaptation to the market is one of **framing and of a technical layer added later** (state
estimation / sensorless control), not a change of roadmap.

**Caution still to confirm:** a good part of classified defence work requires citizenship and
security clearance. The realistic entry target is the commercial and dual-use band — robotics,
mobility, semiconductors, autonomy — which has no such filter and uses the same physics.

---

## Technical horizons (not now, but this is where we are going)

- Digital twin in Simulink: longitudinal dynamics + electric machine, parameterised with real
  measurements and validated against tests.
- Torque control / current loop in simulation, then on the ESP32 (Model-Based Design).
- Traction control and launch control.
- MPC — **needs a validated model first.** It is sequence, not rejection.
- Own telemetry and logging; data analysis in Python.
- Perception, cameras, autonomous systems, companion robot. Very far off, but the quad must
  stay a platform that grows for years. The project does not "end".

---

## Constraints and hard data

- **Time available:** ~2 h a day, weekends included, at the time of writing (since 25 Oct:
  45–60 min Tuesday to Thursday, see the roadmap).
- **Mentors:** engineers and PhDs in combustion engines, every 2 weeks. They can bring
  engineering rigour, critique of method and accountability. **They cannot validate the EV/FOC
  domain** — that needs another source.
- **Language:** everything in English since 3 Nov 2026 (conversation, repo, presentations,
  LinkedIn). English is not a main goal, but it is infrastructure: Israeli recruiters will
  read the repo.
- **Secondary but real personal aspects:** public speaking is hard and there is some social
  shyness. Presentations and, later, video are part of the cure. Don't make it a goal of the
  project, but don't avoid it either.
- **Safety:** see `CLAUDE.md`. The battery margin is the real risk of the project.
