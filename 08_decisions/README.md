# Decisions

One file per decision with real impact: `DEC-00N-name.md`.
Only architecture and trade-offs, not minor details.

- **Decision:** what was decided
- **Alternatives:** what else there was, and why it was rejected
- **Reasoning:** why this one
- **Assumptions:** what I take for granted (and could be false)
- **Consequences:** what it closes and what it opens for me

| | Decision |
|---|---|
| DEC-001 | Organisation tool: Obsidian on the repo (replaced by DEC-003) |
| DEC-002 | Technical environment: MATLAB R2023b, Python venv, arduino-cli, git/gh |
| DEC-003 | Obsidian out; the repo is read in VS Code and GitHub |
| DEC-004 | Non-isolated CAN, with the logger floating |
| DEC-005 | VCU architecture and sensors: throttle and brake to the VCU, BMS untouched |
| DEC-006 | Light V cycle: requirements with numbers, verification matrix, no paperwork |
| DEC-007 | Software gates per cycle; ROS 2 comes in as telemetry on a Raspberry Pi; the quad is not made autonomous |
| DEC-008 | Grounds and EMC: floating in DC, bonded to the chassis by a capacitor at the inverter; IMU on the VCU board |
