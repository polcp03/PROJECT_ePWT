# Session: firmware / embedded

Extra context for working in `05_firmware/`. It adds to the root `CLAUDE.md`.

## Rule no. 1 — Control is not invented here

Control logic is designed and validated in `04_model/`. This directory **implements** it. If a
magic constant shows up that does not come from the model, it is a process bug, not an
optimisation.

## Rule no. 2 — Safety limits are code, not configuration

Current, temperature and BMS-state limits are checked in the firmware, not only in VESC Tool.
See the safety rules in the root `CLAUDE.md`.

## Rule no. 3 — Search before writing

Reference implementations exist (VESC Express for the ESP32, `syssi/esphome-jk-bms` for the
BMS protocol). Review them before reverse-engineering from scratch. First principles are kept
for the domain I want to master, not for protocols.

## How to teach me

I want to learn **software architecture**, not just that it compiles: separation of
responsibilities, modules, interfaces, dependencies. When you propose code, first explain how
the responsibilities are split and why.

No giant `.ino`. Modules with one responsibility each.

**How I learn software: skill `software-con-ia`.** I write each module's contract (in the
`.h` header) and choose the test with its number; the AI writes the code; with every change I
learn one C pitfall in my own code.

## How it is compiled and seen (the Arduino IDE doesn't work)

Skill `esp32`: the code open in the file pane and the serial monitor in a visible Terminal tab,
with `esp32.py` (compile, flash, monitor, send). Never flash blind in the background: Pol has
to see it.

## Folder structure

```
arduino/      sketches and quick experiments
vcu-design/   VCU board: pinout and perfboard layout
```

`src/` (modules) is created **when the VCU starts**, not before. An empty folder is noise: it
promises something that doesn't exist.

**Only my own code goes here.** The VESC material is split on purpose: my unit's configuration
in `03_hardware/vesc/`, its logs in `06_data/`, and the third-party firmware and tool in
`_tools/` (outside Git). See `03_hardware/vesc/README.md`.
