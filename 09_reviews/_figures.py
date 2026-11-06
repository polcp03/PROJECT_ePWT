"""Generate every figure the C00 deck uses, into 09_reviews/assets/figures/.

Nothing here is decoration: each figure carries a number or a relationship that
would need a paragraph of text otherwise. Run it before building the deck.

    ./.venv/Scripts/python.exe 09_reviews/_figures.py
"""
from __future__ import annotations

import csv
import datetime as dt
import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _brand import (BLUE, BLUE_DK, BLUE_LT, CYAN, GREY, INK, LINE, OK, PANEL,
                    RISK, WARN, WHITE, FONT, mpl)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "assets", "figures")
PHOTOS = os.path.join(HERE, "assets", "photos")
CROPS = os.path.join(HERE, "assets", "crops")
DATA = os.path.join(ROOT, "06_data")


def find(pattern, what):
    """Locate a data file by glob. 06_data/ gets reorganised; hard-coded
    paths do not survive that, and a figure silently built on the wrong
    file is worse than one that refuses to build."""
    hits = sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True))
    if not hits:
        raise FileNotFoundError(f"no {what} matching {pattern!r} under 06_data/")
    return hits
os.makedirs(OUT, exist_ok=True)
os.makedirs(CROPS, exist_ok=True)

DPI = 220
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [FONT, "DejaVu Sans"],
    "axes.edgecolor": mpl(LINE),
    "text.color": mpl(INK),
})

# Measured on this vehicle. Kept here so every figure quotes the same numbers.
P_POLES = 3                 # MEASURED, Hall pulse count, 2026-09-06
LAMBDA_M = 16.855e-3        # MEASURED, open-circuit back-EMF, 2026-09-07  [Wb]
LAMBDA_VESC = 15.919e-3     # VESC FOC detection, mean of 3 runs at 40 A   [Wb]
R_PHASE = 0.02802           # VESC FOC detection, mean of 3 runs at 40 A [Ohm]


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print("   ", name, Image.open(path).size)


def blank(w, h):
    """Figure whose axes are the whole canvas, measured in inches."""
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, sub=None, fc=WHITE, ec=BLUE, tc=INK,
        lw=1.2, dashed=False, ts=8.6, ss=7.0, sc=None):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05",
                       fc=mpl(fc), ec=mpl(ec), lw=lw,
                       linestyle=(0, (3, 2)) if dashed else "solid", zorder=2)
    ax.add_patch(p)
    if sub:
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=mpl(tc), zorder=3)
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
                fontsize=ss, color=mpl(sc or GREY), zorder=3, linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=ts, fontweight="bold", color=mpl(tc), zorder=3)


def arrow(ax, x0, y0, x1, y1, color=BLUE, lw=2.0, dashed=False, ms=9):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms,
        lw=lw, color=mpl(color), zorder=1,
        linestyle=(0, (3, 2)) if dashed else "solid", shrinkA=0, shrinkB=0))


def elbow(ax, x0, y0, x1, y1, color=GREY, lw=1.4, dashed=False, ms=7):
    """Vertical-then-horizontal-then-vertical routing, with the head at the end."""
    ls = (0, (3, 2)) if dashed else "solid"
    ax.plot([x0, x0], [y0, y1], color=mpl(color), lw=lw, ls=ls, zorder=1)
    ax.plot([x0, x1], [y1, y1], color=mpl(color), lw=lw, ls=ls, zorder=1)


# ==========================================================================
# 1. Chevron badge — the project mark, matching the DYN-09 corner shape
# ==========================================================================
def badge(text="EV", w=460, h=520, bg=BLUE, name="badge.png"):
    S = 4  # supersample
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W, H = w * S, h * S
    notch = int(H * 0.30)
    outer = [(0, 0), (W, 0), (W, H - notch), (W // 2, H), (0, H - notch)]
    d.polygon(outer, fill=(255, 255, 255, 255))
    b = int(W * 0.075)
    inner = [(0, 0), (W - b, 0), (W - b, H - notch - b // 2),
             (W // 2, H - int(b * 1.55)), (0, H - notch - b // 2)]
    r, g, bl = (int(bg[i:i + 2], 16) for i in (0, 2, 4))
    d.polygon(inner, fill=(r, g, bl, 255))
    size = int(H * 0.30)
    try:
        font = ImageFont.truetype("arialbd.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - b - (bb[2] - bb[0])) // 2 - bb[0], int(H * 0.30) - bb[1]),
           text, font=font, fill=(255, 255, 255, 255))
    im = im.resize((w, h), Image.LANCZOS)
    im.save(os.path.join(OUT, name))
    print("   ", name, im.size)


# --------------------------------------------------------------------------
# Shared: the power path, identical on both architecture diagrams so the eye
# can hold it still and only read what changes underneath.
# --------------------------------------------------------------------------
POWER = [
    ("BATTERY", "13S5P Li-ion\n48.1 V · ~13 Ah"),
    ("BMS", "JK-BD4A17S4P\n40 A · balancing"),
    ("INVERTER", "FSESC 6.7 Mini Pro\nfield-oriented control"),
    ("MOTOR", "PMSM 48 V · ~1.9 kW\n3 pole pairs"),
    ("FINAL DRIVE", "chain 25H\n11T / 92T = 8.36:1"),
    ("WHEELS", "13×5.00-6\nrear driven"),
]


def _power_row(ax, W_, by, bh, gap=0.16):
    n = len(POWER)
    bw = (W_ - (n - 1) * gap) / n
    for i, (t, s) in enumerate(POWER):
        x = i * (bw + gap)
        box(ax, x, by, bw, bh, t, s, fc=BLUE_LT if i < 3 else PANEL,
            ec=BLUE, ts=8.4, ss=6.4)
        if i:
            arrow(ax, x - gap - 0.005, by + bh / 2, x - 0.012, by + bh / 2,
                  lw=2.2, ms=8)
    ax.text(0, by + bh + 0.12, "POWER PATH", fontsize=8, fontweight="bold",
            color=mpl(BLUE), va="bottom")
    ax.text(W_, by + bh + 0.12, "electrical  →  mechanical", fontsize=7.2,
            color=mpl(GREY), va="bottom", ha="right")
    return bw, gap


# ==========================================================================
# 2a. Architecture as it is today
# ==========================================================================
def arch_today():
    W_, H_ = 8.76, 3.30
    fig, ax = blank(W_, H_)
    by, bh = 2.18, 0.90
    bw, gap = _power_row(ax, W_, by, bh)
    vx = 2 * (bw + gap)          # inverter column
    mx = 3 * (bw + gap)          # motor column

    ax.text(0, 1.90, "SIGNALS", fontsize=8, fontweight="bold",
            color=mpl(INK), va="top")
    cy, ch, yh = 1.06, 0.46, 1.36

    # twist grip -> inverter ADC
    box(ax, 0, cy, 1.72, ch, "TWIST GRIP", "Hall effect, 0–5 V",
        fc=WHITE, ec=GREY, ts=7.8, ss=6.3)
    xa = vx + bw * 0.30
    elbow(ax, 1.72, cy + ch / 2, xa, yh)
    ax.plot([1.72, 1.72], [cy + ch / 2, yh], color=mpl(GREY), lw=1.4, zorder=1)
    arrow(ax, xa, yh, xa, by - 0.012, color=GREY, lw=1.4, ms=7)
    ax.text(1.82, yh + 0.14, "analogue demand, straight into the inverter",
            fontsize=6.6, color=mpl(GREY), va="bottom")

    # hall sensors -> inverter
    box(ax, mx, cy, 1.72, ch, "HALL SENSORS", "rotor position",
        fc=WHITE, ec=GREY, ts=7.8, ss=6.3)
    xb = vx + bw * 0.72
    ax.plot([mx, xb], [yh, yh], color=mpl(GREY), lw=1.4, zorder=1)
    ax.plot([mx, mx], [cy + ch / 2, yh], color=mpl(GREY), lw=1.4, zorder=1)
    arrow(ax, xb, yh, xb, by - 0.012, color=GREY, lw=1.4, ms=7)

    # bms -> phone, kept on its own island because that is what it is
    box(ax, W_ - 1.72, cy, 1.72, ch, "PHONE", "Bluetooth, monitoring only",
        fc=WHITE, ec=GREY, ts=7.8, ss=6.3)
    bmx = bw + gap + bw * 0.5
    ax.plot([bmx, bmx], [by - 0.012, 0.72], color=mpl(GREY), lw=1.4, zorder=1)
    ax.plot([bmx, W_ - 0.86], [0.72, 0.72], color=mpl(GREY), lw=1.4, zorder=1)
    arrow(ax, W_ - 0.86, 0.72, W_ - 0.86, cy - 0.012, color=GREY, lw=1.4, ms=7)

    save(fig, "fig_arch_today.png")


# ==========================================================================
# 2b. Architecture as it should be — the VCU takes the vehicle layer
# ==========================================================================
def arch_target():
    W_, H_ = 8.76, 3.30
    fig, ax = blank(W_, H_)
    by, bh = 2.18, 0.90
    bw, gap = _power_row(ax, W_, by, bh)
    vx = 2 * (bw + gap)

    # The VCU band stops short of the right edge on purpose: that corridor is
    # where the rotor-position wire climbs to the inverter without crossing it.
    vy, vh, vw = 1.16, 0.62, 7.20
    box(ax, 0, vy, vw, vh, "VEHICLE CONTROL UNIT   —   ESP32  +  microSD logger",
        "owns the vehicle layer: torque shaping, traction and launch control, "
        "logging every channel the model needs",
        fc=BLUE, ec=BLUE_DK, tc=WHITE, sc=BLUE_LT,
        ts=9.4, ss=6.8, dashed=True, lw=1.4)

    # the one link that replaces today's analogue wire
    xc = vx + bw * 0.50
    arrow(ax, xc, vy + vh, xc, by - 0.012, color=BLUE, lw=2.0, ms=8)
    ax.text(xc + 0.10, vy + vh + 0.16, "torque request over CAN",
            fontsize=7.4, color=mpl(BLUE), fontweight="bold", va="center")

    # driver and vehicle inputs
    iy, ih = 0.16, 0.52
    items = [("TWIST GRIP", "torque demand"),
             ("BRAKE SWITCHES", "to be connected"),
             ("WHEEL SPEED", "Hall + magnets"),
             ("IMU", "LSM6DS3")]
    iw = (vw - (len(items) - 1) * 0.16) / len(items)
    for i, (t, s_) in enumerate(items):
        x = i * (iw + 0.16)
        box(ax, x, iy, iw, ih, t, s_, fc=WHITE, ec=GREY, ts=7.6, ss=6.3,
            dashed=True, lw=1.1)
        arrow(ax, x + iw / 2, iy + ih + 0.005, x + iw / 2, vy - 0.012,
              color=GREY, lw=1.3, dashed=True, ms=7)

    # rotor position: the inverter still needs it, and now the VCU sees it too
    hx, hw = vw + 0.15, W_ - vw - 0.15
    box(ax, hx, iy, hw, ih, "HALL SENSORS", "shared — inverter and VCU",
        fc=WHITE, ec=BLUE, ts=7.6, ss=6.3, lw=1.3)
    x_up, x_side = hx + hw * 0.70, hx + hw * 0.22
    yr = 2.02                                   # clear band above the VCU
    ax.plot([x_up, x_up], [iy + ih, yr], color=mpl(GREY), lw=1.4, zorder=1)
    ax.plot([x_up, vx + bw * 0.78], [yr, yr], color=mpl(GREY), lw=1.4, zorder=1)
    arrow(ax, vx + bw * 0.78, yr, vx + bw * 0.78, by - 0.012,
          color=GREY, lw=1.4, ms=7)
    ax.plot([x_side, x_side], [iy + ih, vy + vh / 2], color=mpl(GREY),
            lw=1.4, zorder=1)
    arrow(ax, x_side, vy + vh / 2, vw + 0.012, vy + vh / 2,
          color=GREY, lw=1.4, ms=7)

    ax.text(0, vy - 0.24, "DRIVER AND VEHICLE INPUTS", fontsize=7.6,
            fontweight="bold", color=mpl(GREY), va="top")
    ax.text(W_, vy - 0.24, "dashed  =  not built yet", fontsize=7.0,
            color=mpl(GREY), va="top", ha="right")
    save(fig, "fig_arch_target.png")



# ==========================================================================
# 3b. Where the limits are — the operating envelope
# ==========================================================================
def envelope():
    """Torque-speed envelope. Three ceilings, not two.

    l_current_max = 120 A   -> flat torque
    l_in_current_max = 40 A -> constant power
    duty * Vbus / sqrt(3)   -> the voltage ceiling, which is what actually
                               closes the envelope at no-load speed.

    An earlier version ran the constant-power hyperbola all the way to the
    measured no-load speed. That region is not reachable: at that speed the
    back-EMF alone already consumes the whole bus, so the machine can make no
    torque there. Drawing the voltage branch is what makes the picture true,
    and it is exactly where field weakening would act.
    """
    Kt = 1.5 * P_POLES * LAMBDA_M          # 0.0758 Nm/A, from measured lambda
    I_MOT, I_BAT = 120.0, 40.0
    V_NOM = 48.1                           # nominal pack, 13S at 3.70 V
    V_LOG = 52.77                          # the bus during the no-load log
    DUTY, LQ = 0.95, 112.77e-6

    T_max = Kt * I_MOT                     # 9.10 Nm
    P_bat = I_BAT * V_NOM                  # 1924 W
    V_max = DUTY * V_NOM / np.sqrt(3)      # 26.4 V, SVPWM voltage ceiling

    def iq_volt(w):
        """Largest iq the bus can push at shaft speed w, with id = 0.
        (we*Lq*iq)^2 + (R*iq + we*lam)^2 = Vmax^2, a quadratic in iq."""
        we = P_POLES * w
        a = (we * LQ) ** 2 + R_PHASE ** 2
        b = 2 * R_PHASE * we * LAMBDA_M
        c = (we * LAMBDA_M) ** 2 - V_max ** 2
        disc = np.maximum(b * b - 4 * a * c, 0.0)
        return np.maximum((-b + np.sqrt(disc)) / (2 * a), 0.0)

    rpm = lambda w: w * 60 / (2 * np.pi)                       # noqa: E731
    w_nl = V_max / (P_POLES * LAMBDA_M)        # 522 rad/s, no-load at 48.1 V
    w_nl_log = DUTY * V_LOG / np.sqrt(3) / (P_POLES * LAMBDA_M)  # 574 at 52.8 V

    w = np.linspace(2, w_nl, 1200)
    T_i = np.full_like(w, T_max)
    T_b = P_bat / w
    T_v = Kt * iq_volt(w)
    T_env = np.minimum(np.minimum(T_i, T_b), T_v)

    seg = lambda m, t: np.where(m, t, np.nan)                  # noqa: E731

    def grow(m):
        """One sample of overlap, so the branches meet instead of leaving a
        white notch at the corner where the binding limit changes hands."""
        d = m.copy()
        d[:-1] |= m[1:]
        d[1:] |= m[:-1]
        return d

    m_mot = grow((T_i <= T_b) & (T_i <= T_v))
    m_bat = grow((T_b < T_i) & (T_b <= T_v))
    m_vol = grow((T_v < T_i) & (T_v < T_b))
    w_knee = P_bat / T_max                                # 211 rad/s, 2019 rpm
    w_fw = w[np.argmax(m_vol)] if m_vol.any() else w_nl   # voltage takes over

    fig = plt.figure(figsize=(4.90, 2.72))
    ax = fig.add_axes([0.125, 0.185, 0.855, 0.775])
    X = rpm(w)

    ax.fill_between(X, 0, T_env, color=mpl(BLUE_LT), zorder=1)
    ax.plot(X, seg(m_mot, T_env), color=mpl(BLUE), lw=2.4, zorder=4)
    ax.plot(X, seg(m_bat, T_env), color=mpl(RISK), lw=2.4,
            ls=(0, (4, 2)), zorder=4)
    ax.plot(X, seg(m_vol, T_env), color=mpl(WARN), lw=2.4, zorder=4)
    ax.axvline(rpm(w_nl_log), color=mpl(GREY), lw=1.2, ls=(0, (2, 2)), zorder=2)

    ax.text(130, T_max + 0.42, "motor current  ·  120 A  ·  9.1 N·m",
            fontsize=7.4, color=mpl(BLUE), fontweight="bold")
    ax.annotate("battery  ·  40 A × 48 V  ·  1.9 kW",
                xy=(3000, P_bat / (3000 * 2 * np.pi / 60)), xytext=(2600, 9.9),
                fontsize=7.4, color=mpl(RISK), fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=mpl(RISK), lw=0.9))
    k = int(np.argmin(np.abs(X - 4700)))
    ax.annotate("voltage ceiling\n0.95 × 48 V ÷ √3",
                xy=(X[k], T_env[k]), xytext=(3980, 6.0),
                fontsize=7.4, color=mpl(WARN), fontweight="bold", ha="left",
                linespacing=1.35,
                arrowprops=dict(arrowstyle="->", color=mpl(WARN), lw=0.9))
    ax.text(rpm(w_nl_log) + 100, 0.28, "no-load, measured\n(pack at 52.8 V)",
            fontsize=6.6, color=mpl(GREY), rotation=90, va="bottom",
            ha="left", linespacing=1.3)

    ax.set_xlim(0, 6050)
    ax.set_ylim(0, 11)
    ax.set_xlabel("shaft speed  [rpm]", fontsize=8, color=mpl(GREY))
    ax.set_ylabel("shaft torque  [N·m]", fontsize=8, color=mpl(GREY))
    ax.tick_params(labelsize=7.5, colors=mpl(GREY), length=2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(mpl(LINE))
    ax.spines["bottom"].set_color(mpl(LINE))
    ax.grid(color=mpl(LINE), lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    save(fig, "fig_envelope.png")
    print("      knee %.0f rpm | voltage binds from %.0f rpm | no-load %.0f rpm"
          % (rpm(w_knee), rpm(w_fw), rpm(w_nl)))


# ==========================================================================
# 3bb. Why 92 teeth — the gearing decision, in four lines
# ==========================================================================
def gearing():
    """Slide 4. What the ratio is, what it buys, the ceiling that makes more
    pointless, and what it costs. The grip line is the one that turns a
    packaging constraint into an engineering argument - and it is the one
    built on assumed numbers, so it says so on the figure."""
    Kt = 1.5 * P_POLES * LAMBDA_M
    I_MOT, V_NOM, DUTY, Z_MOT = 120.0, 48.1, 0.95, 11
    R_ROLL = 0.155                          # ASSUMED, loaded - vehicle_params
    MU, M_TOT, X_REAR = 0.75, 112.0, 0.65   # ASSUMED, all three
    T_mot = Kt * I_MOT                                          # 9.10 Nm
    w_nl = DUTY * V_NOM / np.sqrt(3) / (P_POLES * LAMBDA_M)     # 522 rad/s

    ratio = lambda z: z / Z_MOT                                # noqa: E731
    force = lambda z: T_mot * ratio(z) / R_ROLL                # noqa: E731
    speed = lambda z: w_nl * R_ROLL / ratio(z) * 3.6           # noqa: E731
    F_grip = MU * M_TOT * 9.81 * X_REAR

    rows = [
        ("RATIO", r"$i = z_{crown} / z_{pinion}$",
         "%.2f" % ratio(92), "%.2f" % ratio(72), None),
        ("TRACTION", r"$F = K_t\, i_{max}\, i \,/\, r$",
         "%.0f N" % force(92), "%.0f N" % force(72), None),
        ("GRIP LIMIT", r"$F \leq \mu\, m\, g\, x_{rear}$",
         "%.0f N" % F_grip, "same", "ASSUMED"),
        ("TOP SPEED", r"$v = \omega_{nl}\, r \,/\, i$",
         "%.0f km/h" % speed(92), "%.0f km/h" % speed(72), None),
    ]

    W_, H_ = 5.64, 2.12
    fig, ax = blank(W_, H_)
    x_lab, x_eq, x_tag, x_new, x_old = 0.04, 1.00, 3.30, 4.22, 5.60
    ax.text(x_new, 2.00, "92 T  ·  now", fontsize=7.4, color=mpl(BLUE),
            fontweight="bold", ha="right", va="center")
    ax.text(x_old, 2.00, "72 T  ·  before", fontsize=7.4, color=mpl(GREY),
            fontweight="bold", ha="right", va="center")

    y = 1.68
    for i, (lab, eq, new, old, tag) in enumerate(rows):
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, y - 0.155), W_, 0.33,
                                   facecolor=mpl(PANEL), edgecolor="none",
                                   zorder=0))
        ax.text(x_lab, y, lab, fontsize=7.0, color=mpl(GREY),
                fontweight="bold", va="center")
        ax.text(x_eq, y, eq, fontsize=11.0, color=mpl(INK), va="center")
        ax.text(x_new, y, new, fontsize=10.0, color=mpl(BLUE),
                fontweight="bold", ha="right", va="center")
        ax.text(x_old, y, old, fontsize=9.0, color=mpl(GREY), ha="right",
                va="center")
        if tag:
            ax.text(x_tag, y, tag, fontsize=6.2, color=mpl(WARN),
                    fontweight="bold", va="center")
        y -= 0.36

    d_F = force(92) / force(72) - 1
    d_v = speed(92) / speed(72) - 1
    ax.text(0.04, 0.21,
            "92 T is the largest crown that clears the chassis — and it lands "
            "the traction force on the grip limit,\nso a bigger one would buy "
            "nothing. %+.0f %% traction for %+.0f %% top speed.  "
            "μ, mass and rear weight split are assumed."
            % (100 * d_F, 100 * d_v),
            fontsize=7.0, color=mpl(INK), va="center", linespacing=1.5)
    save(fig, "fig_gearing.png")
    print("      F92 %.0f N | F72 %.0f N | grip %.0f N | v92 %.1f | v72 %.1f"
          % (force(92), force(72), F_grip, speed(92), speed(72)))


# ==========================================================================
# 3c. The three equations the measured parameters feed
# ==========================================================================
def equations():
    fig = plt.figure(figsize=(4.60, 3.10))
    fig.patch.set_alpha(0)
    rows = [
        ("Torque",
         r"$T_e \;=\; \dfrac{3}{2}\, p\, \lambda_m\, i_q$",
         "needs  p,  λm"),
        ("Voltage, q axis",
         r"$v_q \;=\; R\,i_q + L_q \dfrac{di_q}{dt} + \omega_e (L_d i_d + \lambda_m)$",
         "needs  R,  Ld,  Lq,  λm"),
        ("Motion",
         r"$J \dfrac{d\omega}{dt} \;=\; T_e - T_0 - b\,\omega - T_{load}$",
         "needs  J,  T0,  b"),
    ]
    y = 0.95
    for label, eq, needs in rows:
        fig.text(0.03, y, label.upper(), fontsize=7.6, fontweight="bold",
                 color=mpl(BLUE), va="top")
        fig.text(0.05, y - 0.105, eq, fontsize=12.5, color=mpl(INK), va="top")
        fig.text(0.97, y, needs, fontsize=7.6, color=mpl(GREY),
                 va="top", ha="right")
        y -= 0.315
    fig.savefig(os.path.join(OUT, "fig_equations.png"), dpi=DPI,
                transparent=True)
    plt.close(fig)
    print("    fig_equations.png",
          Image.open(os.path.join(OUT, "fig_equations.png")).size)


# ==========================================================================
# 3. Back-EMF — the waveform that was measured, and the constant it gives
# ==========================================================================
def backemf():
    path = find("06_data/**/*.txt", "raw scope capture")[0]
    rows = []
    with open(path) as fh:
        for i, line in enumerate(fh):
            if i < 2 or not line.strip():
                continue
            a, b = line.split()
            rows.append((float(a), float(b)))
            if len(rows) > 60000:
                break
    d = np.array(rows)
    t, v = d[:, 0], d[:, 1]
    f0 = 125.484                        # Hz, from backemf_from_csv.py
    n = int(2.4 / f0 * 1000 / (t[1] - t[0]))
    s = slice(2000, 2000 + n)

    fig = plt.figure(figsize=(8.30, 2.62))
    axw = fig.add_axes([0.055, 0.175, 0.505, 0.70])
    axw.plot(t[s] - t[s.start], v[s], color=mpl(BLUE), lw=1.5)
    axw.axhline(0, color=mpl(LINE), lw=0.8)
    axw.set_xlabel("time  [ms]", fontsize=8, color=mpl(GREY))
    axw.set_ylabel("phase-to-phase  [V]", fontsize=8, color=mpl(GREY))
    axw.set_title("Open-circuit back-EMF, motor dragged by a drill",
                  fontsize=9, fontweight="bold", pad=6)
    axw.tick_params(labelsize=7.5, colors=mpl(GREY), length=2)
    for sp in ("top", "right"):
        axw.spines[sp].set_visible(False)
    axw.spines["left"].set_color(mpl(LINE))
    axw.spines["bottom"].set_color(mpl(LINE))
    axw.text(0.985, 0.05, "2 509 rpm  ·  125.5 Hz electrical",
             transform=axw.transAxes, fontsize=7, color=mpl(GREY), ha="right")

    # the two captures against the inverter's own estimate
    axl = fig.add_axes([0.665, 0.175, 0.325, 0.70])
    caps = [(1310, 16.826), (2510, 16.883)]
    axl.axhline(LAMBDA_VESC * 1e3, color=mpl(RISK), lw=1.5, ls=(0, (4, 2)),
                zorder=2)
    axl.axhline(LAMBDA_M * 1e3, color=mpl(OK), lw=1.5, zorder=2)
    axl.plot([c[0] for c in caps], [c[1] for c in caps], "o", ms=8,
             color=mpl(OK), markeredgecolor=mpl(WHITE), markeredgewidth=1.2,
             zorder=4)
    axl.text(1180, LAMBDA_M * 1e3 + 0.06, "measured  16.86", fontsize=7.4,
             color=mpl(OK), fontweight="bold", va="bottom")
    axl.text(1180, LAMBDA_VESC * 1e3 - 0.06, "inverter estimate  15.92",
             fontsize=7.4, color=mpl(RISK), fontweight="bold", va="top")
    axl.annotate("", xy=(2900, LAMBDA_M * 1e3), xytext=(2900, LAMBDA_VESC * 1e3),
                 arrowprops=dict(arrowstyle="<->", color=mpl(INK), lw=1.1))
    axl.text(2820, (LAMBDA_M + LAMBDA_VESC) / 2 * 1e3, "5.5 %", fontsize=7.6,
             fontweight="bold", color=mpl(INK), ha="right", va="center")
    axl.set_xlim(1100, 3120)
    axl.set_ylim(15.6, 17.2)
    axl.set_xlabel("mechanical speed  [rpm]", fontsize=8, color=mpl(GREY))
    axl.set_ylabel("λm  [mWb]", fontsize=8, color=mpl(GREY))
    axl.set_title("Two captures, speed doubled", fontsize=9,
                  fontweight="bold", pad=6)
    axl.tick_params(labelsize=7.5, colors=mpl(GREY), length=2)
    for sp in ("top", "right"):
        axl.spines[sp].set_visible(False)
    axl.spines["left"].set_color(mpl(LINE))
    axl.spines["bottom"].set_color(mpl(LINE))
    axl.grid(axis="y", color=mpl(LINE), lw=0.6, zorder=0)
    axl.set_axisbelow(True)

    fig.savefig(os.path.join(OUT, "fig_backemf.png"), dpi=DPI, transparent=True)
    plt.close(fig)
    print("    fig_backemf.png",
          Image.open(os.path.join(OUT, "fig_backemf.png")).size)


# ==========================================================================
# 4. Spin-down — the test that is done, and the limit that stops it there
# ==========================================================================
def spindown():
    path = find("06_data/**/*iner*.csv", "spin-down log")[0]
    rows = list(csv.DictReader(open(path), delimiter=";"))
    t = np.array([float(r["ms_today"]) for r in rows]) * 1e-3
    t -= t[0]
    w = np.array([float(r["erpm"]) for r in rows]) * 2 * np.pi / 60 / P_POLES

    fig = plt.figure(figsize=(4.30, 2.42))
    ax = fig.add_axes([0.155, 0.19, 0.825, 0.66])
    ax.plot(t, w, color=mpl(BLUE), lw=1.6)
    for a, b in [(15.1, 16.0), (28.3, 29.3), (39.7, 40.5)]:
        ax.axvspan(a, b, color=mpl(CYAN), alpha=0.22, lw=0, zorder=0)
    ax.set_xlabel("time  [s]", fontsize=8, color=mpl(GREY))
    ax.set_ylabel("shaft speed  [rad/s]", fontsize=8, color=mpl(GREY))
    ax.set_title("Spin-down: three repeats", fontsize=9, fontweight="bold",
                 pad=16)
    ax.tick_params(labelsize=7.5, colors=mpl(GREY), length=2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(mpl(LINE))
    ax.spines["bottom"].set_color(mpl(LINE))
    ax.grid(axis="y", color=mpl(LINE), lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.text(0.5, 1.015, "−636  /  −631  /  −655 rad/s²      repeatable to 2 %",
            transform=ax.transAxes, fontsize=7.4, fontweight="bold",
            color=mpl(CYAN), ha="center", va="bottom")
    fig.savefig(os.path.join(OUT, "fig_spindown.png"), dpi=DPI, transparent=True)
    plt.close(fig)
    print("    fig_spindown.png",
          Image.open(os.path.join(OUT, "fig_spindown.png")).size)


# ==========================================================================
# 5. Plan to December
# ==========================================================================
def timeline():
    D = dt.date
    rows = [
        ("C00", "Kickoff — and the machine already characterised", D(2026, 9, 2), D(2026, 9, 9), D(2026, 9, 8), BLUE_DK),
        ("", "Holidays", D(2026, 9, 10), D(2026, 9, 27), None, LINE),
        ("C01", "Finish the plant: vehicle mass, radius, inertia", D(2026, 9, 28), D(2026, 10, 11), D(2026, 10, 12), BLUE),
        ("C02", "Longitudinal model validated by coast-down", D(2026, 10, 12), D(2026, 10, 25), D(2026, 10, 26), BLUE),
        ("C03", "PMSM in dq — Clarke and Park from the equations", D(2026, 10, 26), D(2026, 11, 8), D(2026, 11, 9), BLUE),
        ("C04", "Inverter + current loop. Torque control", D(2026, 11, 9), D(2026, 11, 22), D(2026, 11, 23), BLUE),
        ("C05", "Instrument the vehicle — VCU and data logger", D(2026, 11, 23), D(2026, 12, 6), D(2026, 12, 7), BLUE),
        ("C06", "Model ↔ vehicle correlation", D(2026, 12, 7), D(2026, 12, 20), D(2026, 12, 21), BLUE),
    ]
    fig = plt.figure(figsize=(8.76, 2.62))
    ax = fig.add_axes([0.345, 0.135, 0.635, 0.79])

    for i, (cid, label, s, e, rev, col) in enumerate(rows):
        y = len(rows) - 1 - i
        hatched = cid == ""
        ax.barh(y, (e - s).days, left=s, height=0.52, color=mpl(col), zorder=3,
                hatch="///" if hatched else None,
                edgecolor=mpl(GREY) if hatched else "none", linewidth=0.0)
        if rev:
            ax.plot([rev], [y], marker="D", ms=6.5, color=mpl(CYAN),
                    markeredgecolor=mpl(WHITE), markeredgewidth=0.9, zorder=5)
        ax.text(-0.012, y, cid, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=9.5, fontweight="bold",
                color=mpl(BLUE if cid else GREY))
        ax.text(-0.080, y, label, transform=ax.get_yaxis_transform(),
                ha="right", va="center", fontsize=7.6,
                color=mpl(INK if cid else GREY))

    ax.set_ylim(-0.75, len(rows) - 0.25)
    ax.set_xlim(D(2026, 8, 31), D(2027, 1, 2))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(axis="x", labelsize=8, colors=mpl(INK), length=0, pad=4)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(mpl(LINE))
    ax.grid(axis="x", color=mpl(LINE), lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.plot([], [], marker="D", ms=6.5, color=mpl(CYAN), ls="none",
            markeredgecolor=mpl(WHITE), label="review with mentors")
    ax.legend(loc="lower right", fontsize=7.4, frameon=False,
              handletextpad=0.4, bbox_to_anchor=(1.0, -0.19))
    fig.savefig(os.path.join(OUT, "fig_timeline.png"), dpi=DPI, transparent=True)
    plt.close(fig)
    print("    fig_timeline.png",
          Image.open(os.path.join(OUT, "fig_timeline.png")).size)


# ==========================================================================
# 6. The two-week cycle
# ==========================================================================
def cycle():
    W_, H_ = 4.60, 2.45
    fig, ax = blank(W_, H_)
    steps = [("PLAN", "one goal,\none deliverable"),
             ("BUILD", "measure, model,\nwrite it down"),
             ("EXPLAIN", "out loud,\nno notes"),
             ("REVIEW", "45 min\nwith you")]
    bw, gap, bh, y = 0.92, 0.16, 0.88, 1.06
    x0 = (W_ - (len(steps) * bw + (len(steps) - 1) * gap)) / 2
    for i, (t, s_) in enumerate(steps):
        x = x0 + i * (bw + gap)
        last = i == len(steps) - 1
        box(ax, x, y, bw, bh, t, s_, fc=BLUE if last else BLUE_LT, ec=BLUE,
            tc=WHITE if last else INK, sc=WHITE if last else GREY,
            ts=8.6, ss=6.4)
        if i:
            arrow(ax, x - gap - 0.005, y + bh / 2, x - 0.012, y + bh / 2,
                  lw=1.8, ms=8)
    xa = x0 + (len(steps) - 1) * (bw + gap) + bw / 2
    xb = x0 + bw / 2
    ax.add_patch(FancyArrowPatch((xa, y - 0.03), (xb, y - 0.03),
                                 connectionstyle="arc3,rad=-0.34",
                                 arrowstyle="-|>", mutation_scale=9,
                                 lw=1.6, color=mpl(CYAN), zorder=1))
    ax.text(W_ / 2, 0.26, "every 2 weeks  ·  ~28 h  ·  fixed date",
            ha="center", fontsize=8, fontweight="bold", color=mpl(CYAN))
    ax.text(W_ / 2, H_ - 0.10, "The deadline is the mechanism, not the ritual",
            ha="center", va="top", fontsize=7.4, color=mpl(GREY), style="italic")
    save(fig, "fig_cycle.png")


# ==========================================================================
# 7. Photo crops
# ==========================================================================
def crops():
    jobs = [
        ("IMG_7301.jpg", "strip_field.jpg", 10 / 1.4625, 0.52),
        ("IMG_7300.jpg", "strip_drive.jpg", 10 / 1.4625, 0.46),
        ("IMG_7239.jpg", "strip_motor.jpg", 10 / 1.4625, 0.47),
        ("IMG_7175.jpg", "strip_pack.jpg", 10 / 1.4625, 0.45),
        ("IMG_7163.jpg", "strip_quad.jpg", 10 / 1.4625, 0.45),
        ("IMG_7301.jpg", "hero.jpg", 10 / 5.625, 0.50),
        ("IMG_7301.jpg", "half_field.jpg", 0.82, 0.50),
        ("IMG_7300.jpg", "half_drive.jpg", 0.82, 0.50),
        ("IMG_7239.jpg", "half_motor.jpg", 0.82, 0.52),
        ("IMG_7175.jpg", "half_pack.jpg", 0.82, 0.50),
        ("IMG_7163.jpg", "half_quad.jpg", 0.82, 0.48),
    ]
    for src, out, aspect, focus in jobs:
        im = Image.open(os.path.join(PHOTOS, src)).convert("RGB")
        w, h = im.size
        if w / h < aspect:
            nh = int(w / aspect)
            top = int((h - nh) * focus)
            im = im.crop((0, top, w, top + nh))
        else:
            nw = int(h * aspect)
            left = int((w - nw) * focus)
            im = im.crop((left, 0, left + nw, h))
        im.thumbnail((2400, 2400), Image.LANCZOS)
        im.save(os.path.join(CROPS, out), quality=88)
        print("    ", out, im.size)


if __name__ == "__main__":
    print("badge")
    badge()
    print("figures")
    arch_today()
    arch_target()
    envelope()
    gearing()
    equations()
    backemf()
    spindown()
    timeline()
    cycle()
    print("crops")
    crops()
    print("done ->", OUT)
