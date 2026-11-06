# How to organise Claude Code sessions

A learning note about the harness. It answers: "how many chats do I open, and what for?"

## 1. The real problem: context is a finite resource

An LLM has no memory between sessions. Everything it knows at a given moment is in its
**context window**: the instructions, the files read and the whole conversation.

That window is large but not infinite, and it has a counter-intuitive property:
**more context is not better context.** A three-hour conversation that has touched Simulink,
battery, Git and planning holds a lot of information — and a lot of noise too. The signal
relevant to the current question gets diluted.

This already happened to me: I poured in ~8,000 words of strategic context at once and the
answer got worse, not better. **That is exactly the failure the session architecture avoids.**

## 2. The rule

> **One session = one task with a checkable goal.**

Not "one session a day" nor "one session per everlasting topic". When the goal is met, the
session closes. If I have been in the same session for three hours and changed topic twice,
the context is already dirty.

## 3. Contexts, not permanent sessions

**Important clarification** (this was badly explained before and contradicted the rule
above): the four "types" below **are not four chats kept open permanently**. They are
**contexts**: categories of work, each with its own rules.

Each concrete task opens **a new session**, and that session *belongs* to a context. In one
cycle I can open 8 different model sessions: one per task. They all share the rules in
`04_model/CLAUDE.md`, and none inherits the previous one's conversation — what they inherit
is **what was written down in the repo**.

## 3b. The four contexts of this project

### Direction session (repository root)
Plan the cycle, review the roadmap, close decisions, prepare the review.
Opened from the root. Loads the main `CLAUDE.md`.
Frequency: when opening and closing each cycle. Short.

### Model session (`cd 04_model`)
Simulink, vehicle physics, control, parameters.
Loads the root `CLAUDE.md` **+** `04_model/CLAUDE.md`.
This is where most of the work will live over the coming months.

### Firmware session (`cd 05_firmware`)
ESP32, CAN, acquisition, embedded software architecture.
Loads the root `CLAUDE.md` **+** `05_firmware/CLAUDE.md`.

### Data session (`cd 06_data`)
Process logs, plots, compare model against measurement.

## 4. How it works technically (and how I do it, working by voice)

Claude Code reads the `CLAUDE.md` of the directory it is launched from **and those of the
parent directories**. There are two ways to work:

**Way A — automatic.** `cd 04_model && claude`. It loads the general rules **plus** the
Simulink ones, and nothing about firmware or strategy. It is the cleanest.

**Way B — by voice, which is how I work.** I launch from the root and say *"let's work on the
model"*. Then Claude has to **read `04_model/CLAUDE.md` itself** before answering. It is
written as an operating rule in the root `CLAUDE.md`, so I don't need to remind it every time.

Way B adds a bit more context than A, but the difference is small and the convenience is
large. **Way A is only worth it for long sessions in one area.**

That is *context engineering*: the task gets what it needs and little more. No MCP, no
subagents, no infrastructure. Just folders and files.

## 5. How to start and close a session

**When starting**, one sentence that sets the scene: *"We are in C01. Today I want to measure
the phase resistance. Read `03_hardware/baseline.md` before answering."*

It is better than dumping context: you tell it **where to look** instead of pasting the
content. The repository is the memory; the session only needs the pointer.

**When closing**, the cheapest and most valuable habit of the whole system:

> Write down the state before closing. What I did, what I learned, what is left.

It goes into the cycle file (`01_plan/cycles/C0X.md`). Without it, every new session starts
blind and the context has to be rebuilt by hand. **If it matters, it gets written.**

## 6. What NOT to do

- **One endless session for the whole project.** It is the mistake I already made.
- **Paste whole documents.** Keep them in the repo and say where they are.
- **Change topic without closing.** If you go from Simulink to planning, new session.
- **Expect it to remember yesterday's session.** It doesn't. What it remembers is what is
  written in the repository.

## 7. Agents and skills: when, not whether

An agent or a skill **encodes a process you already do well**. I haven't done any of these
processes yet, so there is nothing to encode.

Entry criterion, written in `01_plan/backlog.md`: when I have done the same task by hand
**three times** and repeating it annoys me, that is the signal. Not before.
