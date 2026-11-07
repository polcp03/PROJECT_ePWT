# Session: Simulink / digital twin

Extra context for working in `04_model/`. It adds to the root `CLAUDE.md`.

## Rule no. 1 — Parameters in `.m`, structure in `.slx`

Git **cannot diff a `.slx`**: it is a binary. If you put the numbers inside the blocks, you
lose the history of why the model changed.

Therefore:
- Every parameter lives in `params/*.m` as plain text, in **SI units**, with a comment saying
  whether the value is **MEASURED** or **ASSUMED**, and where it comes from.
- The `.slx` blocks reference variables, never literal numbers.
- A calibration change is then a readable diff in Git.

## Rule no. 2 — An assumed parameter is declared

If a value from `03_hardware/baseline.md` is missing, don't estimate it silently. Mark it
`ASSUMED` in the `.m` and log it as an open question. A model full of hidden assumptions
produces convincing, false results.

## Rule no. 3 — The model is worth nothing until it correlates

Before the model is used to design control, it has to reproduce a real measured test
(`06_data/`). Until then it is a hypothesis, not a tool.

## Rule no. 3b — Predictions are frozen before measuring

Since C01. A prediction is written with its band in `results/C0X_predictions.md` **before**
the test that checks it, and is not touched afterwards. If an input changes before the test
(e.g. a mass that becomes MEASURED), a new version is published, saying what changed and why
it is not refitting. Fitting parameters with one test and "validating" with the same test
validates nothing: you validate with another one.

## How to teach me

Before a block, the physics. Before the model, the equation. I want to know which assumption
each simplification brings in and when it stops holding. If you propose a model structure,
also tell me what it does **not** capture.

## Build order

1. Longitudinal vehicle dynamics (mass, wheel, drivetrain, rolling, aero).
2. Electric machine in dq (PMSM).
3. Inverter + current loop.
4. Full FOC (Clarke, Park, Id/Iq control).
5. Vehicle strategies (traction, launch).

Don't skip levels. Each level is validated before the next.

## Folder structure

```
params/     .m scripts with parameters (text, versionable)
models/     .slx files
scripts/    test scripts, model-vs-data comparison, plots
results/    figures and correlation outputs
```

## What is here now (2026-10-09)

| File | What it is |
|---|---|
| `scripts/build_longitudinal_L1.m` | Builds `models/longitudinal_L1.slx` from scratch. **The script is the reviewable source**; the `.slx` is a build artefact |
| `scripts/run_predictions_L1.m` | C01 predictions + sensitivity sweep + CSVs for the deck |
| `scripts/build_longitudinal_L2.m` | L2 = L1 regrouped in 4 subsystems + 2 empty gaps (load transfer, launch control) |
| `scripts/run_regression_L1_L2.m` | L2 has to give the same as L1 while the gaps are empty |
| `results/C01_predictions.md` | Frozen predictions, v2 |

Building a `.slx` from a script meets rule no. 1 better than editing it by hand: every block
and every connection stays in text and shows up in the diff.

## Rule no. 4 — The agent reads and simulates; I place the blocks

The Simulink Agentic Toolkit exposes **write** tools on the `.slx` (create and connect blocks,
change parameters). They are not used unless I explicitly ask in that same conversation.

Reason: the `.slx` is binary, so a change made by the agent **cannot be reviewed in the
diff**. A model I didn't build is a model I can't defend in front of a mentor, and that breaks
Goal 0.

Split:
- **Agent**: read the model structure, query parameters, run simulations, compare against
  `06_data/`, write and run the `.m` files in `params/` and `scripts/`, point out what doesn't
  add up and why.
- **Me**: place and connect the blocks.

> [!warning] Recorded exception — C01, 2026-10-08
> L1 and the structure of L2 were built by the agent, on explicit request, with the review the
> next day. Result: a model I couldn't explain, and a night of questions to win it back. **I
> fill the L2 gaps myself.**
