"""Chain refit (one link longer) vs chain off: duty sweep, iq and id ripple per 2 % step.
Run from PROJECT_ePWT/:  ./.venv/Scripts/python.exe 06_data/2026-11-06_chain-refit/plot.py
"""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
RUNS = [("Chain off (11-05 23:14)", HERE.parent / "2026-11-05_low-speed-no-chain/raw/2026-11-05_23-14-20.csv", (60, 108.5), "#8a8984"),
        ("Chain on, one link longer (11-06 15:22)", HERE / "raw/2026-11-06_15-22-41.csv", (22, 59), "#2a78d6")]
plt.rcParams.update({"figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb", "axes.edgecolor": "#c3c2b7",
                     "axes.grid": True, "grid.color": "#e6e5e0", "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10, "lines.linewidth": 2})


def steps(path, win):
    d = pd.read_csv(path, sep=";")
    d["t"] = (d.ms_today - d.ms_today.iloc[0]) / 1000
    s = d[(d.t > win[0]) & (d.t < win[1])].copy()
    s["k"] = (s.duty_cycle * 50).round()
    s["run"] = (s.k != s.k.shift()).cumsum()
    rows = []
    for _, g in s.groupby("run"):
        if len(g) < 30 or g.k.iloc[0] <= 0:
            continue
        g = g.iloc[int(len(g) * 0.4):]
        rows.append((g.erpm.mean(), g.q_axis_current.mean(), g.d_axis_current.std()))
    return pd.DataFrame(rows, columns=["erpm", "iq", "id_std"])


fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True)
for label, path, win, col in RUNS:
    r = steps(path, win)
    a1.plot(r.erpm, r.iq, "o-", color=col, ms=4, label=label)
    a2.plot(r.erpm, r.id_std, "o-", color=col, ms=4, label=label)
a1.set_ylabel("iq to keep turning [A]")
a1.set_ylim(0, 3.5)
a1.set_title("The chain adds a constant ~1.5 A (≈ 0.11 N·m); the angle stays clean")
a1.legend(frameon=False, fontsize=9)
a2.axvspan(1000, 2000, color="#2a78d6", alpha=0.08, lw=0)
a2.text(1500, 0.7, "Hall→observer\nhandover", ha="center", fontsize=8, color="#52514e")
a2.set_ylabel("id ripple, std [A]")
a2.set_xlabel("speed [erpm]  (one point per 2 % duty step, wheels in the air)")
fig.tight_layout()
fig.savefig(HERE / "chain_on_vs_off.png", dpi=130)
print("ok")
