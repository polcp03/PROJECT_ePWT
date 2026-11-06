# DEC-006: A light V-cycle, with requirements and a verification matrix

**Date:** 2026-11-03. Decided by Pol, after reviewing the project with Claude as a systems
engineer. Replaces the rule "no formal IDs, status fields or traceability matrices" in
`CLAUDE.md`, written when the project started (August 2026).

## Decision

The quad is developed with a **light V-cycle**, on two levels:

1. **The whole quad:** needs → vehicle requirements (`REQ-VEH`) → field validation.
2. **Each system I design:** first the vehicle control unit (VCU, `REQ-VCU`), and also the
   model (`REQ-MOD`) and the logger (`REQ-LOG`): requirements → architecture and interfaces →
   modules with a contract → tests → integration → verification.

It lives in `00_system/` (needs, requirements, architecture, verification), created with the
first draft. **I write it; Claude reviews it** as a systems and validation engineer (skill
`ingenieria-sistemas`). It is updated at every cycle close.

## Alternatives

- **Keep things as they were** (decisions and experiments only). Rejected: the left half of
  the V is exactly what systems engineering work asks for, and it does not exist in the repo.
- **Formal V with functional safety (ISO 26262).** Rejected: paperwork without engineering for
  a one-person project. The technical part stays: a safe state and a reaction time for every
  failure.
- **Rewrite the whole quad backwards.** Rejected: requirements are written only for what is
  going to be built or verified.

## Reasoning

- **What I want to learn is systems engineering:** writing requirements, integration plans,
  test procedures, and validation in the lab and in the field.
- **The right half already worked:** predictions frozen before measuring, MEASURED / ASSUMED
  tags, EXP-002. What was missing is where the criteria come from.
- **What failed without it:** in DEC-005 the VCU requirements were written as tasks, with no
  number and no test; in EXP-002 three things changed at once and nobody knows which one
  fixed it.
- **The VCU is the only part of the quad I design**, and the first one that commands torque:
  that is where a full V makes technical sense, not just teaching sense.

## Assumptions

- A light V (four files, no status fields, no tools) does not turn into bureaucracy. If
  keeping it costs more than ten minutes per cycle, it gets trimmed.

## Consequences

- Decisions (`08_decisions/`) and experiments (`07_experiments/`) stay as they are; tests that
  close a requirement link to it.
- Every cycle review carries one slide: what is verified and what is not.
- First step: my needs for the quad, as user sentences.
