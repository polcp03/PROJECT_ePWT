"""The drill speed is not constant within the window. That widens the FFT peak
and makes the fundamental amplitude come out LOW.
The RMS of the fundamental band is immune to that widening."""
import numpy as np, glob, os

P, SQ3 = 3, np.sqrt(3)
print(f"{'capture':<26}{'f [Hz]':>9}{'jitter':>9}{'A1 FFT':>9}{'A1 RMS':>9}"
      f"{'lam FFT':>10}{'lam RMS':>10}")
print("-" * 82)
out = []
for path in sorted(glob.glob("06_data/2026-09-07_back-emf/raw/scope_txt/*.txt")):
    d = np.loadtxt(path, skiprows=2)
    t, v = d[:, 0] * 1e-3, d[:, 1]
    fs = 1.0 / np.median(np.diff(t)); n = len(v)

    win = np.hanning(n)
    mag = np.abs(np.fft.rfft((v - v.mean()) * win)) / (win.sum() / 2)
    fr = np.fft.rfftfreq(n, 1 / fs)
    k = np.argmax(mag[1:]) + 1
    a, b, c = mag[k-1], mag[k], mag[k+1]
    dd = 0.5 * (a - c) / (a - 2*b + c)
    f_fft = fr[k] + dd * (fr[1] - fr[0]); A1_fft = b - 0.25 * (a - c) * dd

    # banda del fundamental, aislada
    sp = np.fft.rfft(v - v.mean())
    band = (fr > 0.6 * f_fft) & (fr < 1.4 * f_fft)
    vf = np.fft.irfft(np.where(band, sp, 0), n)
    A1_rms = np.sqrt(2) * np.sqrt(np.mean(vf ** 2))   # inmune al ensanchamiento

    s = np.signbit(vf); idx = np.where(s[:-1] & ~s[1:])[0]
    tz = t[idx] - vf[idx] / (vf[idx+1] - vf[idx]) / fs
    f0 = 1.0 / np.polyfit(np.arange(len(tz)), tz, 1)[0]
    jit = np.std(np.diff(tz)) * f0

    l1 = A1_fft / (SQ3 * 2 * np.pi * f0)
    l2 = A1_rms / (SQ3 * 2 * np.pi * f0)
    out.append((l1, l2))
    print(f"{os.path.basename(path):<26}{f0:>9.3f}{jit*100:>8.2f}%{A1_fft:>9.3f}"
          f"{A1_rms:>9.3f}{l1*1e3:>10.3f}{l2*1e3:>10.3f}")

l1 = np.array([x[0] for x in out]); l2 = np.array([x[1] for x in out])
print("-" * 82)
print(f"{'dispersion entre capturas':<26}{'':>9}{'':>9}{'':>9}{'':>9}"
      f"{100*l1.std()/l1.mean():>9.2f}%{100*l2.std()/l2.mean():>9.2f}%")

BMP, VESC = 16.510e-3, 16.016e-3
m = l2.mean()
print(f"\n{'='*62}")
print(f"  TXT  (RMS, inmune al jitter)  : {m*1e3:.3f} mWb")
print(f"  BMP  (43 pantallazos)         : {BMP*1e3:.3f} mWb   -> {100*(m-BMP)/BMP:+.2f} %")
print(f"  VESC (deteccion FOC)          : {VESC*1e3:.3f} mWb   -> {100*(m-VESC)/VESC:+.2f} %")
print(f"{'='*62}")
print(f"\nKt = 1.5*p*lambda = {1.5*P*m:.4f} Nm/A")
