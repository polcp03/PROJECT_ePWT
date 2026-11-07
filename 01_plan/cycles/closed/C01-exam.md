# C01 — Preparation exam for the review

> [!abstract] How it works
> You answer first, by voice, even half an answer or an "I don't know, but I think…".
> Claude corrects under each question. **Your graded answers are the deck's script**: each
> block becomes one or two slides.
>
> ★ = a question the mentors will almost certainly ask.
> Review: **Friday 9 October**.

---

## A · The approach — without this, the rest doesn't stand

**A1 ★** There are no tyres, so no coast-down either. Why do you build a model **before** having
the measurements? What do you gain, what risk do you run, and how do you avoid ending up tuning
the model until the curve looks nice?

**A2 ★** You weighed the quad: 38 kg. The repo estimated 40 kg. Was the estimate good or bad?
Answer with numbers, not adjectives. What does that 38 include and what doesn't it?

**A3** MEASURED, ESTIMATED, ASSUMED, MISSING: how do they differ? Why does labelling each
parameter change what you can conclude from the model?

## B · Longitudinal dynamics — the core of the presentation

**B1 ★** Write the longitudinal force balance from memory. For each term: what does it depend
on, and how does it grow with speed (constant, linear, quadratic)?

**B2 ★** How do you go from motor torque to force at the wheel? Which parameters come in? If
each one rises 10 %, what happens to the force?

**B3 ★** Why is `r_roll` the most leveraged parameter of the whole vehicle? Hint: a 6 % error
in `r_roll` sneaks in in **two** places. Which?

**B4** When the vehicle accelerates you also accelerate things that spin: rotor, pinion,
wheels. How do they enter the equation? Why does the rotor barely weigh in the result, even
though it spins 8 times faster than the wheel?

**B5 ★** `Crr` and `CdA`: which of the two dominates at 15 km/h, and which at 50 km/h? Why does
a coast-down of this quad measure `Crr` well and `CdA` badly?

**B6** What does your model **not** capture? List at least four things, and for each say when it
would stop being negligible.

## C · Motor — the basics, said well

**C1 ★** Write the PMSM torque equation in dq. Where does each term come from? And the 3/2?

**C2 ★** You measured `λm` with three different methods and they agree within 0.02 %. Why does
that matter more than repeating the same method ten times?

**C3** What limits the motor's top speed? With a 48 V bus, at what speed does the back-EMF eat
all the voltage the inverter can give you? Do it on paper with your `λm` and `p`.

**C4 ★** Motor current and battery current: why are they not the same? At low speed and maximum
torque, which of the two is larger, and why?

## D · Battery — the minimum, and safety

**D1** What is the simplest battery model that works for this? What effect does `R_int` have on
the available torque at high speed?

**D2 ★** You have seen battery peaks of 40 A, and the BMS cuts at 40 A. The VESC has a motor
current limit and a battery one. Which of the two protects the pack? Why isn't the other enough?

## E · Prediction and validation — what sets you apart

**E1 ★** Which three or four quantities will you predict? For each: the value, its error band,
and the concrete test that will validate it once you have tyres.

**E2** How do you calculate that band? Which parameter contributes most of each prediction's
uncertainty?

**E3 ★** Suppose you measure and the prediction falls outside the band. What do you conclude?
And what can you **not** conclude?

## F · What you don't understand

**F1 ★** Tell me three things from this cycle you still don't understand. They are the most
valuable 10 minutes of the review: bring them prepared, not improvised.

---

## Answers and corrections

_(filled in as you answer)_

---

## G · Understanding the model (round of 9 Oct, before touching the deck)

**G1** Which variable of the quad cannot change suddenly, and which can change in milliseconds?
→ With that: why does the model have a single integrator?

**G2** The "VESC ramp" block is a *Rate Limiter*, 0.3 s up and 0.1 s down. If you twist the
throttle from 0 to 100 % at once, what does that block do to the current command?

**G3** The "Motor + VESC limits" block computes T = 3/2·p·λm·iq, where iq is the smallest of
three limits. For each limit (120 A motor, voltage ceiling, 40 A battery): which one rules at
standstill, which at mid speed and which near top speed?

**G4** Why does the motor need to know how fast the quad is going? Three reasons.

**G5** For each number on slide 4, where does it come from? Measured by you / estimated by the
VESC / configured by a person / assumed. Include R_int.

**G6** What limits top speed: the force balance or the battery voltage? Why does the tornado
say CdA barely moves it?

**G7** You have a simulator and want to know how much top speed changes with Crr. What would you
do? (That is how the bars and the bands were calculated.)

**G8** If you designed the coast-down, from what speed would you start it? What do you gain by
starting higher, and what does it cost you?

**G9** Does it spin at full throttle? F_trac = (3/2·3·0.016855·120)·8.3636·0.95/0.155.
F_grip = μ·0.65·110·9.81 with μ = 0.75. Calculate it and say whether launch control is needed.

**G10** Your 04_model/CLAUDE.md says "don't skip levels: each level is validated before the
next". You want C02 = motor + inverter without having validated the vehicle. How do you defend
it in front of the mentors?

> [!success] Block G answered on 9 Oct — verdict in the chat
> ✅ G1, G2, G6, G7, G8, G9 · ⚠️ G3 (you didn't see the battery limit), G4 (the *what for*),
> G5 (R_int and 0.95/√3). Corrections applied to the deck. **G10 still unanswered.**

---

## H · Rehearsal: the question you'll get on each slide

No answers, on purpose. Answer out loud, without looking at the slide. If one doesn't come out
in 30 seconds, that is the slide to go over.

| Slide | The question |
|---|---|
| 02 | Why didn't you wait for tyres? What does a model without data gain? |
| 03 | Why is rolling constant and aero growing with v²? What is m_eq and why isn't it just the mass? |
| 04 | Of all the ASSUMED ones, which worries you most and why? Where does μ = 0.75 come from? |
| 05 | Why aren't battery current and motor current the same? What happens from 9 km/h on? |
| 05 | Why does the curve collapse near 35 km/h? |
| 05 | In C00 you said a 1.9 kW battery ceiling; today you say 1.8. What changed? |
| 06 | Why a single integrator? What goes in and out of each block? |
| 06 | What does the −0.6 % validate and what does it **not** validate? |
| 07 | How does each prediction's ± band come out? Are they simulations or hand calculations? |
| 08 | Why doesn't the pack voltage enter the band? |
| 09 | Why from 30 km/h and not from 15? Why there and back? |
| 10 | Why don't you model tyre slip? |
| 11 | (You ask this one) How would you set current limits on a combustion engine? |
| 12 | **G10:** your own rule says "don't skip levels". Why motor + inverter in C02 without validating the vehicle? |

And one more, which always comes: **A1, in your words** — what is the difference between
calibrating and validating a model?

---

## I · For when you open L2 (after the review)

`04_model/models/longitudinal_L2.slx` is the same physics as L1, grouped in 4 blocks, with two
empty gaps. Filling them is yours.

**I1 — Load transfer.** The `F_grip (static - L2 hook)` block uses `μ·x_cg·m·g` today. When
accelerating, the rear normal force changes. Write the missing term yourself. Which parameter
do you need that is MISSING in `vehicle_params.m` today?

**I2 — Launch control.** The `Launch control hook` block does nothing today. To limit the
current when the wheel spins, which signal tells you it is spinning? Does the model have it
today? If not, what would you have to add first?

**I3 — Before simulating.** When you fill in I1: do you expect the 0 → 25 km/h time to go down,
up or stay the same? Why? Write it **before** running `run_regression_L1_L2.m`.
