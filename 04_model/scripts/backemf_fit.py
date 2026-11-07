"""backemf_fit.py - fits lambda_m from backemf_peaks.json and makes the figure.

Requires backemf_extract.py to have been run first.
Usage:  ./.venv/Scripts/python.exe 04_model/scripts/backemf_fit.py   (from the root)
"""

import numpy as np, json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
rows = json.load(open(os.path.join(HERE, "..", "results", "backemf_peaks.json")))
SQ3 = np.sqrt(3)
P = 3

good = [r for r in rows if r["A1"] > 0.5]
bad = [r for r in rows if r["A1"] <= 0.5]
print(f"capturas totales : {len(rows)}")
print(f"validas          : {len(good)}")
print(f"descartadas      : {len(bad)}  (motor ya parado, A1 < 0.5 V)")

f = np.array([r["f"] for r in good])
A = np.array([r["A1"] for r in good])
lam = np.array([r["lam"] for r in good])
thd = np.array([r["thd"] for r in good])
fz = np.array([r["f_zc"] for r in good])

print(f"\nrango de frecuencia : {f.min():.1f} .. {f.max():.1f} Hz  ({f.max()/f.min():.1f}:1)")
print(f"rango mecanico      : {f.min()*60/P:.0f} .. {f.max()*60/P:.0f} rpm")
print(f"acuerdo FFT/cruces  : error medio {np.mean(np.abs(f-fz)/f)*100:.2f} %")

print(f"\nlambda per capture  : {lam.mean()*1e3:.3f} ± {lam.std()*1e3:.3f} mWb "
      f"(dispersion {100*lam.std()/lam.mean():.1f} %)")

sl = (f @ A) / (f @ f)
lam_o = sl / (SQ3 * 2 * np.pi)
res = A - sl * f
print(f"\nFIT FORCED THROUGH THE ORIGIN")
print(f"  A1 = {sl:.5f} * f      ->  lambda = {lam_o*1e3:.3f} mWb")
print(f"  R^2 = {1 - np.sum(res**2)/np.sum((A-A.mean())**2):.5f}")

m, b0 = np.polyfit(f, A, 1)
sm = np.sqrt(np.sum((A-(m*f+b0))**2)/(len(f)-2))
sb = sm*np.sqrt(np.sum(f**2)/(len(f)*np.sum((f-f.mean())**2)))
print(f"\nFREE FIT (bias test)")
print(f"  A1 = {m:.5f}*f {b0:+.4f}   ->  lambda = {m/(SQ3*2*np.pi)*1e3:.3f} mWb")
print(f"  intercept = {b0:+.4f} ± {sb:.4f} V   ({abs(b0/sb):.1f} sigma from zero)")

VESC = 0.016016
print(f"\n{'='*58}")
print(f"  MEASURED (fit through origin): {lam_o*1e3:.2f} mWb")
print(f"  VESC (FOC detection)         : {VESC*1e3:.2f} mWb")
print(f"  deviation                    : {100*(lam_o-VESC)/VESC:+.1f} %")
print(f"{'='*58}")

Kt_v = 1.5*P*VESC
Kt_m = 1.5*P*lam_o
print(f"\nKt VESC   = {Kt_v:.4f} Nm/A     -> 120 A = {Kt_v*120:.2f} Nm")
print(f"Kt MEASURED = {Kt_m:.4f} Nm/A     -> 120 A = {Kt_m*120:.2f} Nm")
print(f"\nTHD (harmonic content) : {thd.mean()*100:.1f} % mean, "
      f"min {thd.min()*100:.1f} % max {thd.max()*100:.1f} %")

fig, ax = plt.subplots(1, 2, figsize=(12.5, 5))
xx = np.linspace(0, f.max()*1.05, 50)
ax[0].plot(xx, sl*xx, "-", color="#1D4E9C", lw=1.6,
           label=f"fit through the origin\n$\\lambda_m$ = {lam_o*1e3:.2f} mWb")
ax[0].plot(xx, SQ3*2*np.pi*VESC*xx, "--", color="#c44", lw=1.4,
           label=f"VESC ({VESC*1e3:.2f} mWb)")
ax[0].plot(f, A, "o", ms=5, color="#222", label=f"{len(f)} captures")
ax[0].set_xlabel("electrical frequency [Hz]"); ax[0].set_ylabel("fundamental amplitude $V_{AB}$ [V]")
ax[0].set_title("Back-EMF: amplitude vs frequency"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[0].set_xlim(0, None); ax[0].set_ylim(0, None)

ax[1].plot(f, lam*1e3, "o", ms=5, color="#222")
ax[1].axhline(lam_o*1e3, color="#1D4E9C", lw=1.6, label="measured mean")
ax[1].axhline(VESC*1e3, color="#c44", ls="--", lw=1.4, label="VESC")
ax[1].set_xlabel("electrical frequency [Hz]"); ax[1].set_ylabel("$\\lambda_m$ [mWb]")
ax[1].set_title("$\\lambda_m$ capture by capture (linearity test)")
ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_ylim(14, 18)
plt.tight_layout()
out = "04_model/results/back_emf_result.png"
plt.savefig(out, dpi=115)
print(f"\nfigura -> {out}")
