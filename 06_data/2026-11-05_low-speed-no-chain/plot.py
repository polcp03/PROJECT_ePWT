"""EXP-003, chain off: plots from the VESC Tool log of 2026-11-05 22:06.

Run from PROJECT_ePWT/:  ./.venv/Scripts/python.exe 06_data/2026-11-05_low-speed-no-chain/plot.py
Writes three PNGs next to this file.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
CSV = HERE / "raw" / "2026-11-05_22-06-04.csv"
SL_START, SL_END = 2500, 4000  # foc_sl_erpm_start, foc_sl_erpm (Hall -> observer blend)

BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    "lines.linewidth": 1.4,
})

d = pd.read_csv(CSV, sep=";")
d["t"] = (d.ms_today - d.ms_today.iloc[0]) / 1000.0


def band(ax):
    ax.axhspan(SL_START, SL_END, color=ORANGE, alpha=0.10, lw=0)


# 1. Whole session: what was asked and what the motor did
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
a1.plot(d.t, d.erpm, color=BLUE)
band(a1)
a1.set_ylabel("speed [erpm]")
a1.set_title("Chain off, wheels in the air: the whole log (147 s, 5354 samples, fault code 0 in all)")
for x, y, txt in [(4, 1200, "1 A"), (12.5, 1200, "2 A"), (36, 12500, "~2.5 A:\nfree spin-up"),
                  (42, 1200, "1 A"), (52, 1200, "2 A"), (74, 12500, "~2.5 A"),
                  (118, 12500, "duty sweep 2 % → 48 %")]:
    a1.annotate(txt, (x, y), ha="center", fontsize=8, color=GREY)
a1.text(146, (SL_START + SL_END) / 2, "Hall → observer\nblend", ha="right", va="center",
        fontsize=8, color=ORANGE)
a2.plot(d.t, d.q_axis_current, color=BLUE, label="iq (torque current)")
a2.plot(d.t, d.current_motor, color=ORANGE, label="'Motor current' shown by VESC Tool")
a2.axhline(0, color=GREY, lw=0.8)
a2.set_ylabel("current [A]")
a2.set_xlabel("time [s]")
a2.legend(loc="upper left", bbox_to_anchor=(0.32, 1.0), fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(HERE / "1_session.png", dpi=130)

# 2. The "negative current" at standstill
w = d[(d.t > 0) & (d.t < 20)]
fig, (b1, b2) = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)
b1.plot(w.t, w.q_axis_current, color=BLUE, label="iq: positive, forward torque")
b1.plot(w.t, w.current_motor, color=ORANGE, label="'Motor current' = sign(vq·iq)·|i|")
b1.plot(w.t, w.current_in, color=AQUA, label="battery current: 0")
b1.axhline(0, color=GREY, lw=0.8)
b1.set_ylabel("current [A]")
b1.set_title("Standstill at 1 A and 2 A: the rotor does not move, and the 'negative' current is only a sign")
b1.legend(loc="lower left", fontsize=8, frameon=False)
b2.plot(w.t, w.q_axis_voltage, color=BLUE, label="vq [V]")
b2.plot(w.t, w.erpm / 1000, color=GREY, label="speed [k erpm]")
b2.axhline(0, color=GREY, lw=0.8)
b2.set_ylim(-0.3, 2)
b2.set_ylabel("vq [V] / speed [k erpm]")
b2.set_xlabel("time [s]")
b2.annotate("vq ≈ −0.03 to −0.08 V: tiny, below the\ndead-time error, so its sign is noise",
            (6, -0.08), (2, 0.9), fontsize=8, arrowprops=dict(arrowstyle="->", color=GREY))
b2.legend(loc="upper left", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(HERE / "2_negative_current.png", dpi=130)

# 3. Duty sweep: current ripple against speed
s = d[(d.t > 93) & (d.t < 144) & (d.erpm > 50)]
bins = list(range(0, 8501, 500))
g = s.groupby(pd.cut(s.erpm, bins), observed=True).d_axis_current.std()
mid = [iv.mid for iv in g.index]
fig, (c1, c2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
c1.scatter(s.erpm, s.d_axis_current, s=6, color=BLUE, alpha=0.6, label="id (should be 0)")
c1.axvspan(SL_START, SL_END, color=ORANGE, alpha=0.10, lw=0)
c1.axhline(0, color=GREY, lw=0.8)
c1.set_ylabel("id [A]")
c1.set_title("Duty sweep, chain off: the current is noisy only while the Halls give the angle")
c1.text((SL_START + SL_END) / 2, 5.2, "Hall → observer blend", ha="center", fontsize=8, color=ORANGE)
c1.text(1200, 5.2, "Halls only", ha="center", fontsize=8, color=GREY)
c1.text(6200, 5.2, "observer only", ha="center", fontsize=8, color=GREY)
c1.set_ylim(-8, 6.5)
c2.bar(mid, g.values, width=440, color=BLUE)
c2.axvspan(SL_START, SL_END, color=ORANGE, alpha=0.10, lw=0)
for x, y in zip(mid, g.values):
    if x in (250, 2250, 4250):
        c2.annotate(f"{y:.2f} A", (x, y), (0, 3), textcoords="offset points", ha="center", fontsize=8)
c2.set_ylabel("id ripple, std [A]")
c2.set_xlabel("speed [erpm]")
fig.tight_layout()
fig.savefig(HERE / "3_ripple_vs_speed.png", dpi=130)
print("ok")
