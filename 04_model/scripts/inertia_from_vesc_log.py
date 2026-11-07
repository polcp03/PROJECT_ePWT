"""Rotor inertia and friction from the VESC log (2026-09-07_inertia_test.csv).

Drag model:  T_drag(w) = T0 + b*w
  - At no-load steady state:  Kt*iq_ss = T0 + b*w_top        (1)
  - In free deceleration:     J*dw/dt = -(T0 + b*w)          (2)
(2) gives T0/J and b/J.  (1) sets the scale -> J.
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

Kt, P = 0.0758, 3
ERPM2W = lambda e: e / P * 2 * np.pi / 60.0     # ERPM -> mechanical rad/s

df = pd.read_csv("06_data/2026-09-07_inertia/2026-09-07_inertia_test.csv", sep=";", index_col=False)
df.columns = [c.strip() for c in df.columns]
df["t"] = (df.ms_today - df.ms_today.iloc[0]) / 1000.0
df["w"] = ERPM2W(df.erpm)

# --- 1. No-load steady point --------------------------------------------
ss = df[df.erpm > 16000]
w_top = ss.w.mean()
iq_ss = ss.q_axis_current.mean()
T_top = Kt * iq_ss
P_elec = 1.5 * (ss.q_axis_voltage * ss.q_axis_current + ss.d_axis_voltage * ss.d_axis_current).mean()
print("=== NO-LOAD STEADY STATE (443 samples, 3 segments) ===")
print(f"  speed          : {ss.erpm.mean():.0f} ERPM = {ss.erpm.mean()/P:.0f} rpm mech = {w_top:.1f} rad/s")
print(f"  iq             : {iq_ss:.3f} A")
print(f"  T_drag         : Kt*iq = {T_top:.4f} N*m")
print(f"  P electrical   : {P_elec:.1f} W  ->  T = P/w = {P_elec/w_top:.4f} N*m  (cross-check)")

# lambda from no load: |v| = R*|i| + we*lambda
R = 0.02802
we = ss.erpm.mean() / 60 * 2 * np.pi
vmag = np.sqrt(ss.q_axis_voltage**2 + ss.d_axis_voltage**2).mean()
lam_nl = (vmag - R * iq_ss) / we
Vbus = ss.input_voltage.mean()
dv_dt = 0.12e-6 * 30000 * Vbus          # voltage error from dead time
print(f"\n  |v_dq|         : {vmag:.3f} V   (duty {ss.duty_cycle.mean():.4f}, Vbat {Vbus:.2f} V)")
print(f"  lambda no load : {lam_nl*1e3:.3f} mWb")
print(f"  + dead-time correction ({dv_dt:.2f} V): {(lam_nl+dv_dt/we)*1e3:.3f} mWb")

# --- 2. Free decelerations ---------------------------------------------
coast = (df.q_axis_current.abs() < 0.05) & (df.erpm > 400) & (df.erpm < 16200)
idx = np.where(coast)[0]
segs, cur = [], [idx[0]]
for a, b in zip(idx, idx[1:]):
    if b == a + 1:
        cur.append(b)
    else:
        segs.append(cur)
        cur = [b]
segs.append(cur)
segs = [s for s in segs if len(s) >= 6]
print(f"\n=== FREE DECELERATIONS: {len(segs)} segments ===")

alls = []
for k, s in enumerate(segs, 1):
    d = df.iloc[s]
    t, w = d.t.values, d.w.values
    dwdt = np.gradient(w, t)
    A = np.vstack([np.ones_like(w), w]).T          # dw/dt = -(T0/J) - (b/J)*w
    coef, *_ = np.linalg.lstsq(A, dwdt, rcond=None)
    alls.append((coef, w, dwdt))
    print(f"  segment {k}: {len(s)} pts, {w[0]:.0f} -> {w[-1]:.0f} rad/s in {t[-1]-t[0]:.2f} s"
          f"   T0/J = {-coef[0]:.1f} s^-2,  b/J = {-coef[1]:.4f} s^-1")

C = np.mean([c[0] for c in alls], axis=0)
T0_J, b_J = -C[0], -C[1]
# (1): Kt*iq = T0 + b*w_top = J*(T0/J + (b/J)*w_top)
J = T_top / (T0_J + b_J * w_top)
T0, b = T0_J * J, b_J * J
print(f"\n  mean: T0/J = {T0_J:.1f} s^-2 , b/J = {b_J:.4f} s^-1")

print(f"\n{'='*60}")
print(f"  ROTOR INERTIA       J  = {J*1e3:.4f} g*m^2  ({J:.3e} kg*m^2)")
print(f"  DRY FRICTION        T0 = {T0*1e3:.1f} mN*m")
print(f"  VISCOUS FRICTION    b  = {b*1e6:.1f} uN*m*s/rad")
print(f"{'='*60}")
print(f"  split at {w_top:.0f} rad/s: dry {T0*1e3:.0f} mN*m ({100*T0/T_top:.0f} %),"
      f" viscosa {b*w_top*1e3:.0f} mN*m ({100*b*w_top/T_top:.0f} %)")
print(f"  mechanical time constant J/b = {J/b:.2f} s")
print(f"  stopping time from {w_top:.0f} rad/s: {w_top/(T0_J+b_J*w_top/2):.2f} s approx")

# spread between segments
Js = [T_top / (-c[0][0] - c[0][1] * w_top) for c in alls]
print(f"\n  J per segment: " + ", ".join(f"{x*1e3:.3f}" for x in Js) +
      f" g*m^2  ->  dispersion {100*np.std(Js)/np.mean(Js):.1f} %")

fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.8))
for k, s in enumerate(segs, 1):
    d = df.iloc[s]
    ax[0].plot(d.t - d.t.iloc[0], d.w, "o-", ms=3, lw=1, label=f"tramo {k}")
ax[0].set_xlabel("t desde soltar [s]"); ax[0].set_ylabel("$\\omega$ mec [rad/s]")
ax[0].set_title("Deceleraciones libres"); ax[0].legend(); ax[0].grid(alpha=.3)
for c, w, dw in alls:
    ax[1].plot(w, -dw, "o", ms=4, alpha=.7)
ww = np.linspace(0, w_top, 50)
ax[1].plot(ww, T0_J + b_J * ww, "-", color="#1D4E9C", lw=2, label="fit $T_0/J + (b/J)\\omega$")
ax[1].plot(w_top, T_top / J, "r*", ms=16, label="anchor: no-load steady state")
ax[1].set_xlabel("$\\omega$ mec [rad/s]"); ax[1].set_ylabel("$-d\\omega/dt$ [rad/s²]")
ax[1].set_title("Deceleration vs speed"); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("04_model/results/inertia_result.png", dpi=115)
print("\n-> 04_model/results/inertia_result.png")
