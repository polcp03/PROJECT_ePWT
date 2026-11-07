# Software — what I can explain

How the work is done: skill `software-con-ia`. I set the contract and the test; the AI writes
the code. Here go my answers, already corrected.

## How do I know an embedded program is right without reading the code? (2 Nov 2026)

**What I said:** I read two CAN nodes, I run a test (I accelerate, the motor moves), I see that
what I do correlates with what I read and there are no CAN errors. If the result is good, there
is no need to read how it is made.

**Correction.** The instinct is the right one, and it is a calibrator's: check against physical
reality. But it stops at step 3 of 6 (ladder in the `software-con-ia` skill):

- "Plausible" is not a criterion. It needs a number: **0 frames lost** and the frame rate equal
  to the one configured in the VESC.
- "No errors" only counts if something counts them. My `can_logger` does: `queue drops`,
  `hw overflows`, `SPI err` and the CAN controller's error counters (`RX err`, `TX err`). The
  test is that they stay at 0. **The contract has to demand those counters**: without them, a
  failure is invisible.
- A two-minute test doesn't see slow failures: a 32-bit microsecond timer wraps to 0 after
  **71.6 minutes**. It has to hold for 30 minutes or more at full load.
- And the failures have to be provoked: unplug the cable, switch a node off, fill the SD. What
  does it do?

**Said well, in one sentence:** without reading the code I trust it if it meets a criterion with
a number, keeps it through a long test and has counters that prove nothing has failed.
