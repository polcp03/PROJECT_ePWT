"""C00 — Kickoff review deck.  OFF-ROAD EV PLATFORM.

Content is English (public/technical, per CLAUDE.md). Every number here is
traceable to 03_hardware/, 04_model/params/ or 03_hardware/vesc/.

Rule for this deck: it is an OVERVIEW. If a slide needs a paragraph to be
understood, the paragraph is the problem, not the reader.

    ./.venv/Scripts/python.exe 09_reviews/_figures.py
    ./.venv/Scripts/python.exe 09_reviews/C00_kickoff.py
    ./.venv/Scripts/python.exe 09_reviews/_check.py
"""
from __future__ import annotations

import glob
import os
import sys

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _brand as B
from _deck import CROP, FIG, ROOT, WEB, Deck

OUT = os.path.join(HERE, "C00-kickoff.pptx")


def asset(pattern):
    hits = sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[0]


d = Deck("OFF-ROAD EV PLATFORM  ·  Kickoff review  ·  September 2026")


def bullets(items, size=B.SZ_BODY, color=B.INK):
    return [{"t": "—  " + t, "size": size, "color": color} for t in items]


# ==========================================================================
# 01 — Cover
# ==========================================================================
d.cover(os.path.join(CROP, "half_field.jpg"),
        "OFF-ROAD\nEV PLATFORM",
        "Powertrain modelling, control and validation on a real vehicle",
        "KICKOFF REVIEW\nPOL CRUAÑAS  ·  SEPTEMBER 2026")

# ==========================================================================
# 02 — What this is, and where I stand
#
# The three cards say what the project is. The two columns underneath say
# where I already have ground and where I do not, and they are the reason the
# closing slide can ask these two for a specific kind of review: they are
# engine people, so they need to know which half of this they can attack.
# ==========================================================================
sl, (x, y, w, h) = d.std("What this project is", "strip_quad.jpg")
d.text(sl, x, y - 0.08, w, 0.44,
       "An electric mini-quad, used as a bench for power electronics, "
       "machines and control. The hardware is finished — the work is "
       "modelling it and controlling it.",
       size=12.5, color=B.INK, bold=True, line=1.25)
cw = (w - 2 * 0.24) / 3
for i, (hd, bd) in enumerate([
    ("THE PLANT", "The vehicle.\nIt exists and it runs."),
    ("THE DIGITAL TWIN", "A Simulink model,\nparameterised from measurements."),
    ("THE ENGINE", "A two-week cycle,\nclosed by a review with you."),
]):
    d.card(sl, x + i * (cw + 0.24), y + 0.42, cw, 0.98, hd, [bd],
           fill=B.PANEL if i else B.BLUE_LT, accent=B.BLUE, hs=11, bs=10,
           pad=0.16)

cw2 = (w - 0.30) / 2
d.card(sl, x, y + 1.50, cw2, 1.30, "WHAT ALREADY TRANSFERS", bullets([
    "Test benches and measurement campaigns",
    "Torque and efficiency maps",
    "Correlating a model against real hardware",
], size=9.5), fill=B.BLUE_LT, accent=B.BLUE, hs=10, bs=9.5, pad=0.18)
d.card(sl, x + cw2 + 0.30, y + 1.50, cw2, 1.30, "WHAT DOES NOT", bullets([
    "Power electronics",
    "Electric machines in the rotating dq frame",
    "Embedded control and software architecture",
], size=9.5), fill=B.PANEL, accent=B.RISK, hs=10, bs=9.5, pad=0.18)

# ==========================================================================
# 03 — The vehicle, and why the gearing is what it is
#
# The four formulas replace a paragraph. Two of them say what the 92T bought,
# one says why a bigger crown would have bought nothing, and one says what it
# cost. The grip line is the only one built on assumed numbers and the figure
# labels it as such — see _figures.gearing().
# ==========================================================================
sl, (x, y, w, h) = d.split("The vehicle", os.path.join(CROP, "half_field.jpg"),
                           side="left", frac=0.34)
d.text(sl, x, y - 0.12, w, 0.26,
       "Nitro Motors mini-quad: 36 V lead-acid → 48 V lithium.",
       size=12, color=B.INK, bold=True)
facts = [
    ("Mass, with driver", "≈ 112 kg"),
    ("Wheels", "13 × 5.00-6  ·  r ≈ 0.155 m loaded"),
    ("Final drive", "chain 25H  ·  11T / 92T = 8.36:1"),
    ("Battery", "13S5P Li-ion  ·  48.1 V  ·  ~13 Ah"),
    ("Motor", "48 V PMSM  ·  ~1.9 kW  ·  3 pp"),
    ("Peak wheel torque", "76 N·m at 120 A"),
]
cw2 = (w - 0.24) / 2
for i, (k, v) in enumerate(facts):
    cx = x + (i % 2) * (cw2 + 0.24)
    cy = y + 0.16 + (i // 2) * 0.62
    d.rect(sl, cx, cy, cw2, 0.56, B.PANEL)
    d.text(sl, cx + 0.16, cy + 0.06, cw2 - 0.32, 0.18, k, size=9,
           color=B.GREY)
    d.text(sl, cx + 0.16, cy + 0.26, cw2 - 0.32, 0.24, v, size=10.5,
           color=B.INK, bold=True)
d.text(sl, x, y + 2.06, w, 0.22, "WHY 92 TEETH", size=9.5, color=B.BLUE,
       bold=True)
d.fit(sl, os.path.join(FIG, "fig_gearing.png"), x, y + 2.28, w, 1.90)

# ==========================================================================
# 04 — Architecture today
# ==========================================================================
sl, (x, y, w, h) = d.tall("System architecture — as it is today")
d.fit(sl, os.path.join(FIG, "fig_arch_today.png"), x, y - 0.02, w, h - 0.50)
d.rect(sl, x, B.FOOT_Y - 0.60, w, 0.46, B.PANEL)
d.text(sl, x + 0.20, B.FOOT_Y - 0.60, w - 0.40, 0.46,
       "The twist grip drives the inverter directly. Nothing sits between the "
       "driver and the torque, and nothing records what happens under load.",
       size=10.5, color=B.INK, anchor=MSO_ANCHOR.MIDDLE)

# ==========================================================================
# 05 — Architecture target
# ==========================================================================
sl, (x, y, w, h) = d.tall("System architecture — where it is going")
d.fit(sl, os.path.join(FIG, "fig_arch_target.png"), x, y - 0.02, w, h - 0.50)
d.rect(sl, x, B.FOOT_Y - 0.60, w, 0.46, B.BLUE)
d.text(sl, x + 0.20, B.FOOT_Y - 0.60, w - 0.40, 0.46,
       "A vehicle control unit takes the driver inputs — brakes included — and "
       "sends a torque request over CAN.",
       size=10.5, color=B.WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ==========================================================================
# 06 — The three components
# ==========================================================================
sl, (x, y, w, h) = d.tall("The powertrain, component by component")
cw = (w - 2 * 0.28) / 3
comps = [
    (os.path.join(CROP, "half_pack.jpg"), "BATTERY",
     ["13S5P Li-ion · 65 cells", "48.1 V · ~13 Ah", "JK smart BMS · 40 A"],
     "Configurable and observable: every cell voltage readable from the phone "
     "while the vehicle runs."),
    (os.path.join(WEB, "vesc_flipsky_1.jpg"), "INVERTER",
     ["Flipsky FSESC 6.7 Mini Pro", "70 A cont. · 200 A peak", "FOC · 30 kHz · CAN"],
     "Open source. I can read the firmware line that computes the torque, and "
     "export the whole configuration to XML — which is what parameterises the "
     "model."),
    (os.path.join(CROP, "half_motor.jpg"), "MOTOR",
     ["48 V PMSM · ~1.9 kW", "3 pole pairs · Hall", "Urban Fox scooter donor"],
     "Came with the donor, and is not confirmed on paper. It is the component "
     "the whole model hangs on, so it had to be measured."),
]
for i, (img, name, specs, why) in enumerate(comps):
    cx = x + i * (cw + 0.28)
    d.rect(sl, cx, y, cw, 1.70, B.WHITE, line=B.LINE)
    if "web" in img:
        d.fit(sl, img, cx + 0.06, y + 0.06, cw - 0.12, 1.58)
    else:
        d.img(sl, img, cx + 0.06, y + 0.06, cw - 0.12, 1.58)
    d.text(sl, cx, y + 1.82, cw, 0.26, name, size=13, color=B.BLUE, bold=True,
           align=PP_ALIGN.CENTER)
    d.text(sl, cx + 0.10, y + 2.16, cw - 0.20, 0.66, bullets(specs, size=9.5,
           color=B.INK), line=1.3, space=2)
    d.card(sl, cx, y + 2.90, cw, 1.18, "WHY THIS ONE", [why],
           fill=B.BLUE_LT if i == 1 else B.PANEL, accent=B.BLUE,
           hs=9, bs=9, pad=0.15)

# ==========================================================================
# 07 — Where the limits are
#
# The figure now draws three ceilings, not two. The voltage branch is the one
# that closes the envelope at no-load speed, and it is the honest answer to
# "why does it stop there" — see _figures.envelope().
# ==========================================================================
sl, (x, y, w, h) = d.tall("Where the limits actually are")
fw = 4.86
d.fit(sl, os.path.join(FIG, "fig_envelope.png"), x, y + 0.24, fw, 2.70)
cx = x + fw + 0.34
cw = w - fw - 0.34
rows = [
    ("BATTERY", "40 A  →  1.9 kW", "this is the ceiling", B.RISK, True),
    ("MOTOR", "120 A  →  9.1 N·m", "no thermal protection", B.WARN, False),
    ("VOLTAGE", "0.95 × 48 V", "sets top speed", B.WARN, False),
]
ry = y - 0.04
for name, val, note, col, hot in rows:
    d.rect(sl, cx, ry, cw, 0.76, B.BLUE_LT if hot else B.PANEL)
    d.text(sl, cx + 0.18, ry + 0.10, cw - 0.36, 0.22, name, size=9.5,
           color=B.BLUE if hot else B.GREY, bold=True)
    d.text(sl, cx + 0.18, ry + 0.34, 2.00, 0.26, val, size=12,
           color=B.INK, bold=True)
    d.text(sl, cx + 2.20, ry + 0.36, cw - 2.38, 0.24, note, size=9.5,
           color=col, bold=hot)
    ry += 0.86
d.card(sl, cx, ry + 0.10, cw, 1.24, "WHAT THAT MEANS FOR THE MODEL", [
    "The inverter, 70 A continuous, never shapes this curve — it limits how "
    "long the flat part can be held. The battery gets only what it takes to "
    "set the ceiling: no thermal model, not this year.",
], fill=B.WHITE, accent=B.BLUE, hs=9.5, bs=9.5, pad=0.16)

# ==========================================================================
# 08 — What the model needs
# ==========================================================================
sl, (x, y, w, h) = d.tall("What the model needs, and where it comes from")
fw = 4.30
d.fit(sl, os.path.join(FIG, "fig_equations.png"), x, y + 0.06, fw, 2.90)
d.text(sl, x, y + 3.06, fw, 0.44,
       "Three equations. Every symbol in them is a number someone has to go "
       "and measure.", size=10, color=B.GREY, italic=True, line=1.2)

cx = x + fw + 0.36
cw = w - fw - 0.36
d.text(sl, cx, y - 0.08, cw, 0.24, "MEASURED ON THIS VEHICLE", size=10,
       color=B.BLUE, bold=True)
params = [
    ("p", "3", "Hall pulse count"),
    ("λm", "16.86 mWb", "back-EMF, scope"),
    ("Kt", "0.0758 N·m/A", "derived from p and λm"),
    ("R", "28.0 mΩ", "inverter detection"),
    ("Ld / Lq", "99 / 113 µH", "inverter detection"),
    ("J", "1.56·10⁻⁴ kg·m²", "spin-down"),
    ("T₀ / b", "63 mN·m / 139 µN·m·s/rad", "spin-down"),
]
ry = y + 0.24
for i, (sym, val, how) in enumerate(params):
    if i % 2 == 0:
        d.rect(sl, cx - 0.10, ry - 0.05, cw + 0.10, 0.44, B.PANEL)
    d.text(sl, cx, ry, 0.90, 0.22, sym, size=11, color=B.BLUE, bold=True)
    d.text(sl, cx + 0.94, ry, 1.90, 0.22, val, size=10, color=B.INK, bold=True)
    d.text(sl, cx + 2.90, ry, cw - 2.90, 0.22, how, size=9, color=B.GREY)
    ry += 0.45
d.rect(sl, cx - 0.10, ry + 0.02, cw + 0.10, 0.52, B.BLUE)
d.text(sl, cx, ry + 0.14, cw - 0.20, 0.34,
       "None of this came from a datasheet. The datasheet was wrong.",
       size=10.5, color=B.WHITE, bold=True, anchor=MSO_ANCHOR.TOP)

# ==========================================================================
# 09 — How it was measured
# ==========================================================================
sl, (x, y, w, h) = d.tall("How the machine was measured")
d.fit(sl, os.path.join(FIG, "fig_backemf.png"), x, y - 0.04, w, 2.46)
cw = (w - 2 * 0.24) / 3
cards = [
    ("POLE PAIRS", B.OK, "Counted the Hall pulses over one turn of the "
     "sprocket: 25 against 25.1 predicted for p = 3, and 33.5 for p = 4."),
    ("FLUX LINKAGE", B.OK, "Motor off the inverter, dragged by a drill, scope "
     "across two phases. Two speeds agree to 0.17 %."),
    ("INERTIA AND DRAG", B.OK, "Three spin-downs anchored on the steady "
     "no-load point: J = 1.56·10⁻⁴ kg·m², plus dry and viscous friction."),
]
for i, (hd, col, bd) in enumerate(cards):
    d.card(sl, x + i * (cw + 0.24), y + 2.56, cw, 1.06, hd, [bd],
           fill=B.PANEL, accent=col, hs=9.5, bs=9, pad=0.15)
d.rect(sl, x, y + 3.72, w, 0.40, B.BLUE)
d.text(sl, x + 0.20, y + 3.72, w - 0.40, 0.40,
       "Next: a coast-down on the vehicle — rolling resistance, drag and "
       "vehicle inertia in one test. That is what the straight-line model needs.",
       size=10, color=B.WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ==========================================================================
# 10 — How I learn
#
# One bold claim per column and the scope as chips. The prose that used to sit
# under each claim said the same thing more slowly.
# ==========================================================================
sl, (x, y, w, h) = d.tall("How I learn, and what I refuse to delegate")
cw = (w - 2 * 0.26) / 3
learn = [
    ("DERIVE IT", B.BLUE, B.BLUE_LT,
     "A dragged-in FOC block gives a quad that works and an engineer who "
     "learned nothing.",
     ["Clarke and Park", "the current loop", "vehicle dynamics"]),
    ("COPY IT", B.GREY, B.PANEL,
     "No first principles there, and no shame about it. The budget for "
     "deriving goes where the learning is.",
     ["build systems", "protocols", "drivers", "file formats"]),
    ("LET THE AI FILE IT", B.CYAN, B.PANEL,
     "Never the reasoning. An agent that hands me a conclusion I should have "
     "reached has negative value.",
     ["notes and plots", "traceability", "formatting", "my own slips"]),
]
for i, (hd, col, fill, claim, tags) in enumerate(learn):
    cx = x + i * (cw + 0.26)
    d.rect(sl, cx, y, cw, 2.86, fill)
    d.rect(sl, cx, y, cw, 0.46, col)
    d.text(sl, cx + 0.18, y, cw - 0.36, 0.46, hd, size=11, color=B.WHITE,
           bold=True, anchor=MSO_ANCHOR.MIDDLE)
    d.text(sl, cx + 0.18, y + 0.64, cw - 0.36, 0.86, claim, size=11,
           color=B.INK, bold=True, line=1.24)
    ty = y + 1.66
    for t in tags:
        d.chip(sl, cx + 0.18, ty, t, col)
        ty += 0.27
d.rect(sl, x, y + 3.04, w, 0.58, B.BLUE)
d.text(sl, x + 0.22, y + 3.04, w - 0.44, 0.58,
       "One Git repository holds the measurements, the decisions and the "
       "reasons behind them. Nothing important lives only in my head.",
       size=11, color=B.WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ==========================================================================
# 11 — How the work is organised
# ==========================================================================
sl, (x, y, w, h) = d.tall("How the work is organised")
fw = 4.30
d.fit(sl, os.path.join(FIG, "fig_cycle.png"), x, y + 0.30, fw, 2.30)
cx = x + fw + 0.40
cw = w - fw - 0.40
d.text(sl, cx, y - 0.06, cw, 0.26, "THE 45 MINUTES WITH YOU", size=11,
       color=B.BLUE, bold=True)
agenda = [("5 min", "What I said I would do"),
          ("15 min", "What I did, with data"),
          ("10 min", "What I do not understand"),
          ("10 min", "Does the reasoning hold?"),
          ("5 min", "Goal of the next cycle")]
ry = y + 0.34
for i, (t, lbl) in enumerate(agenda):
    hot = i in (2, 3)
    d.rect(sl, cx, ry, cw, 0.44, B.BLUE_LT if hot else B.PANEL)
    d.text(sl, cx + 0.16, ry, 0.72, 0.44, t, size=10.5,
           color=B.BLUE if hot else B.GREY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    d.text(sl, cx + 0.98, ry, cw - 1.14, 0.44, lbl, size=10.5,
           color=B.INK, bold=hot, anchor=MSO_ANCHOR.MIDDLE)
    ry += 0.52
d.text(sl, cx, ry + 0.06, cw, 0.34,
       "The middle twenty minutes are the point. A review where I only show "
       "what worked wastes two doctorates.",
       size=10, color=B.GREY, italic=True, line=1.2)
d.rect(sl, x, B.FOOT_Y - 0.60, w, 0.46, B.BLUE)
d.text(sl, x + 0.20, B.FOOT_Y - 0.60, w - 0.40, 0.46,
       "If I cannot explain it out loud without notes, the cycle is not "
       "finished.", size=11, color=B.WHITE, bold=True,
       anchor=MSO_ANCHOR.MIDDLE)

# ==========================================================================
# 12 — The plan
#
# The 2027 strip is the answer to "and then what". It comes straight from the
# long horizon in 01_plan/roadmap.md, deliberately as three words each: it is
# direction, not plan, and pretending otherwise would be the exact failure
# mode the roadmap warns about.
# ==========================================================================
sl, (x, y, w, h) = d.tall("The plan to December")
d.fit(sl, os.path.join(FIG, "fig_timeline.png"), x, y - 0.04, w, 2.62)
d.rect(sl, x, y + 2.66, w, 0.50, B.PANEL)
d.text(sl, x + 0.20, y + 2.66, 1.60, 0.50, "AFTER C06  ·  2027", size=9.5,
       color=B.BLUE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
d.text(sl, x + 1.85, y + 2.66, w - 2.05, 0.50,
       "Control on the ESP32   ·   Traction and launch control   ·   "
       "MPC on a validated model",
       size=10.5, color=B.INK, anchor=MSO_ANCHOR.MIDDLE)
d.rect(sl, x, y + 3.24, w, 0.70, B.BLUE_LT)
d.text(sl, x + 0.22, y + 3.34, w - 0.44, 0.52, [
    {"t": "End of 2026: a model validated against the real vehicle.",
     "size": 12.5, "color": B.BLUE, "bold": True},
    {"t": "The machine came in ahead of plan, so C01 moves on to the vehicle.",
     "size": 10, "color": B.INK},
], line=1.25, space=4)

# ==========================================================================
# 13 — What I need from you
# ==========================================================================
sl, (x, y, w, h) = d.dark("What I need from you")
d.text(sl, x, y - 0.06, w, 0.30,
       "Three things. They are worth more to me than technical answers.",
       size=12.5, color=B.CYAN)
asks = [
    ("01", "Hold me to a date",
     "Without an external deadline I postpone indefinitely. The date being "
     "fixed is the mechanism — the meeting itself is secondary."),
    ("02", "Attack the reasoning, not the result",
     "Do not ask whether the number is right. Ask why I chose that method, "
     "and what would have to be true for it to be wrong."),
    ("03", "Tell me when I explain badly",
     "If an explanation does not land, that is usually not a language "
     "problem. It is me not having understood it."),
]
ry = y + 0.40
for num, hd, bd in asks:
    d.text(sl, x, ry - 0.04, 0.70, 0.44, num, size=24, color=B.CYAN, bold=True)
    d.text(sl, x + 0.82, ry - 0.02, w - 0.82, 0.28, hd, size=14,
           color=B.WHITE, bold=True)
    d.text(sl, x + 0.82, ry + 0.30, w - 0.82 - 0.20, 0.44, bd, size=10.5,
           color=B.BLUE_LT, line=1.25)
    ry += 0.94
d.rect(sl, x, ry + 0.06, w, 0.74, B.BLUE)
d.text(sl, x + 0.22, ry + 0.06, w - 0.44, 0.74,
       "What I am not asking for: that you validate field-oriented control or "
       "electric-machine theory. That gap I close elsewhere — you are not being "
       "examined on a domain that is not yours.",
       size=10.5, color=B.WHITE, anchor=MSO_ANCHOR.MIDDLE, line=1.25)

# ==========================================================================
# 14 — Close
# ==========================================================================
sl, (x, y, w, h) = d.std("What I am asking for today", "strip_field.jpg")
cw = (w - 2 * 0.24) / 3
for i, (big, lbl, sub) in enumerate([
    ("12 Oct", "First full review", "C01 — closing the vehicle side"),
    ("Every 2 weeks", "Cadence", "Monday, 45 minutes, six reviews to December"),
    ("3 of 3", "Machine parameters measured",
     "pole pairs · flux linkage · inertia"),
]):
    cx = x + i * (cw + 0.24)
    d.rect(sl, cx, y - 0.10, cw, 1.72, B.PANEL if i else B.BLUE_LT)
    d.text(sl, cx + 0.20, y + 0.10, cw - 0.40, 0.46, big,
           size=22 if i != 1 else 17, color=B.BLUE, bold=True)
    d.text(sl, cx + 0.20, y + 0.74, cw - 0.40, 0.30, lbl, size=11.5,
           color=B.INK, bold=True)
    d.text(sl, cx + 0.20, y + 1.10, cw - 0.40, 0.44, sub, size=9.5,
           color=B.GREY, line=1.2)
d.rect(sl, x, y + 1.82, w, 0.70, B.BLUE_DK)
d.text(sl, x + 0.22, y + 1.82, w - 0.44, 0.70,
       "Confirm the slot, and I will put all six review dates in the calendar "
       "before I leave.", size=12.5, color=B.WHITE, bold=True,
       anchor=MSO_ANCHOR.MIDDLE)

print("slides:", d.n)
print("saved:", d.save(OUT))
