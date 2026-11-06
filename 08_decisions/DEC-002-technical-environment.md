# DEC-002: Technical environment

**Date:** 2026-09-01. Everything checked by running it, not assumed.

| Tool | Version | How it is used |
|---|---|---|
| MATLAB / Simulink | R2023b | MCP connected + `matlab -batch` (~25 s) |
| Python | 3.14.6 in `.venv/` | numpy, pandas, matplotlib, scipy, control |
| arduino-cli | 1.5.1 + esp32 3.3.11 | Compiles cleanly |
| git / gh | 2.54 / 2.97 | PRs from the terminal |

**Tested end to end:** CSV → pandas → scipy filter → inspectable PNG plot.

## Toolboxes: all 40 are there

Including **Motor Control Blockset**, Simscape Electrical, Vehicle Dynamics Blockset,
Powertrain Blockset, **MPC Toolbox**, Embedded Coder, System Identification.

> [!danger] The trap
> Motor Control Blockset ships **ready-made FOC for PMSM**. Dragging that block in gives a quad
> that works and an engineer who has learned nothing.
>
> **Rule:** first I build it from the equations, then I compare it with the reference. The
> difference between my version and theirs is the learning.

Good consequence: MPC stops being out of reach. It still needs the validated model from C06, so
the sequence doesn't change — but it becomes a real goal at ~6 months.

## MATLAB MCP

Official MathWorks binary (`github.com/matlab/matlab-mcp-server`) v0.12.0, in `_tools/`. It
doesn't need Python — important, because MATLAB Engine for Python in R2023b only supports
Python 3.9/3.10/3.11 and here there is 3.14.

**It needs MATLAB open**: it attaches to an existing session, it doesn't start one.
