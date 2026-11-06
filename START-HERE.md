# ePWT — start here

A learning bench for electric powertrains. **The quad is the physical plant, Simulink is the
digital twin, and the two-week cycle with mentors is the engine of progress.**
Goal 0: become a better engineer, from first principles, with a portfolio that proves it.

## Today

**Study here: [ePWT Bench](https://claude.ai/artifact/JwjbfzLRg98SpwrJfADjBX)**. Open *Today*: it shows the first lesson you have not finished, in calendar order. Do the *Review* tab first. Claude grades every answer on the page; your mistakes come back by themselves.

**Tick off here: [Quad Tasks](https://claude.ai/artifact/4hkig3fuuywMzBDRh6fefu)**. Purchases (to buy → ordered → arrived), measurements, wiring, tests. A tick is saved by itself: no need to tell a chat.

**C03 — dq, limits and the current loop · review Fri 13 Nov (with C02).** Order, gate and open points in [C03](01_plan/cycles/C03.md). **Gate:** REQ-MOD-001 drafted in C03-LM (10 Nov).

## Where everything is

| Folder | What is there | Do I open it? |
|---|---|---|
| `01_plan/` | `tasks/` (Quad Tasks), `cycles/` (active and `closed/`), `bench/` (the learning app), roadmap, backlog | **Daily** |
| `02_knowledge/` | What I have learned, in my words, and my mistakes | Before each exam |
| `03_hardware/` | The quad: what was measured. Source of truth | When I need a number |
| `04_model/` | Simulink: digital twin | In model tasks |
| `05_firmware/` | ESP32 / Arduino code (`arduino/`) and the VCU board (`vcu-design/`). **CAN logger working** (`arduino/can_logger/`) | When recording |
| `06_data/` | Tests by campaign | When there is data |
| `07_experiments/` · `08_decisions/` | Hypothesis → measurement; decisions with their why | When closing something |
| `09_reviews/` | Mentor review decks and their images | Before a review |
| `../BOOKS/` | Library, at the repository root (outside Git). Index in [sources](02_knowledge/sources.md) | Claude filters it |

## My three rules

1. **Only the active cycle exists.** Every new idea goes to the [backlog](01_plan/backlog.md).
2. **If a day falls through, it falls through.** It is not recovered by piling up.
3. **If it matters, it is written down and committed.** Close each session with a line in the
   cycle log and a commit.

## Safety — not negotiable

13S5P Li-ion battery. Peaks of **~40 A** against a design assumption of 25 A, and the BMS cuts
at 40 A continuous. No high-current test without: limit set in the VESC · pack temperature
checked at the end · **never charge unattended**.

## If you are a new session

1. `CLAUDE.md` — how to work with Pol (senior engineer mode, brain first).
2. This file — what is on today.
3. The active cycle in `01_plan/cycles/`, and the ticks in Quad Tasks.
4. If the work falls in `04_model/` or `05_firmware/`, read its `CLAUDE.md` before answering.
5. Lessons → skill `leccion`. Grading answers → skill `corregir`. Deck → skill `review-deck`.
