# Reviews

One deck per review. **Always the same visual system**, so nothing is redesigned every two weeks.

> [!success] Status: v6 built and verified
> `C00-kickoff.pptx` — 14 slides. Checked with `_check.py` (zero overflows) and rendered one by
> one with PowerPoint.
>
> **v6, after Pol's review of 8 Sep:** the "objective zero" slide is out (its two columns merge
> into 02) and so is the configuration-findings slide. The gear ratio goes from a paragraph to
> four formulas, the envelope gains the voltage ceiling and loses the rad/s axis, the method
> slide becomes chips, and the plan shows the 2027 horizon.
>
> **Rule of this v6: it is an OVERVIEW.** If a slide needs a paragraph to be understood, the
> problem is the paragraph. Less text, more figure.
> v1 (rejected design) stays in `_archive/presentations-v1/` as a reference of what not to do.

## The visual system

It comes from the **DYN-09** template (Formula Student, UPC Manresa) that Pol uses at work:
photo band on top, blue strip with the title, body, blue strip at the bottom, chevron with the
logo in the corner. The structure is kept; the palette changes.

| | |
|---|---|
| **Name** | OFF-ROAD EV PLATFORM · badge `EV` |
| **Body** | White (DYN-09 has it black; the quad is blue/white) |
| **Primary blue** | `#1D4E9C` — sampled from the quad's real bodywork |
| **Dark blue** | `#0F2E63` — cover and the requests slide |
| **Typeface** | Arial, as DYN-09 |
| **Format** | 10 × 5.625 in (16:9), identical to the template |

Everything lives in `_brand.py`. A colour is never written twice.

## The five layouts

| Layout | When | Example |
|---|---|---|
| `cover` | Cover. Vertical photo on the left, blue block on the right | 01 |
| `std` | Exact DYN-09: photo band + strip + short body | 02, 14 |
| `split` | Strip on top + full-bleed photo column | 03 |
| `tall` | Strip on top, full-height body. For figures and tables | 04–12 |
| `dark` | Whole slide in dark blue. Only for "what I need from you" | 13 |

## Files

| File | What it is |
|---|---|
| `_brand.py` | Palette, typeface and geometry. Single source |
| `_deck.py` | The five layouts and the primitives (`card`, `chip`, `stat`, `img`) |
| `_figures.py` | Generates the badge, diagrams, plots and crops into `assets/` |
| `C00_kickoff.py` | The C00 deck content. It only says **what** goes in, not **where** |
| `_check.py` | Geometric check: warns about text that overflows its box |
| `_audit.py` | Number audit: every figure on every slide against the repo's sources of truth |
| `_render.ps1` | Renders the PPTX to PNG with PowerPoint, to review by eye |
| `_pdf.ps1` | Exports the PPTX to PDF (what gets shared) |
| `_template-DYN-09.pptx` | The original Formula Student template. Reference, not edited |
| `assets/` | Photos, web images, crops and figures. `photos/` and `web/` are sources; `crops/` and `figures/` are generated and stay out of Git |
| `cover/` | The README cover image of the public repo and its script |
| `C00-kickoff.pptx`, `.pdf` | **Generated.** Don't edit by hand: it is lost on rebuild |

The check PNGs go to `_renders/`, which is outside Git. They are rebuilt with one command; they
are not kept.

## Rebuild it

```bash
./.venv/Scripts/python.exe 09_reviews/_figures.py
./.venv/Scripts/python.exe 09_reviews/C00_kickoff.py
./.venv/Scripts/python.exe 09_reviews/_check.py
powershell -File 09_reviews/_render.ps1 09_reviews/C00-kickoff.pptx _renders
powershell -File 09_reviews/_pdf.ps1 09_reviews/C00-kickoff.pptx
```

## Take it to another computer

There is no Google connector in this environment, nor `rclone` nor the Drive API. The reliable
path is manual and takes half a minute:

1. `_pdf.ps1` generates the PDF.
2. Upload the PDF to Drive. It is presented from the browser on any machine and **goes through
   no converter**, so it looks exactly as it does here.
3. If it also needs editing in Google Slides: upload the `.pptx` and open it with Slides. Drive
   converts it.

> [!warning] Converting to Slides can move text around
> Google Slides recomputes line breaks with its own metrics, so the same fault `_check.py`
> hunts can come back. If you convert, check the slides with the most text — **02, 07 and
> 10** — before presenting. To just present, the PDF is the risk-free option.

> [!danger] The step that is never skipped: `_check.py`
> python-pptx **does not measure text**. It writes a 2 cm box and puts 4 cm of sentence in it
> without complaint: the file opens fine and looks broken. That was the repeated fault of v1
> and v2.
>
> `_check.py` rebuilds the line breaks with Arial's real metrics and warns about the three
> things that really are wrong:
>
> | Warning | What it means |
> |---|---|
> | `SPILL` | The text spills out of the coloured card holding it |
> | `COLLIDE` | The text grows downwards and runs under the next box |
> | `FOOTER` / `BOX/FOOT` | Text or a box invades the blue footer strip |
>
> A text box growing over white is **not** a fault, so it is not flagged. It must say `OK`
> before rendering.

> [!tip] And even so, look at the render
> There is no LibreOffice on this machine, but there is PowerPoint, and `_render.ps1` drives it
> over COM. The checker catches overflows; the render catches the rest (lines crossing in a
> diagram, unlucky photo crops, contrast).

## Content structure (C00)

A design presentation answers three questions per component: **what it is**, **how it is
built**, **why this one and not another**. Slides 6 and 7 follow that pattern explicitly.

| # | Slide | What it is for |
|---|---|---|
| 01 | Cover | |
| 02 | What this project is | Plant + digital twin + cycle, and what carries over from combustion calibration and what doesn't |
| 03 | The vehicle | Basic data + **the four drivetrain formulas** |
| 04 | System architecture — as it is today | No VCU, no logging, brakes not connected |
| 05 | System architecture — where it is going | The VCU takes the vehicle layer. Torque over CAN |
| 06 | The powertrain, component by component | Battery / inverter / motor, with the why of each |
| 07 | Where the limits actually are | **The envelope, with its three ceilings: current, battery and voltage** |
| 08 | What the model needs | The three equations and the parameters they ask for |
| 09 | How the machine was measured | Oscilloscope, Hall count, spin-down. And the coming coast-down |
| 10 | How I learn, and what I refuse to delegate | **First principles + the AI keeps the bookkeeping** |
| 11 | How the work is organised | The cycle and the 45 minutes |
| 12 | The plan to December | C01–C06 with review dates, and the 2027 horizon |
| 13 | What I need from you | Dark background. The explicit request |
| 14 | What I am asking for today | Close with a date |

If something has to be cut for time, the cheapest is **11**.

> [!tip] Why 10 goes where it goes
> The AI slide cannot come before the measurement ones. If you say you work with agents and
> **then** show the numbers, the mentor's silent question is "did you do this yourself?". It
> goes after, merged with first principles, so the message is *the AI keeps what teaches
> nothing*.

> [!warning] The envelope has three ceilings, not two
> Up to v5 the battery power hyperbola ran all the way to the measured no-load speed. That
> corner is **not reachable**: at that speed the back-EMF already eats the whole bus and the
> machine cannot give torque. `_figures.envelope()` now solves the voltage constraint
> (`|v| ≤ 0.95·V_bus/√3`) and draws the branch that closes the envelope at no load. It is also
> where field weakening would act, which on this motor is a bad deal:
> `I_ch = λm/Ld = 170 A` against 120 A available.

### Content decisions kept from v1

- The measurement slide doesn't say "I measured this" but **"I measured, cross-checked and found
  a contradiction"**.
- It says explicitly that **it doesn't start from zero**: calibrating an electric motor is
  similar to calibrating a combustion one.
- The requests slide goes alone with a dark background, and makes clear what is **not** asked
  of them: validating FOC.

---

## C01 — review of 9 October 2026

> [!success] Status: v2 built and verified
> `C01-review.pptx` / `.pdf` — 12 slides. `_check.py` OK, render reviewed slide by slide.
> v1 (night of the 8th) was thrown out entirely after Pol's feedback: see `C01-feedback.md`.

| File | What it is |
|---|---|
| `_figures_c01.py` | C01 figures + new photo crops (`assets/crops/c01_*.jpg`). Reads the CSVs in `04_model/results/` |
| `C01_review.py` | The deck. **Parses `04_model/params/*.m`** and the model CSVs: no number is typed by hand |

```bash
./.venv/Scripts/python.exe 09_reviews/_figures_c01.py
./.venv/Scripts/python.exe 09_reviews/C01_review.py
./.venv/Scripts/python.exe 09_reviews/_check.py 09_reviews/C01-review.pptx
./.venv/Scripts/python.exe 09_reviews/_audit.py 09_reviews/C01-review.pptx
```

If the model changes, first: `04_model/scripts/run_predictions_L1.m` (regenerates the CSVs).

| # | Slide | What it answers |
|---|---|---|
| 01 | Cover | |
| 02 | Why a model before the data | Tyres + ESP32 → model first, predictions frozen |
| 03 | The force balance, with numbers | The equation with each value and its inputs |
| 04 | Where every number comes from | MEASURED / VESC ESTIMATE / CONFIG / ASSUMED, with the why |
| 05 | Where the limits are | Wheel force vs speed: 120 A → 40 A battery → voltage, and the road load |
| 06 | The model: four blocks, one state | Clean diagram (not a Simulink screenshot) + check against C00 |
| 07 | Predictions, frozen before the test | 4 predictions with a band + the two simulated manoeuvres |
| 08 | What moves the predictions | Tornado: which parameter moves each prediction |
| 09 | Designing the tests | Coast-down from 30 km/h (Pol's idea, checked) + instrument per prediction |
| 10 | What is in the model, and what is next | L1 / L2 / C02 |
| 11 | What I need from you | How to set the current limits (dark background: it is the request) |
| 12 | Next: C02, motor and inverter | C02 proposal + 2027 horizon |

> [!tip] System changes made in C01
> - `_deck._band`: line spacing 1.0 in the title. That was the title "misalignment" Pol saw:
>   at 1.15 the line was taller than the band. Also affects C00 if rebuilt (for the better).
> - Titles ≤ 42 characters across the deck, so they all come out the same size.
> - `_check.py` now prints in UTF-8 (it used to crash on `−` or `≤` in the Windows console).
> - **New `_audit.py`:** the skill's number audit, automated. Each number on each slide → the
>   repo file:line that backs it, or `NOT FOUND`. C01: 65 numbers, 0 without a source.
> - **Speaker notes:** each slide carries the mentor's likely question (only the question).
