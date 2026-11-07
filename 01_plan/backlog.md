# Backlog — everything NOT done now

The single destination for ideas. If something does not fit the active cycle, it comes here and
leaves my head. None of this is discarded; it is **postponed with an entry condition**.

Rule: an entry is only activated when its condition is met, and then it becomes the goal of a cycle.
Concrete to-dos that are already decided (buy, wire, test) live in [Quad Tasks](tasks/), not here.

---

## Separate projects (outside this repo, by my own decision)

**Personal second brain + an LLM on it.** Knowledge from university, Formula Student,
calibration, work, projects. Obsidian as a candidate. Reference mentioned: Karpathy's work on a
wiki/LLM on GitHub.
*Why outside:* it is a knowledge management project, not a powertrain engineering one. Mixing it
in here was the cause of the initial overload.
*Note:* this repo's `02_knowledge/` is already plain Markdown and opens in any viewer without
conversion. The personal second brain can absorb it later.

**Information / news agents.** A weekly synthesis on robotics, defence, drones, semiconductors,
AI, the Israeli ecosystem, and specific technical voices.
*Argument for (his, valid):* he does not want to waste time on social media; he prefers filtered
signal from people whose actions have real consequences.
*Risk to watch:* a synthesis accepted without questioning is delegated cognition. It must
deliver **sources + questions**, not conclusions.
*Done since September 2026:* it is the Monday weekly brief, outside this folder.

---

## Inside this project, later

| Idea | Entry condition |
|---|---|
| **Examiner agent** (fed with textbooks, questions me before reviews) | Chosen reference material exists and ≥3 cycles of routine to encode |
| ~~**Own skills**~~ | **Activated 2026-10-25:** `review-deck`, `leccion` and `corregir` exist. Next ones (analyse data, document a decision): same rule, 3 times by hand |
| **CI: compile the firmware on every push** | Condition met (2026-10-31): there is own firmware now. When to do it still to be decided |
| ~~**Own telemetry logger (ESP32 + CAN)**~~ | **Done 2026-10-31**, brought forward by Pol: `05_firmware/arduino/can_logger/`. Records under throttle without errors (EXP-002) |
| **Dashboard / Python analysis of the logs** | Condition met: there are CSVs. Today `04_model/scripts/can_log_decode.py` exists (summary + figure); more when the analysis asks for it |
| **End-of-session hook: warn about uncommitted work** | Having closed 3 more sessions forgetting the commit. See the note below |
| **Traction control, launch control** | Validated model + torque control working |
| **Launch: take up the chain backlash first** (Pol, 2026-11-05) — a small torque (~1–2 A) before the launch so the slack is already gone, instead of a very tight chain, which only adds friction | With launch control. The chain is refitted one link longer (6 Nov, EXP-003) |
| **VESC status rate over CAN** — today ~21 ms, so a timeout is measured with ±21 ms resolution | When a requirement needs a finer measurement than 21 ms |
| **MPC** | Validated model. MPC without a model is impossible by definition |
| **Perception, cameras, autonomy, companion robot** | Very far. Keep as a horizon, don't plan |
| **Diagnose the VESC's USB dropout under load** | Known failure in the VESC community (EMI / ground loop / pull-ups). 30 min of oscilloscope before building anything to avoid it |
| **Decide `l_in_current_max` (today 40 A = the BMS continuous limit)** | Came out of the C01 model: above 9 km/h every full-throttle acceleration sits at 40 A. Taken to the C01 review as a question for the mentors. **2026-11-05:** Pol says it was set to 50 A ("let the BMS cut"), now going to **39 A**. Rule: the VESC limits below the BMS so the BMS never opens the pack under load. 1 A margin is about the VESC's current-reading error; 35–38 A is safer. Re-export the XML and write the number into `baseline.md`. Also in Quad Tasks, section 8 |
| **id–iq operating map** (Pol, 2026-11-05) — current-limit circle, voltage-limit ellipses at several speeds (centre at id = −λ/Ld), MTPA curve, field-weakening path, and the measured operating points from the CAN logs on top | dq model reliable enough (after C03-SA). Rotor construction known since 6 Nov (inset magnets, `03_hardware/motor-parameters.md`) |
| **Field weakening and MTPA settings from the model** — choose `foc_fw_current_max`, `foc_fw_duty_start` and `foc_mtpa_mode` in Simulink before touching the quad. The VESC firmware (FW 7.01) already implements both; nothing to rewrite. **Safety first:** with field weakening, a VESC trip at high speed lets the back-EMF exceed the 57 V limit → simulate the overshoot before enabling it | id–iq map done; REQ-SAF-02 (bus voltage) written |
| **Torque from vehicle data** (Pol, 2026-11-05) — estimate wheel torque from acceleration (F = m·a + drag + rolling + slope) to check Kt and an MTPA table without a dynamometer | Working IMU + wheel speed on the logger, and a flat run. Needs an estimate of rolling resistance |
| **Current-loop decoupling** (`foc_cc_decoupling`, off) — feedforward of the ω·L·i and ω·λ cross terms. At 5480 rpm the electrical speed (~1720 rad/s) is close to the 2000 rad/s loop bandwidth, so it may matter at top speed. Test in the model first: current tracking error at high speed, with and without | dq model with the current loop (C03-SA onwards) |
| ~~**Measure the pack's `R_int`**~~ | **Done 2026-10-31:** ≈ 0.18 Ω battery + cables + BMS, from a CAN log (EXP-002). Still to go into `04_model/params/` (Quad Tasks, section 2) |
| **`si_wheel_diameter` 0.30 m vs `2·r_roll` 0.31 m** | Decide when the **rear** roll-out is done (the 6 Nov one was the front wheel: 146 mm, sensor only) |
| **CG height (`h_cg`)** | MISSING. Needed by the L2 load transfer (C01 exam, block I) |
| **EXP-001 (ground loop) not measured** | **Condition met 2026-11-05:** the ESP32 now sends torque to the VESC (can_throttle). Done safely by running the laptop on battery with the VESC USB unplugged. Measure it before the VCU rides with a laptop attached |
| **Wheel speed: filtering method** | `can_logger` data with the quad rolling (needs the new card). Compare a one-turn average, per-gap calibration and a filter; only then move it to the ESP32 (Pol, 2026-11-01) |
| **IMU to the logger** | The new GY-LSM6DS3 arriving. I2C on GPIO 21/22, address 0x6A. On the VCU board since 6 Nov (DEC-008) |
| **BMS over CAN** | Only if per-cell voltage or temperature is needed. Pack voltage and current already come from the VESC, and the focus is motor and inverter (Pol, 2026-11-01). The BMS stays as a passive backup, untouched ([DEC-005](../08_decisions/DEC-005-vcu-architecture.md)) |
| ~~**Brake switches to the VCU**~~ | **Measured 2 Nov:** normally open, dry contact; only the front one works. Wiring it is in Quad Tasks, section 7 |

---

## Towards robotics — noted, no plan

**Decided on 31 October 2026: the quad gets finished first.** No ROS 2 and no robot sensors
inside the current cycles. The order:

1. **Finish the quad**: the model validated against the vehicle (C02–C06).
2. **Own Vehicle Control Unit**: the unit that commands the inverter.
3. **Programming in C** on that unit: the model's control loop, running on the microcontroller.
   It is what turns "I know Simulink" into "I can do firmware".
4. **Telemetry over ROS 2** (decided 2026-11-04, [DEC-007](../08_decisions/DEC-007-skill-gates-and-ros2-telemetry.md)):
   a Raspberry Pi above the VCU reads its CAN, records it and sends it to the PC over radio.
   This is how robotics enters the quad. The radio is chosen from `REQ-TEL`, not before.
5. **Not on the quad:** autonomy (Pol, 2026-11-04: no need for it). An **autonomous drone**
   (ArduPilot or PX4, Raspberry Pi, camera or lidar) is a separate project, decided after the
   quad is done.

**Parked, with an entry condition:**

| Idea | Entry condition |
|---|---|
| **Learned controller (reinforcement learning) trained on the twin** | (1) Pol writes the requirement it would meet, with a number; (2) model validated (C06); (3) VCU commanding torque with a safety envelope. Then: compare it on the quad against the classic PI controller |
| **Machine learning on the CAN logs** (motor parameter estimation, fault detection) | Enough logs with load, and a question the physics model cannot answer |

The underlying reason does not change: robotics startups ask for C/C++, Linux, ROS 2 and
communications, and today the repository has no code that shows it. The skill gates in the
[roadmap](roadmap.md) make sure each cycle adds some.

---

## Git hygiene: what to automate and what not

> **Updated 2026-10-30: it is automated now, with review.** Pol decided he does not want to do
> the git work by hand: an agent does it and he is the reviewer. The «Sincronizar con GitHub»
> task (every Sunday, on the PC; every night until 31 Oct 2026) groups the changes by topic into
> commits with their why, opens a Pull Request and Pol merges it. That answers the objection
> below: the agent applies the judgement and Pol checks it in the PR, instead of a blind
> automatic commit. Procedure in `../prompts/sincronizar.md`. What follows stays as history.

Opened on 2026-09-09, after a rescue operation: 46 new files and 24 modified ones had gone up
to two weeks without a commit. All of C00's technical work — motor characterisation, inertia,
EXP-001, decks — lived only on the disk.

**Plumbing, done or immediate.** It needs no judgement, so it is automated without debate:
`push.autoSetupRemote` (kills the `-u` on the first push), `fetch.prune` (cleans references to
dead remote branches), and on GitHub disable squash merge and enable deleting the branch on merge.

The squash point is not cosmetic: PR #4 squashed 7 topical commits into one titled like the
first of them, so `a3e6f9b` now says "version the VESC config" and also contains the motor, the
inertia, EXP-001 and the presentations. The content is intact; the traceability is not.
Disabling the option in the repo makes the mistake unrepeatable, which beats remembering not to
make it.

**Judgement, NOT automated.** Grouping changes by topic and writing why the VESC's detection is
no reference for λm are engineering decisions. An automatic commit would produce exactly the
useless history this project tries to avoid.

**The middle ground, postponed.** The real failure was forgetting, not not knowing. An
end-of-session hook that *warns* (never commits) is the right tool. But the entry rule for own
skills applies: three repetitions by hand before encoding anything. One so far.

Meanwhile, the discipline is manual: when closing a session, `add` by topic → `commit` →
`push`, even if the work is half done. A WIP with an honest message is worth more than 46 files
in limbo.

**Continuous integration, postponed (2 Nov 2026).** Having GitHub compile the firmware and run
checks on every PR was considered. Today it adds little: one author, small sketches and no test
that runs on the PC. It goes in with the vehicle control unit, when there is logic with a test
on the PC (step 6 of the `software-con-ia` skill): then it does catch failures and does count on
the CV.

---

## Personal brand, content and company

Recognised as a real long-term goal. **Zero research action now.**

- **LinkedIn:** active, but as a *by-product*. Each review with mentors produces material;
  publishing is copying and translating, not a separate project. No agent.
- **Portfolio for interviews — decided on 2026-10-30.** Three pieces, in this order of
  importance: (1) **this public repository** (`polcp03/PROJECT_ePWT`), which updates by itself;
  (2) **a presentation** that tells the project and what was done, taken from the review decks;
  (3) **a 30-second video** to show people: the quad, the digital twin and a measured number,
  without explaining theory. For the video, **record from now on** short clips of each
  milestone (the bench, a measurement on the oscilloscope, the model running): material not
  recorded when it happens cannot be recorded later. It gets edited when an interview is near
  or when the quad moves with its own control.
- **YouTube / newsletter / teaching:** later. Dual function recognised — build a brand and
  force real understanding. The excuse for video is learning to explain and losing shyness;
  the presentations cover that goal for now.
- **Tech company (robotics or other):** a horizon of years. First: knowledge, experience,
  understanding sectors and spotting real problems. Don't force an idea.
- **AI-first organisation as a lab:** learn to work with AI as a shared knowledge layer before
  having a team. This repo is already the minimal version.

## Bench: next retrospective

Ideas to change the learning app or the method. They wait for the cycle close (method frozen between reviews, 3-Nov-2026).

- _(empty)_
