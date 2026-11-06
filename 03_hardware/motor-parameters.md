# Motor parameters

> [!warning] Rule
> Every value carries its source. **MEASURED** / **ESTIMATED** / **UNVERIFIED**.
> Nothing goes into the model without this label.

The values for simulation live in [`04_model/params/motor_params.m`](../04_model/params/motor_params.m).
This document explains **where they come from and which convention they follow**.

## FOC detection ×3 — 2026-09-07. The saliency DOES converge

Three runs in a row, changing nothing, all at **I = 40.00 A**:

| Run | R [mΩ] | L [µH] | Lq−Ld [µH] | λ [mWb] |
|---|---|---|---|---|
| 1 | 27.83 | 105.95 | 13.41 | 15.978 |
| 2 | 28.14 | 106.10 | 13.91 | 15.859 |
| 3 | 28.10 | 105.96 | 13.31 | 15.919 |
| **Mean** | **28.02** | **106.00** | **13.54** | **15.919** |
| Spread | 0.5 % | 0.06 % | **1.9 %** | 0.3 % |

> [!success] The saliency was repeatable; what changed were the settings
> With fixed conditions it repeats within **1.9 %**. The old range of 9.45 to 16.90 µH came
> from runs with a **different detection current**: the 29-Jul one used 97.85 A against
> today's 40 A.
>
> In other words: **it wasn't noise, it was magnetic saturation.** Saliency is a function of
> current. Any MTPA table would have to capture exactly that, and any single saliency number
> is only valid at its own current.

Hence: **Ld = 99.23 µH, Lq = 112.77 µH**, ratio **Lq/Ld = 1.136**.

## Rotor inertia and friction — 2026-09-07

Three starts up to no-load speed, each followed by free deceleration.
VESC log in `06_data/2026-09-07_inertia/`, analysis in `04_model/scripts/inertia_from_vesc_log.py`.

Drag model `T(ω) = T₀ + b·ω`. The deceleration gives the **ratios**
`T₀/J = 405 s⁻²` and `b/J = 0.89 s⁻¹`; the no-load steady point gives the **scale**
(`Kt·iq = 0.1427 N·m at 573.9 rad/s`). Two relations, one solution.

| | Value |
|---|---|
| **Rotor inertia `J`** | **1.558·10⁻⁴ kg·m²** (±14 %) |
| Dry friction `T₀` | 63.1 mN·m |
| Viscous friction `b` | 138.8 µN·m·s/rad |
| Split at 5480 rpm | 44 % dry / 56 % viscous |
| Mechanical time constant `J/b` | 1.12 s |

> [!warning] Why only ±14 % and not better
> **The clean method could not be used.** The idea was to subtract two tests (accelerating at
> a known current minus freewheeling) so that friction cancels by itself. But the start
> lasted ~0.3 s and the VESC logs at 15 Hz: three samples with the current falling from 96 to
> 11 A. Useless.
>
> The check explains it: with `J = 1.56·10⁻⁴` and 120 A available, the motor at no load
> reaches 5480 rpm in **10 ms**. No 15 Hz log captures that.
>
> What was used (the deceleration slope anchored on the steady drag) is valid, but **it
> depends on `Kt`**, that is, on `λm`. It is not independent.
>
> **And lowering the current does NOT fix it.** For the start to last 2 s it would take
> ~2 A, and the motor already draws 1.88 A just to overcome its own drag. There is no margin.
> The rotor is so light that at any useful current it accelerates faster than the log can see.
> It is physics, not settings.

> [!success] Decision: not repeated. ±14 % is more than enough
> | | Inertia | Share |
> |---|---|---|
> | Rotor | 1.56·10⁻⁴ kg·m² | **0.4 %** |
> | Vehicle, seen from the motor | 3.85·10⁻² kg·m² | **99.6 %** |
>
> The vehicle weighs **247 times** more than the rotor. ±14 % on 0.4 % is **±0.06 % of the
> total**. Refining it changes no result.
>
> **What will be done**, with the wheels fitted: the same test with the quad on stands. The
> total inertia is 250 times larger, so the deceleration lasts minutes instead of a second
> and the 15 Hz log is plenty. That is the number the model really uses.
>
> If the rotor `J` were ever needed precisely, the method is to bolt a disc of known inertia
> to the shaft and subtract. Not needed.

## VESC FOC detection — the history of two runs

| Parameter | 2026-07-29 | 2026-08-10 (saved config) | Spread |
|---|---|---|---|
| Resistance `R` | 27.90 mΩ | **28.80 mΩ** | 3 % |
| Mean inductance `L` | 106.49 µH | **105.25 µH** | 1 % |
| Saliency `Lq−Ld` | 16.90 µH | **9.45 µH** | **79 %** |
| Flux linkage `λm` | 16.07 mWb | **16.016 mWb** | 0.3 % |
| Sensors | Hall | Hall | — |

Sources: `Screenshot 2026-07-29 152318.png` and `MOTOR_1.9.xml`.

**It was believed** that the saliency was unrepeatable noise. **False**, see the section
above: the runs used different detection currents and saliency depends on current. These two
rows are kept only as a historical record; the current values are those of the 07-Sep batch.

## Flux linkage: **λm = 16.86 mWb, MEASURED** — 2026-09-07

> [!success] Open-circuit back-EMF, independent of the VESC
> Motor disconnected from the inverter, probe between phase A and phase B, driven by a drill.
>
> $$\lambda_m = \frac{A_1}{\sqrt{3}\cdot 2\pi f}$$
>
> **Raw data** (`06_data/2026-09-07_back-emf/raw/scope_txt/`), two captures at 1310 and 2510 mechanical rpm:
> **16.826 and 16.883 mWb → agree within 0.17 %** with the speed doubled.

### The amplitude is taken as RMS, not as the FFT peak

The drill does not spin at constant speed: the period varies by **1–2 %** within the window.
That widens the fundamental's peak in the FFT and makes an amplitude read from the peak come
out **low**.

The estimator `A1 = √2 · RMS(fundamental band)` is immune to that widening.

| Estimator | Spread between the two captures |
|---|---|
| FFT peak | 1.08 % |
| **Band RMS** | **0.17 %** |

And the bias has the right sign: the capture with more jitter (1.97 %) was the one giving the
lowest value. It is the complete explanation, not a correction by eye.

### History: the screenshot batch gave 16.51 mWb

Before exporting raw data, **43 screenshots were analysed by reading the pixels**
(calibrating with the gridlines). Fit through the origin: `A1 = 0.17968·f`, R² = 0.9911,
intercept 1.3σ from zero, and `λm` flat over a 16:1 speed range.

It came out **16.51 mWb, 2.0 % below** the raw-data value: the same jitter bias, plus 47 mV of
pixel resolution. Agreeing within 2 % validates the pixel extraction method, but **the raw
data rules**.

Method lesson: the export format is not an administrative detail. One good CSV was worth more
than 43 images.

### Third independent confirmation: the no-load steady state

From the same inertia log, with the motor pinned at the duty ceiling for 443 samples:
16,440 ERPM, `|v_dq|` = 28.886 V, `iq` = 1.883 A, battery 52.77 V.

$$\lambda_m = \frac{|v| - R\,i}{\omega_e} = 16.748\ \text{mWb}$$

The VESC reports the voltage it **commands**, not the one it applies. Dead time costs
`t_d · f_sw · V_bus` = 0.12 µs × 30 kHz × 52.77 V = **0.19 V**. Giving it back:

$$\lambda_m = 16.858\ \text{mWb} \quad\text{against}\quad 16.855\ \text{mWb from the oscilloscope}$$

**A 0.02 % difference.** Two methods that do not share a single assumption.

Those same 0.19 V would weigh more at the low voltage of the detection test. But detections
vary too much between sessions to see that effect (next section).

### The VESC detection is no reference: it varies more than any bias

> [!warning] Corrected on 2026-11-06
> Until today this section said the detection "falls 5.5 % short, and in the right
> direction", with dead time as the cause. That came from **a single session** (07-Sep).
> Detections on other days give values above and below the measurement, so that 5.5 % is not
> a result.

| Source | λm [mWb] | vs oscilloscope |
|---|---|---|
| **Oscilloscope, raw data** | **16.855** | — |
| **No-load steady state + dead time** | **16.858** | **+0.02 %** |
| No-load steady state, uncorrected | 16.748 | −0.6 % |
| FOC detection, 29-Jul | 16.07 | −4.7 % |
| FOC detection, 10-Aug (saved config) | 16.016 | −5.0 % |
| FOC detection ×3, 07-Sep, at 40 A | 15.86 – 15.98 | −5.9 to −5.2 % |
| Detection in the config until 05-Nov (EXP-003) | 16.19 | −3.9 % |
| Later detections (Pol, noted 06-Nov) | 17.0 · 16.2 · 16.7 · 16.8 | +0.9 to −3.9 % |

**Within one session the detection repeats within 0.3 %; between sessions it goes from 15.86
to 17.0 mWb, 7 %.** The measurement, 16.86, falls inside that range. With that spread you
cannot claim a fixed detection bias, nor its sign, nor its cause. The dead-time mechanism
exists, but the data do not separate it from the session-to-session variation.

What changes from one session to the next: **not recorded.** Most likely the detection
current and the temperature, as happened with the saliency. From now on, every detection is
logged with its current and its temperature.

**Method lesson** (the same as the saliency): a detection number is only valid with its
conditions. Before claiming "X is off by N %", look at how much X spreads when repeated on
different days. If it spreads more than the effect, there is no effect to report.

**Consequence:** `Kt = 1.5·p·λm` = **0.0758 N·m/A** with the measurement. The reference λm is
the oscilloscope's, confirmed by the no-load steady state; the detection is not used. The
saved configuration (`vesc/MOTOR_1.9.xml`, 06-Nov) already holds 16.855 mWb, so the VESC's
observer and the model start from the same value.

> [!note] Pol's decision, 2026-11-06
> The values in the saved configuration (`vesc/MOTOR_1.9.xml`) are **final**:
> λm = 16.855 mWb, R = 18.76 mΩ, L = 105.6 µH (Lq−Ld = 14.42 µH → Ld 98.39 µH, Lq 112.81 µH).
> They are already in the model (`04_model/params/motor_params.m`) and in `baseline.md`. The
> 07-Sep values in this document (R 28.02 mΩ, L 106.00 µH) stay as history.

### Harmonic content — and a check that the measurement is good

Ratio to the fundamental, **identical in both captures**:

| Harmonic | 5th | 7th | 11th | 13th | THD |
|---|---|---|---|---|---|
| % of fundamental | 4.0 | **8.1** | 2.0 | 1.4 | **9.4 %** |

> [!success] No 3rd or 9th, and that is how it must be
> Triplen harmonics are **in phase in all three phases**, so they cancel in any line-to-line
> voltage. Their absence is not luck: it is physics confirming the measurement was taken well.

The dq model assumes a sine, so **it will not reproduce the torque ripple** that the 5th and
7th create (seen as 6th order in the rotor frame). Irrelevant at vehicle level; worth
remembering before blaming something else for a correlation gap.

Reproducible analysis in `04_model/scripts/backemf_extract.py` and `backemf_fit.py`.

## Convention: SETTLED by the code, no longer an unknown

> [!success] The VESC's `R` is **per phase**, not line to line
> `mcpwm_foc_measure_resistance()` computes `R = norm(v_dq) / norm(i_dq)` with the rotor
> locked ([`mcpwm_foc.c:1869`](vesc/_firmware/motor/mcpwm_foc.c), sampling at `:4144`).
> `v_dq` and `i_dq` are **phase** quantities in the amplitude-invariant dq frame.
> So `foc_motor_r` is the per-phase resistance.
>
> **Check still to do:** the multimeter between two phases should read ≈ 2·R = 57.6 mΩ.
> It no longer settles a doubt; now it is a check that the VESC test does not lie.

Important nuance: that `R` includes the MOSFETs' on-resistance and the dead-time effect. It is
an **upper bound** on the real winding resistance.

The VESC uses exactly the equations of the Simulink PMSM block
([`virtual_motor.c:305-345`](vesc/_firmware/motor/virtual_motor.c); the firmware's own comment cites MathWorks):

$$v_d = R i_d + L_d \frac{di_d}{dt} - \omega_e L_q i_q$$
$$v_q = R i_q + L_q \frac{di_q}{dt} + \omega_e (L_d i_d + \lambda_m)$$
$$T_e = \tfrac{3}{2} p \,(\lambda_m + (L_d - L_q) i_d)\, i_q$$

And the inductance split ([`foc_math.c:782`](vesc/_firmware/motor/foc_math.c)):
`Lq = L + diff/2`, `Ld = L − diff/2` → **Ld = 100.53 µH, Lq = 109.98 µH**.

The four values go into the Simulink block **without rescaling**.

## Pole pairs: **p = 3, MEASURED** — 2026-09-06

> [!success] Hall pulse count, with the drivetrain fitted
> One Hall line gives `p` cycles per mechanical turn of the motor. One turn of the sprocket
> (92T) is 92/11 = 8.364 motor turns, so `8.364·p` flashes are expected: **25.1 if p=3**,
> 33.5 if p=4.
>
> **Counted: 25, repeatable.** → `p = 3`. No grey zone.
>
> Method: an LED with a 1 kΩ resistor between +5 V and the Hall signal (open-collector output:
> it sinks current, it does not source it). One sprocket turn in ~30 s, three repeats.

As a bonus, it validates the **92/11 gear ratio**: with a different ratio the count would not
have landed on any valid row of the table.

And it closes the contradiction this document had: the market rated torque of ~4.0 N·m **does
not belong to this motor**. With `p = 3` and the `Kt = 0.0758 N·m/A` that comes from the
measured λm, 4 N·m would need 53 A, far above the quoted current (34–40 A). The MY1020/BM1109
reference is dropped as a reliable source, just as [baseline](baseline.md) warned.

### Historical record of the reasoning

The VESC had `si_motor_poles = 6` (p = 3) **typed by hand**, not measured.

> [!important] The quad running well does not validate `p`
> `si_motor_poles` only feeds the RPM display and the telemetry
> ([`commands.c:929`](vesc/_firmware/comm/commands.c), `canard_driver.c:517`).
> **It does not enter the FOC control law**, which always works in electrical angle.
> You could ride for years with the wrong `p` and not notice.

The earlier table set "no-load speed says p=3" against "torque says p=4". That was the wrong
framing: **both references came from the same unconfirmed motor** (MY1020/BM1109). They are not
two conflicting pieces of evidence, they are zero evidence.

Direct consequence: `Kt = 1.5·p·λm` scales linearly with `p`. **The whole torque axis of the
model is worth what that measurement is worth.** With p=3 and the measured λm,
`Kt = 0.0758 N·m/A` → 3.03 N·m at 40 A. (With the λm of a single detection, 15.92 mWb, it came
out 0.0716: that is why the detection is not used.)

### How to measure it

> [!success] Counting Hall transitions — the good method
> One electrical turn is **6 Hall state changes**. Counting transitions over one full
> mechanical turn and dividing by 6 gives `p` directly.
> It counts discrete events, it does not measure speed: no error builds up.

ERPM alternative: `ERPM = RPM_mech × p`. Mark the wheel, turn it slowly, read ERPM in VESC Tool
and count turns on video. Faster, less exact.

## Motor opened — 2026-11-06 (Pol, by eye and ruler; photos on his phone)

| What | Value | Source |
|---|---|---|
| Topology | **9 slots, 6 poles (9N6P)**: 3 coils per phase, p = 3 | Counted (agrees with the Hall count of 2026-09-06) |
| Winding | **Star**: the three phase ends meet at one visible joint | Seen |
| Rotor | Laminated steel, hollow, on a splined shaft. OD ≈ 50 mm, length ≈ 60 mm | Ruler, approx. |
| Magnets | 6 poles, each **two NdFeB pieces of ≈ 20 × 30 × 2 mm** end to end (60 mm per pole) | Ruler, approx. |
| Between magnets | ≈ 5 mm of **lamination steel reaching the rotor surface**, with two small steel tips facing each other and a slit between them | Seen. Purpose not confirmed |
| Stator | Laminated, OD ≈ 90 mm, bore ≈ rotor OD | Ruler, approx. |
| Air gap | **≈ 1 mm** (Pol's estimate). With the rotor loose in the stator it touched on one side and showed ≈ 2 mm on the other | By eye, not measured |
| Magnet gaps, Hall spacing | "All the same" | By eye, not measured with calipers |
| Rotor mass | ≈ 850 g (unclear whether bearings and shaft ends are included) | Scale |
| Bearings | Turn smoothly, no play felt | Hand |
| Magnet surface | Light rub marks on some magnets | Seen. Cause open: assembly or running |
| Hall sensors | 3, held in a plastic cage, cannot move. Cable: 5 wires (5 V, GND, H1–H3), **no temperature wire** | Seen |
| Insulation phase-to-case | OK (2026-11-05) | Multimeter |

**Consequence for the model:** magnets on the surface **with iron between them** (inset
rotor). Along the q axis the flux crosses that iron instead of a magnet, so Lq > Ld. That is
consistent with the measured Lq/Ld ≈ 1.14; the saliency is real, not a measurement artefact.
Sanity check: pole pitch at r = 25 mm is 26.2 mm ≈ 20 mm magnet + 5 mm gap.

A large air gap does **not** explain Lq > Ld: the gap is in both the d and the q loop, so it
lowers both inductances and, if anything, shrinks the ratio. Only the d loop crosses a magnet
(2 mm, which flux sees as air): d ≈ 2 × (1 + 2) mm of "air", q ≈ 2 × 1 mm over the iron. The
iron is only 5 of every 26 mm of pole pitch, so most q flux still crosses magnets, hence 1.14
and not ~3.

**Hall placement error (19° spread, EXP-003), after the opening:** the sensors sit in a fixed
cage and look evenly spaced. Equal 5 mm iron gaps shift every edge by the same amount, so they
cannot make a *spread*. Left as candidates, unmeasured: unequal magnet gaps (1 mm ≈ 7° el.),
different switching thresholds between the three Hall chips (the field changes slowly across
the 5 mm iron gap, so a small threshold difference becomes a larger angle). Not pursued: the
fix chosen on 2026-11-05 (handover at 1000/2000 erpm) already removes the ripple above
1000 erpm.

**Photos:** `09_reviews/assets/photos/2026-11-06_*.jpg`. One of them
(`_stator-cable-end`) shows a small black part taped on an end-turn, marked "16?°C". It looks
like a thermal protector (a bimetal switch that opens at that temperature). Pol, having seen it:
most likely just a piece of heat-shrink. Not checked; the motor is closed. Cheap check whenever
the cable is open: any wire that is neither one of the 5 Hall wires (5 V, GND, H1–H3: the three
sensors share supply and ground) nor one of the 3 phases.

**Not measured before closing:** caliper gaps and Hall spacing, stator bore, shaft and inner
hole of the rotor (→ a geometric J to check against 1.558e-4 kg·m²).

## Still to measure

- [x] **Pole pairs** = 3 (Hall count, 2026-09-06)
- [ ] Line-to-line R with a multimeter, to compare with the expected ≈ 56.0 mΩ (2·28.02)
- [x] **Back-EMF with the oscilloscope** → `λm` = 16.86 mWb MEASURED (2026-09-07)
      (16.51 was the screenshot batch, superseded by the raw data)
- [x] **Inertia and friction** → `J` = 1.558e-4 kg·m² (±14 %), 2026-09-07
- [x] **FOC detection ×3** → the saliency converges: 13.54 ± 0.26 µH
- [ ] **FOC detection with its conditions:** repeat several, noting detection current and
      temperature, to learn what moves the detected λm between 15.9 and 17.0 mWb
- [ ] **Vehicle** inertia on stands, with wheels: it is the one the model uses
      (lowering `l_current_max` does NOT work for the rotor alone — see the decision above)
- [ ] Loaded rolling radius, total mass, coast-down → see `vehicle_params.m`
