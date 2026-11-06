# 2026-11-06 — Axle loads and CG height: results

Raw readings in [`readings.md`](readings.md). Wheelbase L = 0.72 m, track 0.46 m front / 0.44 m rear.

## 1. Weight split (level)

| | Front | Rear | Rear fraction |
|---|---|---|---|
| Empty | 19.9 kg | 19.5 kg | **0.50** |
| With rider | 40.7 kg | 80.0 kg | **0.66** |

- The scales over-read at high load: 120.7 kg against 113.9 kg known. **Fractions are trusted,
  absolute kg are not.** Vehicle mass stays at the 38 kg of the 2026-10-08 single-scale reading.
- CG along the wheelbase: empty **36 cm** ahead of the rear axle; with rider **24 cm**.
  The rider sits ≈ 18 cm ahead of the rear axle.
- Front axle left/right: 11.5 / 8.4 kg empty, but the rear goes the other way (9.5 / 10.0). Not a
  lateral CG offset: most likely a **diagonal load** from the larger front-left tyre on a rigid
  four-wheel chassis (FL + RR carry more), or a scale bias. Swapping the scales would separate them.

## 2. CG height, empty (tilt test)

Moments about the contact of the lifted axle, with h′ the CG height above the axle-centre line:

```
N_lower = W · [ a_lower/L + (h′/L) · tanθ ]      sinθ = Δh / L
```

`a_lower` is the horizontal distance from the CG to the raised axle on level ground, i.e. the
lower axle's share of the wheelbase. N_lower rises linearly with tanθ; the slope is W·h′/L.
Δh = block − 3 cm scale = 6.5 and 13 cm.

| Series | Slope (kg per unit tanθ) | h′ |
|---|---|---|
| Front lifted, rear on scales | 11.0 | 0.20 m |
| Rear lifted, front on scales | 4.8 | 0.09 m |
| **Both, joint fit** | 7.9 | **0.15 m** |

- **h_cg empty = h′ + loaded wheel radius (≈ 0.16 m, ASSUMED) ≈ 0.31 m, ± 0.08 m.**
- The two series disagree by a factor of two: the signal is only 1–2.5 kg against ±0.5 kg per
  scale. The number is good to about ±25 %.
- 3 cm scale correction: W·h′·tan(3/72)/L ≈ 0.3 kg. Below the scale noise, so ignored.

## 3. CG height with rider (estimated, not measured)

- The rider's CG is **not** at the seat (0.45 m). Seated, knees at 90°: trunk, head and arms
  (~2/3 of body mass) sit well above the seat, legs below it → body CG ≈ 0.15–0.20 m above the
  seat → **≈ 0.62 m**.
- Combined: (38 × 0.31 + 74.5 × 0.62) / 112.5 ≈ **0.51 m** (range 0.45–0.55 m).
  Putting the rider at the seat would give 0.40 m: 20 % too low.
- h_cg / L ≈ 0.7. A tall vehicle for its wheelbase: the rider dominates.

## 4. What it means (with rider, h = 0.51 m)

| Effect | Formula | Number |
|---|---|---|
| Load transfer under acceleration | ΔN = m·a·h/L | **≈ 8 kg to the rear per 0.1 g** |
| Front wheels lift (wheelie) | a/g = b/h, b = CG to rear axle | 0.24 / 0.51 ≈ **0.47 g** |
| Rear wheelspin limit (rear drive) | a/g = μ·(l_f/L) / (1 − μ·h/L) | μ = 0.4 → 0.37 g; μ = 0.6 → 0.70 g |
| Static rollover (rigid, no compliance) | a_y/g = t/(2h) | 0.44 / 1.02 ≈ **0.43 g** |

- **Dirt (μ ≈ 0.4): the rears spin before the front lifts.** On high grip the front would lift
  first, if the drivetrain can push ≈ 520 N at the wheels (not checked).
- **Rollover ≈ 0.43 g** is an upper bound: tyre and frame compliance lower it. On dirt the quad
  slides before it tips (μ < 0.43); on asphalt it can tip first. That is why you lean in.
- Traction control on the VCU needs h and the split: **both now have numbers.**

## 5. If it is ever repeated

Rider on board for the tilt; lift 25–30 cm instead of 13 (a bigger signal against the same
noise); swap the scales left/right once; one scale per wheel, all four at the same time.
