# DEC-004: Non-isolated CAN, with the logger floating

**Date:** 2026-10-31. Pol decides. It replaces what `shopping-list.md` asked for (ISO1050).

## Decision

The logger uses the **MCP2515 + TJA1050** that was already there, without galvanic isolation.
Safety comes from the architecture: the logger runs from **its own 12 V battery** with a DC-DC
to 5 V, and joins the VESC only through CAN-H, CAN-L and the CAN ground. No mains-connected
equipment touches that system: the laptop, if connected over USB, is **always without its
charger**.

The MCP2515's SO output (5 V) goes through a 1 kΩ / 2 kΩ divider to the ESP32 (3.3 V).

## Alternatives

- **ISO1050 (isolated).** The right choice if there were mains-referenced equipment in the
  loop. Rejected: Pol doesn't want to buy it, and with the logger floating there is no loop to
  break.
- **SN65HVD230.** Native 3.3 V, no divider. Just as non-isolated, and it had to be bought.
- **MCP2515 at 3.3 V.** The TJA1050 needs 5 V: it doesn't work.

## Reasoning

September's ESP32 died from a **ground loop**: the PC ground (mains) joined to the ground of a
VESC switching 54 V ([EXP-001](../07_experiments/EXP-001-ground-loop-vesc-pc.md)). Isolating is
one way to break that loop; not having mains in the loop is another, and it costs nothing.

## Assumptions

- Nobody plugs a charger into the laptop while it is joined to the vehicle.
- The VESC's common-mode noise under load fits within the TJA1050's common-mode range. With 0
  bus errors in log_017 (49 A peak) it holds; under real load, to be seen.

## Consequences

- It works today, without spending anything ([EXP-002](../07_experiments/EXP-002-spi-noise-can-logger.md)).
- The divider and the breadboard make the SPI link sensitive to noise: short wires, away from
  the VESC. Fitting it on the vehicle needs a **soldered perfboard**, not a breadboard.
- If one day the ESP32 commands torque to the VESC (vehicle control unit), a failure here stops
  being lost data: this decision is reviewed before that.
