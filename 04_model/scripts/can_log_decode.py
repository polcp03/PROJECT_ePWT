"""Decode can_logger CSV files (raw VESC status frames) and plot them.
Scaling from VESC firmware comm_can.c (FW 6/7).

Usage: python can_log_decode.py <out_dir> log_017.csv [log_018.csv ...]
Prints min/max per signal and writes <out_dir>/<log>.png.
Frames that cannot be VESC status frames (id > 0xFFFF, VESC id != 15, dlc != 8)
are counted as bad and left out: on 2026-10-31 they were SPI noise (EXP-002).
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def s16(b, i):
    v = (b[i] << 8) | b[i + 1]
    return v - 65536 if v >= 32768 else v


def s32(b, i):
    v = (b[i] << 24) | (b[i + 1] << 16) | (b[i + 2] << 8) | b[i + 3]
    return v - (1 << 32) if v >= (1 << 31) else v


def decode(pkt, b):
    if pkt == 9:
        return {"erpm": s32(b, 0), "I_motor": s16(b, 4) / 10, "duty": s16(b, 6) / 1000}
    if pkt == 16:
        return {"T_fet": s16(b, 0) / 10, "T_motor": s16(b, 2) / 10, "I_batt": s16(b, 4) / 10}
    if pkt == 27:
        return {"tacho": s32(b, 0), "V_in": s16(b, 4) / 10}
    if pkt == 58:
        return {"adc1": s16(b, 0) / 1000, "adc2": s16(b, 2) / 1000, "adc3": s16(b, 4) / 1000,
                "ppm": s16(b, 6) / 1000}
    return {}


def load(path):
    raw = pd.read_csv(path, comment="#", dtype=str)
    stats = [l.strip().split(",") for l in open(path) if l.startswith("#stat")]
    rows, bad = [], []
    for r in raw.itertuples():
        idv = int(r.id, 16)
        pkt, vid = (idv >> 8) & 0xFF, idv & 0xFF
        if idv > 0xFFFF or vid != 15 or r.dlc != "8":
            bad.append((int(r.t_us), r.id))
            continue
        b = [int(getattr(r, f"d{i}"), 16) for i in range(8)]
        d = decode(pkt, b)
        if d:
            d["t"] = int(r.t_us) / 1e6
            rows.append(d)
    df = pd.DataFrame(rows).sort_values("t")
    sig = df.groupby(df["t"].round(2)).first().ffill() if len(df) else df
    return sig, stats, bad


def main(files, out):
    for f in files:
        sig, stats, bad = load(f)
        name = Path(f).stem
        print(f"== {name}: {sig.index.max():.1f} s, stats lines {len(stats)}, bad ids {bad[:5]}")
        print("   last stat:", stats[-1] if stats else None)
        for c in ["erpm", "I_motor", "I_batt", "duty", "V_in", "adc1", "adc2", "T_fet"]:
            if c in sig:
                print(f"   {c:8s} min {sig[c].min():9.2f}  max {sig[c].max():9.2f}  last {sig[c].iloc[-1]:9.2f}")
        cols = [("erpm", "erpm"), ("I_motor", "A"), ("I_batt", "A"), ("V_in", "V"),
                ("adc1", "V"), ("duty", "-")]
        cols = [c for c in cols if c[0] in sig]
        fig, ax = plt.subplots(len(cols), 1, figsize=(9, 1.8 * len(cols)), sharex=True)
        for a, (c, u) in zip(ax, cols):
            a.plot(sig.index, sig[c], lw=1)
            a.set_ylabel(f"{c} [{u}]")
            a.grid(alpha=.3)
        ax[-1].set_xlabel("t since recording start [s]")
        ax[0].set_title(name)
        fig.tight_layout()
        fig.savefig(Path(out) / f"{name}.png", dpi=90)
        plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[2:], sys.argv[1])
