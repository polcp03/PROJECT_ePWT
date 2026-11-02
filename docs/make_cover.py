"""Cover image for the README and GitHub's social preview: real photo, architecture, real signals.

Usage, from PROJECT_ePWT/:  .venv/Scripts/python.exe docs/make_cover.py
Needs the raw data in 06_data/*/raw/, which stays out of Git: it runs on the author's machine.
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from PIL import Image, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
OUT = str(ROOT / "docs" / "cover.png")
sys.path.insert(0, str(ROOT / "04_model/scripts"))
import can_log_decode as cld

BG, PANEL, LINE = "#0d1117", "#161b22", "#30363d"
INK, DIM, FAINT = "#e6edf3", "#9aa4ae", "#6e7681"
ORANGE, BLUE, GREEN, RED = "#f0883e", "#58a6ff", "#3fb950", "#ff7b72"
W, H = 1280, 640

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)


def fx(px):  # pixels -> figure fraction
    return px / W


def fy(py):  # pixels from top -> figure fraction
    return 1 - py / H


# ---------- photo, left ----------
PW = 470
im = ImageOps.exif_transpose(Image.open(ROOT / "01_plan/presentations/assets/photos/IMG_7301.jpg"))
iw, ih = im.size                      # 3024 x 4032
cw = iw
ch = int(cw * H / PW)                 # keep the panel aspect
top = int(ih * 0.10)
im = im.crop((0, top, cw, min(ih, top + ch))).resize((PW, H), Image.LANCZOS)
im = ImageEnhance.Brightness(im).enhance(0.88)
arr = np.asarray(im).astype(float) / 255
# fade the right edge into the background
fade = np.clip((np.arange(PW) - (PW - 120)) / 120, 0, 1)[None, :, None]
bg_rgb = np.array([0x0d, 0x11, 0x17]) / 255
arr = arr * (1 - fade) + bg_rgb * fade
axp = fig.add_axes([0, 0, fx(PW), 1])
axp.imshow(arr, extent=(0, PW, H, 0))
axp.set_xlim(0, PW); axp.set_ylim(H, 0); axp.axis("off")

# callouts in photo pixels (crop starts 10 % down the original frame)
sx = PW / cw
def px(x_frac, y_frac):  # position in the original photo (fractions) -> panel pixels
    return x_frac * iw * sx, (y_frac * ih - top) * sx


def callout(pt, label, sub, tx, ty, color):
    x, y = px(*pt)
    axp.plot([x, tx], [y, ty], color=color, lw=1.2)
    axp.add_patch(plt.Circle((x, y), 5, color=color))
    axp.text(tx, ty - 4, label, color=INK, fontsize=10.5, fontweight="bold", ha="left", va="bottom",
             bbox=dict(boxstyle="round,pad=0.25", fc="#0d1117cc", ec="none"))
    axp.text(tx, ty + 3, sub, color=color, fontsize=9, ha="left", va="top",
             bbox=dict(boxstyle="round,pad=0.2", fc="#0d1117cc", ec="none"))


callout((0.70, 0.662), "PMSM MOTOR", "1.9 kW · 3 pole pairs · λm 16.86 mWb", 205, 560, ORANGE)
callout((0.84, 0.73), "FINAL DRIVE", "chain 11T / 92T = 8.36 : 1", 250, 455, ORANGE)
callout((0.14, 0.64), "FRONT WHEEL", "Hall + magnets → speed reference", 24, 395, BLUE)

# ---------- title ----------
X0 = 500
fig.text(fx(X0), fy(52), "ePWT", color=INK, fontsize=40, fontweight="bold", va="center")
fig.text(fx(X0 + 195), fy(47), "ELECTRIC POWERTRAIN LEARNING BENCH", color=ORANGE, fontsize=15,
         fontweight="bold", va="center")
fig.text(fx(X0 + 195), fy(70), "A real electric quad, modelled and instrumented from first principles",
         color=DIM, fontsize=11, va="center")

# ---------- architecture ----------
axa = fig.add_axes([fx(X0), fy(330), fx(W - X0 - 30), fy(105) - fy(330)])
axa.set_xlim(0, 750); axa.set_ylim(225, 0); axa.axis("off")
axa.text(0, 8, "ARCHITECTURE", color=FAINT, fontsize=9, fontweight="bold", va="top")


def block(x, y, w, h, title, sub, ec, fc=PANEL, dashed=False):
    axa.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                 fc=fc, ec=ec, lw=1.4, ls="--" if dashed else "-"))
    axa.text(x + w / 2, y + h * 0.38, title, color=INK, fontsize=9.5, fontweight="bold", ha="center", va="center")
    axa.text(x + w / 2, y + h * 0.72, sub, color=DIM, fontsize=8, ha="center", va="center")


def arrow(x1, y1, x2, y2, color, ls="-"):
    axa.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                  color=color, lw=1.6, ls=ls, shrinkA=0, shrinkB=0))


names = [("BATTERY", "13S5P · 48 V"), ("BMS", "40 A limit"), ("INVERTER", "VESC · FOC"),
         ("MOTOR", "PMSM · p = 3"), ("CHAIN", "8.36 : 1"), ("REAR AXLE", "13×5.00-6")]
bw, gap, y = 106, 22, 28
for i, (t, s) in enumerate(names):
    x = i * (bw + gap)
    block(x, y, bw, 52, t, s, ORANGE)
    if i:
        arrow(x - gap, y + 26, x, y + 26, ORANGE)
axa.text(750, 8, "power path →", color=ORANGE, fontsize=8.5, ha="right", va="top")

# ESP32 logger / VCU
ex, ey, ew, eh = 128, 140, 360, 58
block(ex, ey, ew, eh, "ESP32 · CAN LOGGER → VEHICLE CONTROL UNIT", "MCP2515 + microSD · own FreeRTOS task", BLUE, fc="#0f2136")
inv_x = 2 * (bw + gap) + bw / 2
arrow(inv_x, y + 52, inv_x, ey, BLUE)
axa.text(inv_x + 6, (y + 52 + ey) / 2, "CAN 500 kbit/s · 290 frames/s", color=BLUE, fontsize=8, va="center")
arrow(620, ey + eh / 2, ex + ew, ey + eh / 2, BLUE)
axa.text(626, ey + eh / 2, "wheel Hall", color=BLUE, fontsize=8, va="center")
axa.text(0, ey + eh / 2, "throttle,\nbrakes, IMU\n(next)", color=FAINT, fontsize=7.5, va="center", linespacing=1.1)
arrow(70, ey + eh / 2, ex, ey + eh / 2, FAINT, ls="--")

# ---------- signals ----------
def style(ax, title):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.tick_params(colors=FAINT, labelsize=7.5, length=2)
    ax.grid(color=LINE, lw=0.6)
    ax.set_title(title, color=INK, fontsize=9.5, fontweight="bold", loc="left", pad=6)


# back-EMF, oscilloscope
txt = sorted((ROOT / "06_data/2026-09-07_back-emf/raw/scope_txt").glob("*.txt"))[0]
d = np.loadtxt(txt, skiprows=3, max_rows=90000)
t_ms, v = d[:, 0], d[:, 1]
axb = fig.add_axes([fx(X0 + 40), fy(540), fx(300), fy(368) - fy(540)])
axb.plot(t_ms, v, color=ORANGE, lw=1.3)
axb.set_xlim(t_ms[0], t_ms[-1])
style(axb, "Back-EMF, oscilloscope")
axb.set_xlabel("time [ms]", color=FAINT, fontsize=8)
axb.set_ylabel("V phase-phase", color=FAINT, fontsize=8)

# CAN log on the vehicle under throttle
sig, _, _ = cld.load(str(ROOT / "06_data/2026-10-31_can_logger_bench/raw/log_017.csv"))
w = sig.loc[62:80]
t = w.index - w.index[0]
axc = fig.add_axes([fx(X0 + 410), fy(540), fx(300), fy(368) - fy(540)])
axc.plot(t, w["I_motor"], color=ORANGE, lw=1.2, label="motor current")
axc.plot(t, w["I_batt"], color=BLUE, lw=1.2, label="battery current")
axc.set_xlim(0, t.max()); axc.set_ylim(-5, 55)
style(axc, "CAN log on the quad · throttle, wheels lifted")
axc.set_xlabel("time [s]", color=FAINT, fontsize=8)
axc.set_ylabel("A", color=FAINT, fontsize=8)
ax2 = axc.twinx()
ax2.plot(t, w["erpm"] / 3 / 8.364 * 60 / 60, color=GREEN, lw=1.0, alpha=0.9)  # wheel rpm
ax2.set_ylim(0, 800); ax2.tick_params(colors=GREEN, labelsize=7.5, length=2)
for s in ax2.spines.values():
    s.set_color(LINE)
ax2.set_ylabel("wheel rpm", color=GREEN, fontsize=8)
leg = axc.legend(loc="upper left", fontsize=7, frameon=False, labelcolor=DIM, ncol=2)

# ---------- footer: numbers ----------
chips = [("λm 16.86 mWb", "3 methods within 0.02 %"), ("33 783 CAN frames", "0 corrupted, 0 lost"),
         ("65 deck numbers", "all traced to source"), ("Simulink twin", "built by script")]
cx = X0
for big, small in chips:
    fig.text(fx(cx), fy(603), big, color=INK, fontsize=10.5, fontweight="bold", va="center")
    fig.text(fx(cx), fy(622), small, color=FAINT, fontsize=8.5, va="center")
    cx += 190

fig.savefig(OUT, facecolor=BG)
print(OUT)
