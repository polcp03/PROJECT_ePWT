# ePWT Bench

The one place where I study the quad: https://claude.ai/artifact/JwjbfzLRg98SpwrJfADjBX

- **Today**: the lesson of the day, on a 3D model of my motor that follows the text.
- Every answer is graded by Claude on the spot: what is right, what is wrong, the fundamental
  explained, and a second try in my own words before the reference solution opens.
- **Review**: every mistake comes back the next day, until I get it right on two different days.

## How it is built

| File | What |
|---|---|
| `lessons/*.md` | One lesson per file. Format in `.claude/skills/leccion/SKILL.md` |
| `build.py` | Turns the lessons into `app.html`. Run from `PROJECT_ePWT/`: `./.venv/Scripts/python.exe 01_plan/bench/build.py` |
| `engine.js` | Tabs, the 3-turn grading, the spaced review, storage |
| `motor3d.js` | The 3D motor (three.js r128): interior-magnet PMSM, p = 3 |
| `labs.js` | 2D labs: Clarke, SVPWM hexagon |
| `style.css`, `template.html` | Look and page shell |

`app.html` is generated: never edit it by hand. Republish it to the same URL without changing
its capabilities (`db`, `sample`), or the stored answers are lost.

Storage, in the artifact database: `attempts` (one per question), `errors` (the live list of
mistakes; `02_knowledge/mistakes.md` is its weekly mirror) and `doubts`.

Slot count (18) and magnet layout in the 3D model are illustrative: neither is measured yet
(`03_hardware/baseline.md`).
