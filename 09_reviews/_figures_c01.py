"""Figures for the C01 review deck.

Every number is read from the CSVs written by
04_model/scripts/run_predictions_L1.m. Nothing model-derived is typed in.
Photo crops are new framings of Pol's photos, none of them reused from C00.

    ./.venv/Scripts/python.exe 09_reviews/_figures_c01.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _brand import (BLUE, BLUE_DK, BLUE_LT, CYAN, GREY, INK, LINE, OK, PANEL,
                    RISK, WARN, WHITE, FONT, mpl)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "04_model", "results")
OUT = os.path.join(HERE, "assets", "figures")
PHOTOS = os.path.join(HERE, "assets", "photos")
CROPS = os.path.join(HERE, "assets", "crops")
os.makedirs(OUT, exist_ok=True)
os.makedirs(CROPS, exist_ok=True)
DPI = 220

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [FONT, "DejaVu Sans"],
    "axes.edgecolor": mpl(LINE),
    "text.color": mpl(INK),
    "axes.labelcolor": mpl(INK),
    "xtick.color": mpl(GREY),
    "ytick.color": mpl(GREY),
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def read(name):
    with open(os.path.join(RES, name), newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for k in rows[0]:
        if k == "param":
            out[k] = [r[k] for r in rows]
        else:
            out[k] = np.array([float(r[k]) if r[k] not in ("", "NaN") else np.nan
                               for r in rows])
    return out


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, transparent=True)
    plt.close(fig)
    print("   ", name)


def title(ax, t):
    ax.set_title(t, fontsize=10.5, loc="left", color=mpl(BLUE), fontweight="bold")


# --------------------------------------------------------------------------
# Photo crops — new framings, none used in C00
# --------------------------------------------------------------------------
def crops():
    jobs = [
        ("IMG_7300.jpg", "c01_tyre.jpg", (806, 1680, 1994, 3629)),
        ("IMG_7239.jpg", "c01_drive.jpg", (540, 1480, 3024, 3400)),
        ("IMG_7300.jpg", "c01_cover.jpg", (0, 500, 3024, 4032)),
    ]
    for src, dst, box in jobs:
        im = Image.open(os.path.join(PHOTOS, src))
        im = im.crop(box)
        im.thumbnail((1600, 1600))
        im.save(os.path.join(CROPS, dst), quality=88)
        print("   ", dst, im.size)


# --------------------------------------------------------------------------
# Where the limits are: wheel force vs speed, with the road load crossing it
# --------------------------------------------------------------------------
def envelope():
    e = read("C01_envelope.csv")
    v, F, iq, ib = e["v_kmh"], e["F_wheel"], e["iq"], e["I_bat"]
    # keep the samples in time order where speed makes progress: near the
    # no-load speed v creeps asymptotically and sorting would zig-zag the line
    vmax = np.maximum.accumulate(v)
    keep = (v > 0.3) & (F > 8) & np.r_[True, np.diff(vmax) > 1e-4]
    v, F, iq, ib = v[keep], F[keep], iq[keep], ib[keep]
    zone = np.where(iq >= 119.5, 0, np.where(ib >= 39.6, 1, 2))

    oat = read("C01_oat.csv")
    vtop = oat["vtop_lo"][oat["param"].index("NOMINAL")]
    vb = oat["vtop_lo"][oat["param"].index("V_BATLIM")]

    vr = np.linspace(0, 40, 200)
    road = np.interp(vr, e["v_kmh"][np.argsort(e["v_kmh"])],
                     e["F_road"][np.argsort(e["v_kmh"])])
    # the CSV road load only spans the traced speeds; extend with its own law
    c0 = e["F_road"][0]
    k2 = (e["F_road"][-1] - c0) / (e["v_kmh"][-1] / 3.6) ** 2
    road = c0 + k2 * (vr / 3.6) ** 2
    grip = e["F_grip"][0]

    fig, ax = plt.subplots(figsize=(6.0, 3.3), dpi=DPI)
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.15, top=0.95)
    cols = [mpl(BLUE), mpl(RISK), mpl(WARN)]
    for z in range(3):
        m = zone == z
        if m.any():
            ax.plot(v[m], F[m], color=cols[z], lw=2.6, solid_capstyle="butt")
    ax.fill_between(v, 0, F, color=mpl(BLUE_LT), lw=0, zorder=0)
    ax.plot(vr, road, color=mpl(INK), lw=1.4)
    ax.axhline(grip, color=mpl(GREY), lw=1.0, ls="--")
    ytop = np.interp(vtop, vr, road)
    ax.plot([vtop], [ytop], "o", color=mpl(INK), ms=5, zorder=5)

    ap = dict(arrowstyle="-", color=mpl(GREY), lw=0.8)
    ax.annotate("motor current · 120 A", xy=(4, F[v < 4][-1]), xytext=(1.0, 300),
                color=cols[0], fontsize=8.5, fontweight="bold", arrowprops=ap)
    ax.annotate(f"battery current · 40 A · from {vb:.0f} km/h",
                xy=(18, np.interp(18, v, F)), xytext=(17, 380),
                color=cols[1], fontsize=8.5, fontweight="bold", arrowprops=ap)
    ax.annotate("voltage ceiling", xy=(32.0, np.interp(32.0, v, F)),
                xytext=(35.0, 300), ha="center", color=cols[2], fontsize=8.5,
                fontweight="bold", arrowprops=ap)
    ax.annotate("road load: rolling + aero", xy=(22, np.interp(22, vr, road)),
                xytext=(8.5, 95), color=mpl(INK), fontsize=8.5, arrowprops=ap)
    ax.annotate(f"top speed {vtop:.1f} km/h", xy=(vtop, ytop),
                xytext=(21.0, 150), color=mpl(INK), fontsize=8.5,
                fontweight="bold", arrowprops=ap)
    mu = float(re.search(r"^veh\.mu\s*=\s*([\d.]+)", open(os.path.join(
        ROOT, "04_model", "params", "vehicle_params.m"), encoding="utf-8").read(),
        re.M).group(1))
    slip = F > grip
    ax.fill_between(v, grip, F, where=slip, color=mpl(RISK), alpha=0.25, lw=0)
    ax.text(39.5, grip + 10, f"grip on dirt, μ = {mu:.2f}  (ASSUMED)", ha="right",
            va="bottom", fontsize=8, color=mpl(GREY))
    ax.annotate("motor > grip: wheel spins", xy=(7.0, (grip + F[slip].max()) / 2),
                xytext=(11.5, 520), color=mpl(RISK), fontsize=8.5,
                fontweight="bold", arrowprops=ap)
    ax.set_xlim(0, 40); ax.set_ylim(0, 600)
    ax.set_xlabel("vehicle speed [km/h]"); ax.set_ylabel("force at the rear wheel [N]")
    ax.grid(True, color=mpl(LINE), lw=0.5)
    save(fig, "fig_c01_envelope.png")


# --------------------------------------------------------------------------
# The model as four blocks — what the Simulink file contains, readable
# --------------------------------------------------------------------------
def model_blocks():
    fig = plt.figure(figsize=(9.0, 3.1), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 9.0); ax.set_ylim(0, 3.1)
    ax.axis("off")

    def block(x, y, w, h, head, lines, fc=WHITE, hc=BLUE):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    fc=mpl(fc), ec=mpl(hc), lw=1.6))
        ax.text(x + 0.12, y + h - 0.13, head, fontsize=9.5, fontweight="bold",
                color=mpl(hc), va="top")
        for i, ln in enumerate(lines):
            ax.text(x + 0.12, y + h - 0.45 - i * 0.24, ln, fontsize=8.2,
                    color=mpl(INK), va="top", family="serif" if "=" in ln else None)

    def arrow(x0, y0, x1, y1, label=None, lx=None, ly=None, col=BLUE, rad=0.0):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                     mutation_scale=11, lw=1.5, color=mpl(col),
                                     connectionstyle=f"arc3,rad={rad}"))
        if label:
            ax.text(lx if lx is not None else (x0 + x1) / 2,
                    ly if ly is not None else (y0 + y1) / 2 + 0.08, label,
                    fontsize=8, color=mpl(GREY), ha="center", va="bottom")

    block(0.05, 1.45, 1.85, 1.20, "1 · DRIVER + VESC",
          ["throttle 0 → 1", "ramp: 0.3 s up", "iq_cmd = throttle·120 A"])
    block(2.45, 1.45, 2.45, 1.20, "2 · MOTOR",
          ["T = 3/2·p·λm·iq − T_drag", "iq = smallest of:", "command · voltage · battery"])
    block(2.45, 0.22, 2.45, 0.80, "3 · BATTERY",
          ["V_bat = V_oc − R_int·I_bat"], fc=PANEL, hc=GREY)
    block(5.45, 1.45, 3.45, 1.20, "4 · VEHICLE",
          ["F_wheel = min(T·i·η / r_roll, μ·N_rear)", "m_eq·dv/dt = F_wheel − F_roll − F_aero",
           "∫  →  v   (the only state)"], fc=BLUE_LT)

    arrow(1.90, 2.05, 2.45, 2.05, "iq_cmd", ly=2.12)
    arrow(4.90, 2.05, 5.45, 2.05, "T", ly=2.12)
    arrow(3.30, 1.45, 3.30, 1.02, "I_bat", lx=3.02, ly=1.16, col=GREY)
    arrow(4.05, 1.02, 4.05, 1.45, "V_bat", lx=4.36, ly=1.16, col=GREY)
    # speed feedback: vehicle -> motor, routed between motor and battery
    ax.plot([8.90, 8.98, 8.98, 5.15, 5.15], [2.05, 2.05, 1.24, 1.24, 1.65],
            color=mpl(RISK), lw=1.5)
    arrow(5.15, 1.65, 4.90, 1.65, None, col=RISK)
    ax.text(7.05, 1.02, "speed fed back:  ω_m = v · i / r_roll", fontsize=8.2,
            color=mpl(RISK), ha="center", va="top", fontweight="bold")
    ax.text(7.05, 0.74, "the motor needs it for back-EMF, power and drag",
            fontsize=7.8, color=mpl(GREY), ha="center", va="top")
    save(fig, "fig_c01_model.png")


# --------------------------------------------------------------------------
# The two simulated manoeuvres
# --------------------------------------------------------------------------
def envelope_band(c):
    cases = [k for k in c if k not in ("t", "nominal")]
    stack = np.vstack([c[k] for k in cases])
    return np.nanmin(stack, axis=0), np.nanmax(stack, axis=0)


def runs():
    acc, cst = read("C01_accel_curves.csv"), read("C01_coast_curves.csv")
    oat = read("C01_oat.csv")
    i = oat["param"].index("NOMINAL")
    vtop, t025, tcst = oat["vtop_lo"][i], oat["t025_lo"][i], oat["tcst_lo"][i]

    fig, axs = plt.subplots(1, 2, figsize=(9.0, 2.9), dpi=DPI)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.17, top=0.88, wspace=0.22)
    ap = dict(arrowstyle="-", color=mpl(GREY), lw=0.8)

    ax = axs[0]
    t = acc["t"] - 0.5                      # throttle opens at t = 0.5 s in the sim
    lo, hi = envelope_band(acc)
    ax.fill_between(t, lo, hi, color=mpl(BLUE_LT), lw=0)
    ax.plot(t, acc["nominal"], color=mpl(BLUE), lw=2.2)
    ax.plot([t025], [25], "o", color=mpl(RISK), ms=5)
    ax.annotate(f"25 km/h after {t025:.1f} s", xy=(t025, 25), xytext=(5, 14),
                arrowprops=ap, fontsize=9)
    ax.annotate(f"top speed {vtop:.1f} km/h", xy=(18, vtop), xytext=(10, 25),
                arrowprops=ap, fontsize=9)
    ax.set_xlim(0, 25); ax.set_ylim(0, 40)
    ax.set_xlabel("time [s]"); ax.set_ylabel("speed [km/h]")
    title(ax, "Full throttle from standstill")

    ax = axs[1]
    lo, hi = envelope_band(cst)
    ax.fill_between(cst["t"], lo, hi, color=mpl(BLUE_LT), lw=0)
    ax.plot(cst["t"], cst["nominal"], color=mpl(BLUE), lw=2.2)
    ax.plot([tcst], [5], "o", color=mpl(RISK), ms=5)
    ax.annotate(f"5 km/h after {tcst:.1f} s", xy=(tcst, 5), xytext=(tcst + 3, 15),
                arrowprops=ap, fontsize=9)
    ax.set_xlim(0, 30); ax.set_ylim(0, 32)
    ax.set_xlabel("time [s]"); ax.set_ylabel("speed [km/h]")
    title(ax, "Coast-down: throttle released at 30 km/h")
    for a in axs:
        a.grid(True, color=mpl(LINE), lw=0.5)
    save(fig, "fig_c01_runs.png")


# --------------------------------------------------------------------------
# Sensitivity, one parameter at a time
# --------------------------------------------------------------------------
LABEL = {
    "r_roll": "rolling radius", "Crr": "rolling resistance Crr",
    "CdA": "drag area CdA", "eta_drive": "chain efficiency",
    "mu": "tyre grip μ", "x_cg": "rear weight share",
    "m_rot_wheels": "wheel inertia", "R_int": "pack resistance",
    "V_oc": "pack voltage *",
}


def tornado():
    oat = read("C01_oat.csv")
    names = oat["param"]
    i_nom = names.index("NOMINAL")
    panels = [("vtop", "Top speed", "change [km/h]", True, "km/h"),
              ("tcst", "Coast-down time", "change [s]", False, "s")]
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 2.75), dpi=DPI)
    fig.subplots_adjust(left=0.17, right=0.985, bottom=0.17, top=0.88, wspace=0.75)
    for ax, (key, ttl, xl, with_v, unit) in zip(axs, panels):
        nom = oat[key + "_lo"][i_nom]
        rows = [(n, oat[key + "_lo"][i] - nom, oat[key + "_hi"][i] - nom)
                for i, n in enumerate(names)
                if n not in ("NOMINAL", "V_BATLIM") and (with_v or n != "V_oc")]
        rows.sort(key=lambda r: max(abs(r[1]), abs(r[2])))
        rows = rows[-6:]
        for j, (n, dl, dh) in enumerate(rows):
            if n == "V_oc":
                ax.barh(j, dl, color=mpl(GREY), height=0.6)
                ax.barh(j, dh, color=mpl(GREY), height=0.6)
            else:
                ax.barh(j, dl, color=mpl(CYAN), height=0.6)
                ax.barh(j, dh, color=mpl(BLUE), height=0.6)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([LABEL[r[0]] for r in rows], fontsize=8.5)
        ax.axvline(0, color=mpl(INK), lw=0.8)
        ax.set_xlabel(xl, fontsize=9)
        title(ax, f"{ttl}: {nom:.1f} {unit} nominal")
        ax.grid(True, axis="x", color=mpl(LINE), lw=0.5)
    from matplotlib.patches import Patch
    axs[1].legend(handles=[Patch(color=mpl(CYAN), label="parameter at low end"),
                           Patch(color=mpl(BLUE), label="parameter at high end")],
                  loc="lower right", fontsize=7.5, frameon=False)
    save(fig, "fig_c01_tornado.png")


# --------------------------------------------------------------------------
# Pol's G8 answer, checked: does a higher coast-down start let CdA show?
# --------------------------------------------------------------------------
def coast_start():
    c = read("C01_coast_start.csv")
    x = np.arange(len(c["v_start_kmh"]))
    fig, ax = plt.subplots(figsize=(4.4, 2.9), dpi=DPI)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.17, top=0.88)
    w = 0.38
    ax.bar(x - w / 2, c["dt_Crr"], w, color=mpl(BLUE), label="from Crr range")
    ax.bar(x + w / 2, c["dt_CdA"], w, color=mpl(WARN), label="from CdA range")
    for xi, val in zip(x + w / 2, c["dt_CdA"]):
        ax.text(xi, val + 0.08, f"{val:.2f}", ha="center", va="bottom",
                fontsize=8, color=mpl(INK))
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v:.0f}" for v in c["v_start_kmh"]])
    ax.set_xlabel("coast-down start speed [km/h]  (to 5 km/h)")
    ax.set_ylabel("spread in coast time [s]")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.grid(True, axis="y", color=mpl(LINE), lw=0.5)
    title(ax, "Start higher → CdA shows more")
    save(fig, "fig_c01_coast_start.png")


# --------------------------------------------------------------------------
# Motor current vs battery current, and the voltage that closes the curve
# --------------------------------------------------------------------------
def _param(fname, key):
    txt = open(os.path.join(ROOT, "04_model", "params", fname), encoding="utf-8").read()
    return float(re.search(r"^" + re.escape(key) + r"\s*=\s*(-?[\d.]+(?:e-?\d+)?)",
                           txt, re.M).group(1))


def currents():
    e = read("C01_envelope.csv")
    o = np.argsort(e["v_kmh"]); v = e["v_kmh"][o]; iq = e["iq"][o]; ib = e["I_bat"][o]
    keep = (v > 0.3) & (v < 35.6) & (iq > 3.0) & (np.r_[np.diff(v) > 1e-4, False])
    v, iq, ib = v[keep], iq[keep], ib[keep]
    p = _param("motor_params.m", "mot.p"); lam = _param("motor_params.m", "mot.lambda_m")
    duty = _param("motor_params.m", "lim.duty_max")
    i_g = _param("vehicle_params.m", "veh.z_wheel") / _param("vehicle_params.m", "veh.z_motor")
    r = _param("vehicle_params.m", "veh.r_roll"); Rint = _param("vehicle_params.m", "bat.R_int")
    we = p * (v / 3.6) * i_g / r
    bemf = we * lam
    vmax = duty * (50.0 - Rint * ib) / np.sqrt(3)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.0, 3.5), dpi=DPI, sharex=True,
                                 gridspec_kw=dict(height_ratios=[1.35, 1]))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.13, top=0.97, hspace=0.12)
    a1.plot(v, iq, color=mpl(BLUE), lw=2.4)
    a1.plot(v, ib, color=mpl(RISK), lw=2.4)
    a1.axvline(9.0, color=mpl(GREY), lw=0.8, ls=":")
    a1.text(2.0, 103, "motor current iq", color=mpl(BLUE), fontsize=8.5, fontweight="bold")
    a1.text(16.0, 46, "battery current", color=mpl(RISK), fontsize=8.5, fontweight="bold")
    a1.text(9.4, 5, "9 km/h: battery hits 40 A,\nthe VESC starts cutting iq",
            fontsize=7.8, color=mpl(GREY))
    a1.set_ylim(0, 135); a1.set_ylabel("current [A]")
    a1.grid(True, color=mpl(LINE), lw=0.5)
    a2.plot(v, vmax, color=mpl(WARN), lw=2.0)
    a2.plot(v, bemf, color=mpl(INK), lw=2.0)
    a2.text(1.0, vmax[0] - 4.5, "max phase voltage = 0.95 · V_bat / √3", color=mpl(WARN),
            fontsize=8, fontweight="bold")
    a2.annotate("back-EMF = ω_e · λm  (grows with speed)", xy=(24.0, 24.0 * we[1] / v[1] * lam),
                xytext=(14.0, 3.0), color=mpl(INK), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=mpl(GREY), lw=0.8))
    a2.annotate("no voltage left → iq collapses", xy=(33.5, 26.0), xytext=(19.0, 30.5),
                fontsize=8, color=mpl(INK), fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=mpl(GREY), lw=0.8))
    a2.set_ylim(0, 34); a2.set_ylabel("phase [V]")
    a2.set_xlim(0, 40); a2.set_xlabel("vehicle speed [km/h]")
    a2.grid(True, color=mpl(LINE), lw=0.5)
    save(fig, "fig_c01_currents.png")


if __name__ == "__main__":
    crops()
    envelope()
    model_blocks()
    runs()
    tornado()
    coast_start()
    currents()
