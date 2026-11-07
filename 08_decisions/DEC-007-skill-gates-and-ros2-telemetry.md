# DEC-007: Skill gates per cycle, and robotics enters the quad through ROS 2 telemetry

**Date:** 2026-11-04. Decided by Pol, after a review with Claude of which engineering skills
robotics pays for as AI writes more of the code.

## Decision

1. **Every cycle has a skill gate** (reading C, Python on data, real-time C, ROS 2) that
   blocks its close: no gate, no review, no next cycle. The table lives in
   [`01_plan/roadmap.md`](../01_plan/roadmap.md). A gate may slip one cycle, once, with a
   reason written in the cycle log.
2. **ROS 2 enters as telemetry, after VCU v0:** a Raspberry Pi above the VCU reads its CAN,
   records it and streams it to the PC over a radio link. The VCU stays a microcontroller in
   real-time C; ROS 2 never runs inside it.
3. **The quad is not made autonomous.** An autonomous drone is a separate project, decided
   after the quad. Reinforcement learning on the twin is parked with an entry condition
   ([backlog](../01_plan/backlog.md)).

## Alternatives

- **Software skills as optional backlog items.** Rejected: Pol's own history is that what goes
  to "later" does not get done. Software is his main gap for the jobs he wants.
- **ROS 2 inside the VCU (micro-ROS on the ESP32).** Rejected: it mixes a hard-real-time
  torque command with a middleware layer. Robots split it the same way: real-time controller
  below, Linux and ROS 2 above.
- **Autonomous quad (lidar, camera, steering actuator).** Rejected: no need behind it, and it
  needs new hardware. Autonomy without a need is not systems engineering.
- **Reinforcement learning on the twin now.** Rejected for now: no requirement, and the model
  is not validated, so it would learn the model's errors.

## Reasoning

- Writing code is getting cheaper; specifying, reading and verifying it is not. Pol does not
  need to type C, he needs to find where it fails (skill `software-con-ia`).
- Israeli robotics and drone postings ask for C/C++, Python, Linux and ROS 2, plus system
  requirements, integration and validation. The gates add one of these per cycle without
  leaving the quad.
- Telemetry is a real need (data from the moving vehicle), so ROS 2 gets used for something.

## Assumptions

- Each gate fits in 1–3 sessions inside the cycle's 14 h. If two gates in a row slip, the
  gates are too big, not Pol.
- A Raspberry Pi with ROS 2 can read the CAN bus (a CAN interface board will be needed).

## Consequences

- Opens: a portfolio with code Pol can explain line by line, and a robot-style architecture
  (real-time controller + ROS 2) to defend in interviews.
- Closes: autonomy on the quad, and ROS 2 before the VCU exists.
- New requirement set when telemetry starts: `REQ-TEL` (rate, latency, frame loss, range),
  which chooses the radio.
