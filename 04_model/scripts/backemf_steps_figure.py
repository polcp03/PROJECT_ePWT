import numpy as np, glob
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

F = sorted(glob.glob("06_data/**/*12-18-49*.txt", recursive=True))[0]
print("file:", F)
d = np.loadtxt(F, skiprows=2)
t, v = d[:, 0] * 1e-3, d[:, 1]
fs = 1.0 / np.median(np.diff(t)); n = len(v)
print(f"{n:,} samples, {t[-1]*1e3:.0f} ms, fs = {fs/1e3:.0f} kS/s\n")

# --- step A: separate the fundamental from the harmonics --------------
sp = np.fft.rfft(v - v.mean())
fr = np.fft.rfftfreq(n, 1 / fs)
k = np.argmax(np.abs(sp[1:])) + 1
f_gross = fr[k]
band = (fr > 0.6 * f_gross) & (fr < 1.4 * f_gross)
fund = np.fft.irfft(np.where(band, sp, 0), n)

# --- step B: frequency from zero crossings ----------------------------
s = np.signbit(fund)
idx = np.where(s[:-1] & ~s[1:])[0]
tz = t[idx] - fund[idx] / (fund[idx + 1] - fund[idx]) / fs
per, t0 = np.polyfit(np.arange(len(tz)), tz, 1)
f0 = 1 / per

# --- step C: amplitude from RMS ----------------------------------------
A1 = np.sqrt(2) * np.sqrt(np.mean(fund ** 2))
vpk_raw = 0.5 * (np.percentile(v, 99.99) - np.percentile(v, 0.01))

# --- steps D and E ------------------------------------------------------
Vph = A1 / np.sqrt(3)
we = 2 * np.pi * f0
lam = Vph / we
lam_naive = (vpk_raw / np.sqrt(3)) / we

print(f"A  fundamental isolated, harmonics out")
print(f"B  zero crossings: {len(tz)} in {t[-1]:.3f} s -> period {per*1e3:.4f} ms -> f = {f0:.4f} Hz")
print(f"C  fundamental amplitude A1 = sqrt(2)*RMS = {A1:.4f} V")
print(f"   (RAW peak on screen, with harmonics = {vpk_raw:.3f} V, {100*(vpk_raw/A1-1):.1f} % more)")
print(f"D  V_fase_pico = {A1:.4f}/sqrt(3) = {Vph:.4f} V")
print(f"E  we = 2*pi*{f0:.4f} = {we:.2f} rad/s")
print(f"\n   lambda = {Vph:.4f}/{we:.2f} = {lam*1e3:.3f} mWb     <-- RIGHT")
print(f"   reading the raw peak:         {lam_naive*1e3:.3f} mWb  <-- {100*(lam_naive/lam-1):+.1f} % error")

# ---------------------------------------------------------------- figure
nc = 3
m = t < nc / f0
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))

ax[0].plot(t[m] * 1e3, v[m], lw=1.1, color="#333")
ax[0].set_title("A · What the TXT holds\nmeasured $V_{AB}$, 3 cycles")
ax[0].set_xlabel("t [ms]"); ax[0].set_ylabel("V"); ax[0].grid(alpha=.3)
ax[0].axhline(vpk_raw, color="#c44", ls=":", lw=1.2)
ax[0].annotate(f"raw peak {vpk_raw:.2f} V\n(includes harmonics)", (0.03, .90),
               xycoords="axes fraction", color="#c44", fontsize=9)

ax[1].plot(t[m] * 1e3, v[m], lw=1.0, color="#bbb", label="measured")
ax[1].plot(t[m] * 1e3, fund[m], lw=1.8, color="#1D4E9C", label="fundamental")
ax[1].axhline(A1, color="#1D4E9C", ls="--", lw=1.2)
ax[1].set_title(f"B · Remove the harmonics\nfundamental $A_1$ = {A1:.2f} V "
                f"({100*(vpk_raw/A1-1):.0f} % menos)")
ax[1].set_xlabel("t [ms]"); ax[1].legend(fontsize=9); ax[1].grid(alpha=.3)

mz = tz < nc / f0
ax[2].plot(t[m] * 1e3, fund[m], lw=1.4, color="#1D4E9C")
ax[2].plot(tz[mz] * 1e3, np.zeros(mz.sum()), "o", ms=9, color="#c44", zorder=5)
ax[2].axhline(0, color="k", lw=.6)
for i, x in enumerate(tz[mz]):
    ax[2].annotate(f"{i}", (x * 1e3, 0), textcoords="offset points",
                   xytext=(0, 12), ha="center", color="#c44", fontsize=10)
ax[2].set_title(f"C · Frequency from zero crossings\n{len(tz)} crossings "
                f"→ f = {f0:.3f} Hz")
ax[2].set_xlabel("t [ms]"); ax[2].grid(alpha=.3)

plt.tight_layout()
plt.savefig("04_model/results/backemf_steps.png", dpi=115)
print("\n-> 04_model/results/backemf_steps.png")
