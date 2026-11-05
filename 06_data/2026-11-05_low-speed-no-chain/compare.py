"""EXP-003: duty sweep before (22:06, blend 2500/4000) and after (23:14, blend 1000/2000 as
reported by Pol). Per duty step: steady part only (first 40 % of each step dropped).

Run from PROJECT_ePWT/:  ./.venv/Scripts/python.exe 06_data/2026-11-05_low-speed-no-chain/compare.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RUNS = [("Blend 2500→4000 erpm (22:06)", "2026-11-05_22-06-04.csv", (93, 144), "#eb6834", (2500, 4000)),
        ("Blend 1000→2000 erpm (23:14)", "2026-11-05_23-14-20.csv", (60, 108.5), "#2a78d6", (1000, 2000))]
plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10, "lines.linewidth": 2,
})


def steps(csv, window):
    d = pd.read_csv(HERE / "raw" / csv, sep=";")
    d["t"] = (d.ms_today - d.ms_today.iloc[0]) / 1000.0
    s = d[(d.t > window[0]) & (d.t < window[1])].copy()
    s["k"] = (s.duty_cycle * 50).round()
    s["run"] = (s.k != s.k.shift()).cumsum()
    rows = []
    for _, g in s.groupby("run"):
        if len(g) < 30 or g.k.iloc[0] <= 0:
            continue
        g = g.iloc[int(len(g) * 0.4):]
        rows.append((g.erpm.mean(), g.erpm.std(), g.d_axis_current.std()))
    return pd.DataFrame(rows, columns=["erpm", "erpm_std", "id_std"])


fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True)
for label, csv, win, col, (lo, hi) in RUNS:
    r = steps(csv, win)
    a1.plot(r.erpm, r.id_std, "o-", color=col, ms=4, label=label)
    a2.plot(r.erpm, r.erpm_std, "o-", color=col, ms=4, label=label)
    for ax in (a1, a2):
        ax.axvspan(lo, hi, color=col, alpha=0.08, lw=0)
a1.set_ylabel("id ripple, std [A]")
a1.set_title("Moving the Hall→observer handover down moves the noise down with it")
a1.legend(frameon=False, fontsize=9)
a2.set_ylabel("reported speed ripple, std [erpm]")
a2.set_xlabel("speed [erpm]  (one point per 2 % duty step, chain off)")
a2.set_ylim(0, 60)
a2.annotate("below ~500 erpm: no interpolation,\nangle jumps in 60° steps (off scale)",
            (450, 58), (900, 45), fontsize=8, arrowprops=dict(arrowstyle="->", color="#52514e"))
fig.tight_layout()
fig.savefig(HERE / "4_before_after.png", dpi=130)
print("ok")
