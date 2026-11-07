# C01 deck — Pol's feedback (night of 8 to 9 Oct)

To apply **after** the round of questions about the model. Not before.

## Form
- Misaligned text, even in the title.
- More visual: new images, **don't reuse** the C00 ones. It still looks cheap.

## What is surplus
- VESC poles (14 → 6): it has no place in this review.
- The measured mass as an "achievement": not needed. Get straight to the point.
- Slide 10 ("what I don't understand"): he doesn't see the point of it in its current form.
- It stays: why there is no coast-down (tyres + ESP32).

## What is missing
- Force equation: good, but **with data**: which μ, why that μ, total mass, each value with its source.
- Motor and battery: **where each number comes from** (measured, from the VESC, configured, assumed?). R_int: who measured it?
- Explain the model better: why a single integrator, what the MATLAB block does, what the VESC ramp does.
- Predictions: say they are simulations, why the coast-down starts at 25 km/h, how the bands are calculated.
- Tornado: "change from nominal" is not understood.
- What it doesn't capture: discuss what is in and what is not (slip, load transfer, tyre pressure, inverter losses, chain). Drivetrain losses: never discussed.

## Direction
- C01 = explain the longitudinal model well, the basics.
- C02 = motor + inverter seriously (Clarke, Park, current control). That is what interests him.
