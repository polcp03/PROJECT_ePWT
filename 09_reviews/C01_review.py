"""C01 — Review deck. The longitudinal model, built before the vehicle data.

Content is English (public/technical, per CLAUDE.md). Parameters are parsed
from 04_model/params/*.m and predictions from 04_model/results/*.csv, so no
number on a slide can drift from the repo. Structure agreed with Pol on
2026-10-09 (see C01-feedback.md).

    ./.venv/Scripts/python.exe 09_reviews/_figures_c01.py
    ./.venv/Scripts/python.exe 09_reviews/C01_review.py
    ./.venv/Scripts/python.exe 09_reviews/_check.py 09_reviews/C01-review.pptx
"""
from __future__ import annotations

import csv
import math
import os
import re
import sys

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _brand as B
from _deck import CROP, FIG, ROOT, Deck

OUT = os.path.join(HERE, "C01-review.pptx")
RES = os.path.join(ROOT, "04_model", "results")
PAR = os.path.join(ROOT, "04_model", "params")
MATH = "Cambria Math"


# --- parameters, parsed from the .m files --------------------------------
def params(fname):
    out = {}
    pat = re.compile(r"^(\w+)\.(\w+)\s*=\s*(-?[\d.]+(?:e-?\d+)?)\s*;")
    for line in open(os.path.join(PAR, fname), encoding="utf-8"):
        m = pat.match(line.strip())
        if m:
            out[f"{m.group(1)}.{m.group(2)}"] = float(m.group(3))
    return out


P = {**params("motor_params.m"), **params("vehicle_params.m"),
     **params("throttle_params.m")}
m_total = P["veh.m_vehicle"] + P["veh.m_driver"]
i_gear = P["veh.z_wheel"] / P["veh.z_motor"]
r = P["veh.r_roll"]
g = P["veh.g"]
m_rotor = P["mot.J"] * i_gear ** 2 / r ** 2
m_eq = m_total + P["veh.m_rot_wheels"] + m_rotor
T_max = 1.5 * P["mot.p"] * P["mot.lambda_m"] * P["lim.i_motor_max"]
F_roll = P["veh.Crr"] * m_total * g
F_aero30 = 0.5 * P["veh.rho_air"] * P["veh.CdA"] * (30 / 3.6) ** 2
F_grip = P["veh.mu"] * P["veh.x_cg"] * m_total * g
V_FET = 0.9486 * 52.77 / math.sqrt(3)       # C00 no-load point, motor_params.m


# --- model outputs ----------------------------------------------------------
def rows(name):
    with open(os.path.join(RES, name), newline="") as f:
        return list(csv.DictReader(f))


OAT = {rw["param"]: rw for rw in rows("C01_oat.csv")}
fl = lambda s: float(s) if s not in ("", "NaN") else float("nan")  # noqa: E731
NOM = {k: fl(v) for k, v in OAT["NOMINAL"].items() if k != "param"}


def band(key):
    s = 0.0
    for p, rw in OAT.items():
        if p in ("NOMINAL", "V_oc", "V_BATLIM"):
            continue
        s += max(abs(fl(rw[key + "_lo"]) - NOM[key + "_lo"]),
                 abs(fl(rw[key + "_hi"]) - NOM[key + "_lo"])) ** 2
    return s ** 0.5


table = open(os.path.join(RES, "C01_predictions_table.md"), encoding="utf-8").read()
mb = re.search(r"battery limit kicks in \[km/h\] \| ([\d.]+) \| \+/- ([\d.]+)", table)
mc = re.search(r"Crr \((\d+) % of variance\)", table.split("Coast-down")[1])
V_BATLIM, V_BATLIM_B = float(mb.group(1)), float(mb.group(2))
CRR_SHARE = int(mc.group(1))
mt = re.search(r"Time 0-25 km/h \[s\] \|[^|]*\|[^|]*\| (\w+) \((\d+) % of variance\)", table)
T025_DOM, T025_SHARE = mt.group(1), int(mt.group(2))
RPM_MODEL, RPM_MEAS = 16343 / P["mot.p"], 16440 / P["mot.p"]
VTOP, VTOP_B = NOM["vtop_lo"], band("vtop")
T025, T025_B = NOM["t025_lo"], band("t025")
TCST, TCST_B = NOM["tcst_lo"], band("tcst")
VOC_LO, VOC_HI = fl(OAT["V_oc"]["vtop_lo"]), fl(OAT["V_oc"]["vtop_hi"])
ENV = rows("C01_envelope.csv")
_env = sorted((fl(e["v_kmh"]), fl(e["F_wheel"])) for e in ENV)
F_WHEEL_MAX = next(f for v_, f in _env if v_ >= 5.0)     # motor-limited plateau, drag included
P_BAT = (50.0 - P["bat.R_int"] * P["lim.i_batt_max"]) * P["lim.i_batt_max"]
CS = rows("C01_coast_start.csv")
CDA_GAIN = fl(CS[-1]["dt_CdA"]) / fl(CS[0]["dt_CdA"])
CS_LO, CS_HI = fl(CS[0]["v_start_kmh"]), fl(CS[-1]["v_start_kmh"])

d = Deck("OFF-ROAD EV PLATFORM  ·  C01 review  ·  October 2026")


def chip_row(sl, x, y, labels, color, gap=0.08):
    for t in labels:
        c = d.chip(sl, x, y, t, color, w=0.22 + 0.068 * len(t))
        x += c.width / 914400 + gap
    return x


def band_note(sl, x, w, txt, fill=B.BLUE):
    d.rect(sl, x, B.FOOT_Y - 0.56, w, 0.42, fill)
    d.text(sl, x + 0.20, B.FOOT_Y - 0.56, w - 0.40, 0.42, txt, size=11,
           color=B.WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)


def step(sl, x, y, w, h, txt, fill, tc=B.INK, bold=True):
    d.rect(sl, x, y, w, h, fill)
    d.text(sl, x, y, w, h, txt, size=11, color=tc, bold=bold,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ==========================================================================
# 01 — Cover
d.cover(os.path.join(CROP, "c01_cover.jpg"),
        "LONGITUDINAL\nMODEL",
        "Level 1 of the digital twin — built before the vehicle could be measured",
        "C01 REVIEW\nPOL CRUAÑAS  ·  9 OCTOBER 2026")

# ==========================================================================
# 02 — Why a model before the data
sl, (x, y, w, h) = d.split("Why a model before the data",
                           os.path.join(CROP, "c01_tyre.jpg"), side="left", frac=0.32)
d.text(sl, x, y - 0.10, w, 0.60,
       "The coast-down could not run: both tyres punctured, and the "
       "logger's ESP32 was lost to a ground loop.",
       size=13, color=B.INK, bold=True, line=1.2)
sw, ar = 1.55, 0.30
for row, (lbl, steps, fills) in enumerate([
    ("C01 PLAN · SEPTEMBER", ["measure", "fit", "model"], [B.PANEL] * 3),
    ("DONE · AFTER THE PIVOT", ["model", "predict + freeze", "measure → C02"],
     [B.BLUE_LT, B.BLUE_LT, B.PANEL]),
]):
    ry = y + 0.95 + row * 1.10
    d.text(sl, x, ry, w, 0.22, lbl, size=9.5,
           color=B.GREY if row == 0 else B.BLUE, bold=True)
    for k, (s_, f_) in enumerate(zip(steps, fills)):
        sx = x + k * (sw + ar)
        step(sl, sx, ry + 0.26, sw, 0.50, s_, f_,
             tc=B.GREY if row == 0 else B.BLUE)
        if k < 2:
            d.text(sl, sx + sw, ry + 0.26, ar, 0.50, "→", size=16,
                   color=B.GREY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
band_note(sl, x, w, "Written down first, so the test can prove it wrong.")

# ==========================================================================
# 03 — The model
sl, (x, y, w, h) = d.tall("The model: four blocks, one state")
d.fit(sl, os.path.join(FIG, "fig_c01_model.png"), x, y - 0.08, w, 2.95)
d.text(sl, x, y + 2.88, 6.0, 0.24, "SANITY CHECK · MOTOR ONLY, WHEELS IN THE AIR", size=9.5,
       color=B.BLUE, bold=True)
cw = (w - 2 * 0.20) / 3
for k, (big, lbl, fill) in enumerate([
    (f"{RPM_MODEL:.0f} rpm", "model, wheels in the air, 52.77 V", B.PANEL),
    (f"{RPM_MEAS:.0f} rpm", "measured, C00 no-load (16 440 ERPM ÷ 3)", B.PANEL),
    ("−0.6 %", "λm + voltage ceiling + drag — not the vehicle", B.BLUE_LT),
]):
    sx = x + k * (cw + 0.20)
    d.rect(sl, sx, y + 3.14, cw, 0.70, fill)
    d.text(sl, sx + 0.16, y + 3.17, cw - 0.32, 0.34, big, size=15,
           color=B.BLUE, bold=True)
    d.text(sl, sx + 0.16, y + 3.50, cw - 0.32, 0.30, lbl, size=8.5,
           color=B.GREY)

# ==========================================================================
# 03b — The same model in Simulink
# ==========================================================================
sl, (x, y, w, h) = d.tall("The same model in Simulink (L1)")
d.fit(sl, os.path.join(RES, "C01_model_L1.png"), x - 0.2, y - 0.10, w + 0.4, 3.60)
d.text(sl, x, B.FOOT_Y - 0.30, w, 0.22,
       "Built by script (build_longitudinal_L1.m): every block and wire is "
       "text in Git. L2 = same physics in 4 subsystems, identical output.",
       size=9, color=B.GREY)

# ==========================================================================
# 04 — The force balance, with numbers
sl, (x, y, w, h) = d.tall("The force balance, with numbers")
d.rect(sl, x, y - 0.04, w, 0.56, B.BLUE_LT)
d.text(sl, x, y - 0.04, w, 0.56,
       "m_eq · dv/dt  =  F_wheel  −  F_roll  −  F_aero",
       size=19, color=B.BLUE, bold=True, align=PP_ALIGN.CENTER,
       anchor=MSO_ANCHOR.MIDDLE, font=MATH)
cols = [1.25, 2.55, 1.55, 3.41]
hdr = ["TERM", "LAW", "VALUE", "INPUTS"]
cx = x
for j, hd in enumerate(hdr):
    d.text(sl, cx + 0.14, y + 0.62, cols[j], 0.22, hd, size=8.5, color=B.GREY,
           bold=True)
    cx += cols[j]
table_rows = [
    ("F_wheel", "T · i · η / r_roll", f"≤ {F_WHEEL_MAX:.0f} N",
     f"i = {i_gear:.2f} · η = {P['veh.eta_drive']:.2f} · r = {r:.3f} m"),
    ("F_roll", "Crr · m · g", f"{F_roll:.0f} N",
     f"Crr = {P['veh.Crr']:.3f} · m = {m_total:.0f} kg"),
    ("F_aero", "½ · ρ · CdA · v²", f"{F_aero30:.0f} N at 30 km/h",
     f"CdA = {P['veh.CdA']:.2f} m² · ρ = {P['veh.rho_air']:.2f} kg/m³"),
    ("grip", "μ · N_rear", f"{F_grip:.0f} N",
     f"μ = {P['veh.mu']:.2f} (dirt) · rear share {P['veh.x_cg']:.2f}"),
    ("m_eq", "m + J_wheels/r² + J_rotor·i²/r²", f"{m_eq:.1f} kg",
     f"{m_total:.0f} + {P['veh.m_rot_wheels']:.0f} wheels (ASSUMED) + {m_rotor:.2f} rotor (MEASURED)"),
]
ry = y + 0.90
for k, (t_, law, val, inp) in enumerate(table_rows):
    d.rect(sl, x, ry, w, 0.44, B.PANEL if k % 2 == 0 else B.WHITE)
    cx = x
    for j, (txt, sz, col, bold, font) in enumerate([
        (t_, 12, B.BLUE, True, None), (law, 12, B.INK, False, MATH),
        (val, 12, B.INK, True, None), (inp, 9.5, B.GREY, False, None)]):
        d.text(sl, cx + 0.14, ry, cols[j] - 0.20, 0.44, txt, size=sz,
               color=col, bold=bold, anchor=MSO_ANCHOR.MIDDLE, font=font)
        cx += cols[j]
    ry += 0.46
band_note(sl, x, w, "At top speed, rolling and aero are about equal. "
          "Below it, rolling resistance dominates.")

# ==========================================================================
# 05 — Where every number comes from
sl, (x, y, w, h) = d.tall("Where every number comes from")
groups = [
    ("MEASURED", B.OK, [
        ("pole pairs", f"{P['mot.p']:.0f}", "Hall count"),
        ("flux linkage λm", f"{P['mot.lambda_m']*1e3:.1f} mWb", "scope, 3 methods"),
        ("rotor drag", f"{P['mot.T_coulomb']*1e3:.0f} mN·m", "spin-down, + viscous"),
        ("masses", f"{P['veh.m_vehicle']:.0f} + {P['veh.m_driver']:.0f} kg", "scale"),
        ("gear", f"{P['veh.z_wheel']:.0f}/{P['veh.z_motor']:.0f}", "teeth counted"),
    ]),
    ("VESC ESTIMATE", B.WARN, [
        ("phase resistance", f"{P['mot.Rs']*1e3:.0f} mΩ", "detection, 3 runs"),
        ("inductance", f"{P['mot.L_avg']*1e6:.0f} µH", "detection, 3 runs"),
    ]),
    ("CONFIG", B.RISK, [
        ("motor current", f"{P['lim.i_motor_max']:.0f} A", "typed in VESC"),
        ("battery current", f"{P['lim.i_batt_max']:.0f} A", "= BMS rating"),
        ("max duty", f"{P['lim.duty_max']:.2f}", "typed in VESC"),
        ("throttle ramp", f"{P['thr.ramp_time_pos']:.1f} s", "typed in VESC"),
    ]),
    ("ASSUMED", B.GREY, [
        ("rolling radius", f"{r:.3f} m", "13 in, −6 % squash"),
        ("Crr", f"{P['veh.Crr']:.3f}", "soft knobby tyre"),
        ("CdA", f"{P['veh.CdA']:.2f} m²", "upright rider"),
        ("grip μ", f"{P['veh.mu']:.2f}", "dirt, no tyre data"),
        ("chain η", f"{P['veh.eta_drive']:.2f}", "roller chain"),
        ("pack R_int", f"{P['bat.R_int']:.2f} Ω", "no datasheet"),
    ]),
]
gw = (w - 3 * 0.16) / 4
for gi, (tag, col, items) in enumerate(groups):
    gx = x + gi * (gw + 0.16)
    d.rect(sl, gx, y - 0.04, gw, 0.30, col)
    d.text(sl, gx, y - 0.04, gw, 0.30, tag, size=10, color=B.WHITE, bold=True,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    for k, (nm, val, why) in enumerate(items):
        iy = y + 0.32 + k * 0.52
        d.rect(sl, gx, iy, gw, 0.46, B.PANEL)
        d.rect(sl, gx, iy, 0.05, 0.46, col)
        d.text(sl, gx + 0.14, iy + 0.04, gw - 0.20, 0.20, nm, size=8.5,
               color=B.GREY)
        d.text(sl, gx + 0.14, iy + 0.21, 0.95, 0.22, val, size=10.5,
               color=B.INK, bold=True)
        d.text(sl, gx + 1.00, iy + 0.23, gw - 1.06, 0.20, why, size=7.5,
               color=B.GREY, align=PP_ALIGN.RIGHT)
band_note(sl, x, w, "Every ASSUMED value carries a range. "
          "The sensitivity sweep runs over exactly those ranges.")

# ==========================================================================
# 06 — Where the limits are
sl, (x, y, w, h) = d.tall("Where the limits are")
fw = 5.45
d.fit(sl, os.path.join(FIG, "fig_c01_envelope.png"), x - 0.05, y - 0.06, fw, 3.30)
cx, cw = x + fw + 0.12, w - fw - 0.12
lims = [
    ("MOTOR CURRENT", B.BLUE, f"iq ≤ {P['lim.i_motor_max']:.0f} A",
     f"T = 3/2·p·λm·iq = {T_max:.1f} N·m"),
    ("BATTERY CURRENT", B.RISK, f"I_bat ≤ {P['lim.i_batt_max']:.0f} A",
     f"≈ {P_BAT/1e3:.1f} kW, from {V_BATLIM:.0f} km/h"),
    ("VOLTAGE", B.WARN, "|v| ≤ 0.95 · V_bat / √3",
     f"C00 check: {V_FET:.1f} V reached"),
]
for k, (nm, col, law, note) in enumerate(lims):
    iy = y - 0.04 + k * 1.10
    d.rect(sl, cx, iy, cw, 1.00, B.PANEL)
    d.rect(sl, cx, iy, 0.06, 1.00, col)
    d.text(sl, cx + 0.18, iy + 0.08, cw - 0.26, 0.22, nm, size=9, color=col,
           bold=True)
    d.text(sl, cx + 0.18, iy + 0.34, cw - 0.26, 0.30, law, size=12.5,
           color=B.INK, bold=True, font=MATH)
    d.text(sl, cx + 0.18, iy + 0.68, cw - 0.26, 0.24, note, size=9,
           color=B.GREY)
band_note(sl, x, w, f"On dirt the tyre limits the launch ({F_grip:.0f} N < "
          f"{F_WHEEL_MAX:.0f} N). From {V_BATLIM:.0f} km/h: the battery. At the top: voltage.")

# ==========================================================================
# 06b — Motor current is not battery current
# ==========================================================================
sl, (x, y, w, h) = d.tall("Motor current is not battery current")
fw = 6.0
d.fit(sl, os.path.join(FIG, "fig_c01_currents.png"), x - 0.05, y - 0.08, fw, 3.50)
cx, cw = x + fw + 0.15, w - fw - 0.15
for k, (hd, txt, col) in enumerate([
    ("POWER IS CONSERVED", "V_bat · I_bat ≈ 3/2 · v_q · iq. Low speed → low motor voltage → "
     "120 A of motor is little battery current.", B.BLUE),
    (f"FROM {V_BATLIM:.0f} KM/H", f"The battery reaches {P['lim.i_batt_max']:.0f} A. "
     "The VESC cuts iq so it stays there: constant power.", B.RISK),
    ("NEAR THE TOP", "The back-EMF reaches the voltage the inverter can make. "
     "No voltage left to push current: iq collapses.", B.WARN),
]):
    iy = y - 0.04 + k * 1.12
    d.rect(sl, cx, iy, cw, 1.04, B.PANEL)
    d.rect(sl, cx, iy, 0.06, 1.04, col)
    d.text(sl, cx + 0.18, iy + 0.06, cw - 0.26, 0.22, hd, size=9, color=col, bold=True)
    d.text(sl, cx + 0.18, iy + 0.30, cw - 0.26, 0.70, txt, size=9.5, color=B.INK,
           line=1.1)

# ==========================================================================
# 07 — Predictions
sl, (x, y, w, h) = d.tall("Predictions, frozen before the test")
cw = (w - 3 * 0.16) / 4
for k, (big, lbl) in enumerate([
    (f"{VTOP:.1f} ± {VTOP_B:.1f} km/h", "top speed, at 50 V"),
    (f"{T025:.1f} ± {T025_B:.1f} s", "0 → 25 km/h, full throttle"),
    (f"{TCST:.1f} ± {TCST_B:.1f} s", "coast-down 30 → 5 km/h"),
    (f"{V_BATLIM:.1f} ± {V_BATLIM_B:.1f} km/h", "where the 40 A limit starts"),
]):
    sx = x + k * (cw + 0.16)
    d.rect(sl, sx, y - 0.04, cw, 0.78, B.BLUE_LT if k < 3 else B.PANEL)
    d.text(sl, sx + 0.12, y + 0.02, cw - 0.24, 0.36, big, size=14,
           color=B.BLUE, bold=True)
    d.text(sl, sx + 0.12, y + 0.42, cw - 0.24, 0.26, lbl, size=9,
           color=B.GREY)
d.fit(sl, os.path.join(FIG, "fig_c01_runs.png"), x, y + 0.84, w, 2.82)
d.text(sl, x, B.FOOT_Y - 0.30, w, 0.22,
       "Two simulated manoeuvres. Shaded: every parameter at the ends of its "
       "range, one at a time.", size=9, color=B.GREY)

# ==========================================================================
# 08 — What moves the predictions
sl, (x, y, w, h) = d.tall("What moves the predictions")
d.fit(sl, os.path.join(FIG, "fig_c01_tornado.png"), x, y - 0.06, w, 2.70)
cw2 = (w - 2 * 0.20) / 3
for k, (hd, claim, col) in enumerate([
    ("TOP SPEED", f"Pack voltage moves it {VOC_LO:.0f}–{VOC_HI:.0f} km/h. "
     "Measure V_bat first.", B.PANEL),
    ("0 → 25 KM/H", f"Grip μ is {T025_SHARE} % of the spread. "
     "On dirt the tyre, not the motor.", B.PANEL),
    ("COAST-DOWN", f"Crr is {CRR_SHARE} % of the spread. "
     "The first thing to measure.", B.BLUE_LT),
]):
    sx = x + k * (cw2 + 0.20)
    d.rect(sl, sx, y + 2.74, cw2, 0.90, col)
    d.text(sl, sx + 0.18, y + 2.80, cw2 - 0.36, 0.22, hd, size=9.5,
           color=B.BLUE, bold=True)
    d.text(sl, sx + 0.18, y + 3.06, cw2 - 0.36, 0.52, claim, size=11.5,
           color=B.INK, bold=True, line=1.15)
d.text(sl, x, B.FOOT_Y - 0.30, w, 0.22,
       "* pack voltage is a test condition, not an unknown — it is measured, "
       "so it stays out of the band.", size=9, color=B.GREY)

# ==========================================================================
# 09 — Designing the tests
sl, (x, y, w, h) = d.tall("Designing the tests")
fw = 3.95
d.fit(sl, os.path.join(FIG, "fig_c01_coast_start.png"), x - 0.05, y - 0.06, fw, 2.65)
d.text(sl, x, y + 2.62, fw, 0.62,
       f"Start the coast-down as high as the quad reaches: CdA shows "
       f"{CDA_GAIN:.0f}× more at {CS_HI:.0f} than at {CS_LO:.0f} km/h — "
       "still small next to Crr.", size=10.5, color=B.INK, bold=True, line=1.2)
cx, cw = x + fw + 0.25, w - fw - 0.25
runs_ = [
    ("RUN 1 · FULL THROTTLE, 0 → TOP SPEED", B.BLUE,
     f"Checks: top speed · 0 → 25 km/h · battery limit at {V_BATLIM:.0f} km/h",
     "GPS + VESC log · V_bat before"),
    ("RUN 2 · COAST-DOWN, 30 → 5 KM/H", B.CYAN,
     "Checks: coast time. Then fits Crr (CdA only weakly)",
     "VESC log: speed vs time"),
]
for k, (hd, col, chk, inst) in enumerate(runs_):
    iy = y - 0.04 + k * 1.40
    d.rect(sl, cx, iy, cw, 1.28, B.PANEL)
    d.rect(sl, cx, iy, 0.06, 1.28, col)
    d.text(sl, cx + 0.18, iy + 0.08, cw - 0.26, 0.24, hd, size=10, color=col, bold=True)
    d.text(sl, cx + 0.18, iy + 0.40, cw - 0.26, 0.50, chk, size=11, color=B.INK,
           bold=True, line=1.1)
    d.text(sl, cx + 0.18, iy + 0.92, cw - 1.30, 0.26, inst, size=9.5, color=B.GREY)
    chip_row(sl, cx + cw - 1.60, iy + 0.92, ["tyres", "logger"], B.WARN)
band_note(sl, x, w, "Every run in both directions: slope and wind cancel "
          "in the average.")

# ==========================================================================
# 10 — In the model, next, and the question for the room
# ==========================================================================
sl, (x, y, w, h) = d.tall("What is in the model, and what is next")
d.text(sl, x, y - 0.06, w, 0.34,
       "Level 1 answers “how fast, how quick”. It cannot answer “how much does it slip”.",
       size=13, color=B.INK, bold=True)
cols3 = [
    ("IN NOW · LEVEL 1", B.BLUE, ["force balance + grip cap", "3 limits on iq",
                                  "rotor drag", "throttle ramp", "pack R_int sag"]),
    ("NEXT · TYRES + LEVEL 2", B.CYAN, ["new tyres → check predictions",
                                       "load transfer (needs h_cg)",
                                       "launch-control hook",
                                       "tyre pressure → Crr"]),
    ("C02 · MOTOR + INVERTER", B.BLUE_DK, ["dq machine: Clarke, Park",
                                           "current loop", "inverter losses",
                                           "temperature"]),
]
cw = (w - 2 * 0.22) / 3
for k, (hd, col, items) in enumerate(cols3):
    sx = x + k * (cw + 0.22)
    d.rect(sl, sx, y + 0.36, cw, 0.34, col)
    d.text(sl, sx + 0.16, y + 0.36, cw - 0.32, 0.34, hd, size=10.5,
           color=B.WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    d.rect(sl, sx, y + 0.70, cw, 2.02, B.PANEL)
    for j, it in enumerate(items):
        d.text(sl, sx + 0.18, y + 0.80 + j * 0.37, cw - 0.36, 0.30,
               "—  " + it, size=11, color=B.INK)
d.text(sl, x, y + 2.80, 0.60, 0.26, "2027", size=9.5, color=B.GREY, bold=True,
       anchor=MSO_ANCHOR.MIDDLE)
chip_row(sl, x + 0.62, y + 2.82, ["traction control", "launch control", "MPC"],
         B.BLUE_DK)
band_note(sl, x, w, f"For you: {P['lim.i_motor_max']:.0f} A motor and "
          f"{P['lim.i_batt_max']:.0f} A battery were typed in. How would you derive them?",
          fill=B.BLUE_DK)

# ==========================================================================
# Speaker notes: the likely question per slide (exam block H). Questions only,
# never the answer - the answer is Pol's. Notes do not reach the PDF.
NOTES = {
    2: "Why didn't you wait for tyres? Calibrating vs validating: what is the difference?",
    3: "Why a single integrator? What does the −0.6 % validate and what does it NOT?",
    4: "What does the MATLAB block do? What is the Memory on I_bat for?",
    5: "Why is rolling constant and aero growing with v²? Why is m_eq not just the mass?",
    6: "Of the ASSUMED ones, which worries you most? Where does μ = 0.60 come from?",
    7: "What happens from 9 km/h? Why does it collapse near 35 km/h? If it spins, does the model see it?",
    8: "Why is the battery current lower than the motor current at low speed?",
    9: "How does the ± band come out? Simulations or hand calculations?",
    10: "Why doesn't the pack voltage enter the band? Why does μ rule the 0→25?",
    11: "Why from 30 and not from 15 km/h? Why there and back?",
    12: "G10: your rule says 'don't skip levels'. Why motor + inverter without validating the vehicle?",
}
for n, q in NOTES.items():
    d.prs.slides[n - 1].notes_slide.notes_text_frame.text = "PREGUNTA PROBABLE: " + q

print("slides:", d.n)
print("saved:", d.save(OUT))
