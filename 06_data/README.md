# Test data

One folder per campaign: `YYYY-MM-DD_<test>`. Inside, `raw/` holds the files exactly as the
instrument spits them out — **they are never edited**.

> [!warning] `raw/` is not in Git
> Oscilloscope raw files weigh hundreds of MB and cannot be diffed. They live on the local disk
> and are ignored. **This README is the index: if a raw file is not listed here, it does not
> exist.** What does go into the repo: small CSVs, and the analysis figures, which go to
> `04_model/results/`.

---

## `2026-09-07_back-emf` — open-circuit back-EMF

Motor disconnected from the VESC, probe between phase A and phase B, motor spun with a drill.
500 ms window, ±20 V range. This is the measurement that gives `λm = 16.86 mWb`
(see `03_hardware/motor-parameters.md`).

| Path | What | Size |
|---|---|---|
| `raw/low_speed/*.BMP` | 12 MaxiScope screenshots | 67 MB |
| `raw/mid_speed/*.BMP` | 13 screenshots | 73 MB |
| `raw/high_speed/*.BMP` | 32 screenshots | 179 MB |
| `raw/scope_txt/*.txt` | 2 numeric exports from the oscilloscope, at 1310 and 2510 mechanical rpm | 56 MB |

**Analysis:** `04_model/scripts/backemf_extract.py` (reads the BMPs) →
`backemf_fit.py` (fits λm and makes the figure) and `backemf_from_csv.py` (same measurement
from the TXT files, immune to the drill's jitter).

---

## `2026-09-07_inertia` — rotor inertia and friction

VESC Tool log during a free deceleration. CSV with `;` as the separator.

| Path | What |
|---|---|
| `2026-09-07_inertia_test.csv` | VESC Tool log (195 KB, versioned) |

**Analysis:** `04_model/scripts/inertia_from_vesc_log.py`.

---

## `2026-10-31_can_logger_bench` — CAN logger on the bench

Raw CAN traffic from the VESC recorded by our own logger (`05_firmware/arduino/can_logger/`),
wheels in the air. Format in the logger's README. Full story in
`07_experiments/EXP-002-spi-noise-can-logger.md`.

| Path | What |
|---|---|
| `raw/log_003…010.csv` | First recordings, cut short by ESP32 resets |
| `raw/log_012.csv` | Test A: ESP32 alone, no VESC (138 s) |
| `raw/log_013.csv` | Test B: VESC on, motor stopped (144 s) |
| `raw/log_014.csv` | Test C: with throttle, before the hardware fix (70 s, corrupt frames) |
| `raw/log_017.csv` | **With throttle, after the fix** (137 s, 0 corrupt). Majority merge of `log_017_dl1…3.csv` |
| `raw/log_017_dl1…3.csv` | The three USB downloads as they came, with the serial port's garbage |

013, 014 and 017 were downloaded over USB three times and merged by majority: downloading over
the serial port slips in the odd garbage line. With a card reader it is not needed.

**Analysis:** `04_model/scripts/can_log_decode.py` → figure
`04_model/results/can_logger_log017.png`.

---

## `2026-11-01_wheel_hall` — wheel speed sensor

Front wheel turned by hand, quad on the stand. A 3144 Hall on GPIO 34 and 10 magnets on a
160 mm diameter circle. Captured with `05_firmware/arduino/wheel_capture/` (reads the pin level
and the interrupt counter, CSV at 921600).

| Path | What |
|---|---|
| `raw/run1.csv` | Magnets placed by eye. `t_us,level,isr_edges`, ~575 magnets |
| `raw/run2_spacing_fixed.csv` | Magnets re-placed with a compass (chord 4.94 cm). Same format |
| `speed_raw.png` | Run 1: magnet-by-magnet speed and the one-turn average |
| `speed_run2.png` | Run 2: the same after re-placing |

**What came out:**
- **1 interrupt edge per magnet and 0 false ones** in both captures. The wiring is fine.
- **The magnet spacing error repeats every 10 pulses**, with the same percentage at any speed:
  ±20 % by eye, **±8 %** with a compass.
- **The one-turn average cancels it completely** (0.7 % of noise is left), at the cost of one
  turn of delay: 0.7 s at 5 km/h.
- A once-per-turn wobble remains: the magnet circle is not centred on the axle.
- **Next:** calibrate the real angle of each gap (like an ABS with an imperfect tone wheel) and
  choose the filter with data from the quad rolling. The `can_logger` will record it (`#wheel`
  lines) as soon as there is a new card.

**Analysis:** done in the session, no script saved. The first one needed for the quad's logs
will go to `04_model/scripts/`.

---

## `2026-11-05_low-speed-no-chain` — VESC low-speed control, chain off (EXP-003)

Wheels in the air, chain removed, VESC Tool log at ~33 Hz. Current requests 1 / 2 / ~2.5 A
twice, then a duty sweep 2 → 48 %.

| Path | What | Size |
|---|---|---|
| `raw/2026-11-05_22-06-04.csv` | VESC Tool realtime log, blend 2500/4000, 5354 rows, `;`-separated | 1.5 MB |
| `raw/2026-11-05_23-14-20.csv` | Same, blend moved to 1000/2000, 5277 rows | 1.5 MB |

**Analysis:** `plot.py` → `1_session.png`, `2_negative_current.png`, `3_ripple_vs_speed.png`; `compare.py` → `4_before_after.png`.
Conclusions in [EXP-003](../07_experiments/EXP-003-low-speed-control.md).

---

## `2026-11-06_mass-cg` — axle loads and CG height (task `{#cg}`)

Two bathroom scales (3 cm tall) under one axle at a time: level empty, level with Pol on board,
and tilt tests empty (other axle lifted 9.5 and 16 cm). No raw files: the dictated readings are
in [`readings.md`](2026-11-06_mass-cg/readings.md).

**Analysis:** derived with Pol in a session; results go to `03_hardware/baseline.md`.

---

## How to add a campaign

1. `mkdir 06_data/YYYY-MM-DD_<test>/raw`.
2. Drop the instrument's files into `raw/`, without renaming or trimming.
3. Add a section here: what was measured, with which setup and which script reads it.
4. The output figure goes to `04_model/results/`, never next to the data.
