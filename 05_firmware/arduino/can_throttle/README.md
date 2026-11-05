# can_throttle — bring-up: throttle → ESP32 → CAN → VESC

Throwaway bring-up test, not the VCU. The ESP32 reads the throttle grip and commands the
VESC's motor current over CAN (`CAN_PACKET_SET_CURRENT`, VESC id 15, every 10 ms), capped
at 10 A. Contract at the top of [`can_throttle.ino`](can_throttle.ino).

**Setup (2026-11-05):** wheels in the air. Grip powered from the ESP32's 3V3, signal straight
to GPIO 35 (no divider, no RC). ESP32 on the USB of a laptop **running on battery**, VESC
USB unplugged (EXP-001 rule 1). VESC Tool: App to Use = No App, CAN timeout 100 ms, timeout
brake current 0 A, motor current max 120 A (Pol's setting), battery current max 39 A. The
ESP32 code caps the request at 10 A.

## Results

| Test | Result | Verdict |
|---|---|---|
| Frames | 33 080 sent in 5.5 min = 100.2 /s, 0 send failures, TX error counter 0 | Pass |
| Command tracking | Above ~2500 erpm the VESC's motor current matches the request within ~0.5 A (7.0 asked → 7.1 A) | Pass |
| Low speed | 0–2500 erpm: 4–8 A asked and delivered with the wheel stopped; delivered current swings 5–18 A, sometimes negative, for a steady ask | **Open**: VESC start-up / Hall configuration, not this code. Same symptom as duty 10–30 % not spinning. Evidence and plan in [EXP-003](../../../07_experiments/EXP-003-low-speed-control.md) |
| CAN cable pulled while spinning | Motor stops pushing; full throttle afterwards does nothing | Pass (by eye) |
| Timeout, measured (`silence`) | Current reported 0 A after **105, 117, 119, 121, 114 ms** (5 runs, 1 900–15 800 erpm) | Pass within the measurement resolution: the VESC reports its status every ~21 ms, so a 100 ms timeout shows as 100–121 ms |
| Re-arm after a cut | Grip held at 76 % after the cut: stays at 0 A until released for 0.5 s | Pass |

## Bugs found by the first unplug test, fixed

1. Stale VESC data was printed as valid ("VESC ok 8.6 A 15881 erpm" for a minute with the
   cable out). Now: older than 100 ms → `VESC --`.
2. After a CAN loss the program stayed ARMED, and the MCP2515 kept the last 3 queued frames
   (~7.9 A) to send on reconnection. Now: loss → `WAIT_REST`, chip reset to drop the queue.

## Learned

- **The 10 A cap limits the command, not the current:** at low speed the VESC delivered
  18.3 A for a 6.7 A request. The VESC's own limit is the barrier that really holds.
- In current mode with no load, a steady request is a steady acceleration up to the voltage
  limit (15 900 erpm ≈ 5300 rpm): expected, not a fault.
- Bench noise with the motor spinning at 5 A (inverter switching, no RC): spikes up to
  +80 mV on the averaged reading (4.5 % of throttle). Harmless with a 10 A cap; the RC goes
  on the final board.
