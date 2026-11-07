# Quad Tasks

Tick it here: https://claude.ai/artifact/4hkig3fuuywMzBDRh6fefu

- **Tasks** get a tick: to do → done.
- **Purchases** get a pill: To buy → Ordered → Arrived.
- **Add a task or a note** at the bottom: typed on the phone, filed into the list on Sunday.

| File | What |
|---|---|
| `tasks.md` | The source: every task with a permanent `{#id}`. Format in the comment at its top |
| `build.py` | Turns `tasks.md` into `tasks.html`. Run from `PROJECT_ePWT/`: `./.venv/Scripts/python.exe 01_plan/tasks/build.py` |
| `template.html` | Look and behaviour of the page |
| `tasks.html` | Generated: never edit it by hand |

Ticks live in the artifact database: `status` (one document per task id, `s` = `todo`,
`ordered` or `done`) and `inbox`. A tick in the database wins over the box in `tasks.md`. Every
Sunday the sync copies them into `tasks.md` (`prompts/sincronizar.md`, step 4c at the repo root).
Republish to the same URL **without changing its capabilities** (`db`), or the ticks are lost.

Changing a task's text keeps its tick. Changing its `{#id}` loses it.
