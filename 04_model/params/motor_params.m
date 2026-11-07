%% MOTOR_PARAMS  PMSM + inverter + VESC control configuration
%
%  Source of truth for the electrical machine and the low-level controller.
%  All values in SI base units unless the name says otherwise.
%
%  Every value carries a tag:
%    MEASURED      - measured on this vehicle, traceable to 03_hardware/
%    VESC_ESTIMATE - produced by the VESC FOC detection routine (not independent)
%    CONFIG        - typed into the VESC by a human; NOT a measurement
%    ASSUMED       - engineering guess, must be replaced before correlation
%
%  Primary source : 03_hardware/vesc/MOTOR_1.9.xml   (saved 2026-08-10)
%  Cross-check    : Screenshot 2026-07-29 152318.png      (earlier detection run)
%  Convention ref : VESC firmware, motor/virtual_motor.c and motor/mcpwm_foc.c
%
%  SIGN / SCALING CONVENTION  (verified against the firmware, not assumed)
%  ---------------------------------------------------------------------
%  VESC uses the amplitude-invariant (K = 1) Clarke/Park transform and the
%  standard per-phase (wye-equivalent) dq model. From mcpwm_foc.c:4650 and
%  virtual_motor.c:305-330:
%
%     vd = Rs*id + Ld*d(id)/dt - we*Lq*iq
%     vq = Rs*iq + Lq*d(iq)/dt + we*(Ld*id + lambda_m)
%     Te = 1.5 * p * (lambda_m + (Ld - Lq)*id) * iq
%
%  This is exactly the equation set of the Simulink/Simscape PMSM block, so
%  R, Ld, Lq and lambda_m below drop straight into it with no rescaling.
%
%  IMPORTANT - the phase-vs-line question is RESOLVED, see EXP-001:
%  mcpwm_foc_measure_resistance() computes R = norm(v_dq) / norm(i_dq) with the
%  rotor frame locked (mcpwm_foc.c:1869-1885, sampling at :4144). Both are
%  dq-frame phase quantities, so foc_motor_r is the PER-PHASE resistance, not
%  line-to-line. A multimeter across two phases must read about 2*Rs.

%% ------------------------------------------------------------------
%% 1. Electrical machine
%% ------------------------------------------------------------------

% Pole pairs.
% MEASURED 2026-09-06 by Hall pulse counting, drivetrain assembled.
% One hall line produces p electrical cycles per mechanical motor revolution.
% One turn of the 92T rear sprocket = 92/11 = 8.364 motor turns, so the
% expected count is 8.364*p: 25.1 for p=3, 33.5 for p=4.
% Counted 25, repeatable. -> p = 3, unambiguous.
% Side effect: this also confirms the 92/11 gear ratio. A wrong ratio would
% not have landed the count on a valid row of that table.
mot.p            = 3;              % [-]  MEASURED

% Stator resistance, per phase.
% FINAL (Pol, 2026-11-06): the value in the saved config,
%   03_hardware/vesc/MOTOR_1.9.xml, foc_motor_r = 18.76 mOhm.
% 2026-11-05: THREE VESC detections at I = 40 A, after rewriting the config,
%   all 18.7 mOhm. Replaces the 2026-09-07 value (27.83 / 28.14 / 28.10 ->
%   28.02 mOhm, same 40 A), which no longer reproduces. Cause of the change
%   not found; temperature alone cannot explain 33 %.
% Still a VESC_ESTIMATE: it includes MOSFET on-resistance and dead-time, so it
% is the resistance the CURRENT LOOP sees, an upper bound on the winding
% copper. That is the right number for simulating the loop; it is not the right
% number for a copper-loss or thermal model. Temperature of the run unknown
% (no motor sensor), and copper moves 0.39 %/K.
mot.Rs           = 0.01876;        % [Ohm]  VESC_ESTIMATE, final config 2026-11-06

% Inductances. VESC stores the average L and the saliency difference:
%   Lq = L + diff/2 ,  Ld = L - diff/2      (foc_math.c:782-783)
% FINAL (Pol, 2026-11-06): the saved config, foc_motor_l = 105.6 uH and
%   foc_motor_ld_lq_diff = 14.42 uH  ->  Ld 98.39, Lq 112.81 uH, Lq/Ld 1.147.
% History, the 2026-09-07 detections at I = 40.00 A:
%   L      : 105.95 / 106.10 / 105.96 uH  ->  106.00 +/- 0.07 uH  (0.06 %)
%   Lq-Ld  :  13.41 /  13.91 /  13.31 uH  ->   13.54 +/- 0.26 uH  (1.9 %)
mot.L_avg        = 105.6e-6;       % [H]  VESC_ESTIMATE, final config 2026-11-06
mot.L_diff       = 14.42e-6;       % [H]  VESC_ESTIMATE, final config 2026-11-06
mot.Ld           = mot.L_avg - mot.L_diff/2;   %  98.39 uH
mot.Lq           = mot.L_avg + mot.L_diff/2;   % 112.81 uH
% Saliency ratio Lq/Ld = 1.147 (1.136 in the 09-07 runs).
% RESOLVED: the saliency is repeatable to 1.9 % when the detection settings are
% held fixed. The old 9.45 / 16.90 uH spread came from runs at DIFFERENT
% detection currents (the 2026-07-29 run used 97.85 A against 40 A here), i.e.
% it is magnetic saturation, not noise. Saliency is therefore a function of
% current, which is exactly what an MTPA table would have to capture. Anything
% built on a single saliency number is only valid at that current.

% Permanent-magnet flux linkage (peak phase value, amplitude-invariant dq).
% MEASURED 2026-09-07 by open-circuit back-EMF, independently of the VESC.
% Motor disconnected from the inverter, scope across two phases, drill drive.
%   lambda = A1_fundamental / (sqrt(3) * 2*pi*f)
%
% Two raw-data captures (06_data/2026-09-07_back-emf/raw/scope_txt/), 1310 and 2510 rpm mechanical:
%   16.826 and 16.883 mWb  ->  agreement 0.17 % across a 2:1 speed range.
% Amplitude taken as sqrt(2)*RMS of the fundamental band, NOT the FFT peak:
% the drill speed wobbles ~1-2 % inside the window, which smears the peak and
% biases a peak-picked amplitude low. The RMS estimator is immune to that, and
% it is what collapses the two captures from 1.08 % apart to 0.17 %.
% Script: 04_model/scripts/backemf_from_csv.py
mot.lambda_m     = 0.016855;       % [Wb]  MEASURED

% Superseded, kept for traceability:
% An earlier pass read 43 oscilloscope SCREENSHOTS pixel by pixel and fitted
% A1 vs f through the origin -> 16.51 mWb, R^2 = 0.9911, intercept 1.3 sigma
% from zero. That is 2.0 % below the raw-data value, from the same speed-wobble
% bias plus 47 mV of pixel resolution. It agreeing to 2 % validates the pixel
% calibration, but the raw data supersedes it.
% Scripts: 04_model/scripts/backemf_extract.py + backemf_fit.py

% THIRD, INDEPENDENT CONFIRMATION - 2026-09-07, no-load steady state.
% Held at the duty ceiling (0.9486) for 443 logged samples: 16440 ERPM,
% |v_dq| = 28.886 V, iq = 1.883 A, Vbat 52.77 V.
%     lambda = (|v| - R*i) / we  =  16.748 mWb
% The VESC reports the voltage it COMMANDS, not the one it applies. Dead time
% costs td*fsw*Vbus = 0.12us * 30kHz * 52.77 = 0.19 V. Adding it back:
%     lambda = 16.858 mWb   vs   16.855 mWb from the scope  ->  0.02 % apart.
% Two methods sharing no assumption, agreeing to two parts in ten thousand.
mot.lambda_m_nl  = 0.016858;       % [Wb] MEASURED, no-load telemetry route

% The VESC's own FOC detection is NOT a reference (corrected 2026-11-06).
% Within one session it repeats to 0.3 % (2026-09-07, 3 runs at 40 A:
% 15.978 / 15.859 / 15.919 mWb), but between sessions it ranges from 15.86 to
% 17.0 mWb (16.07, 16.016, 16.19, then 17.0 / 16.2 / 16.7 / 16.8), about 7 %.
% The measured 16.855 sits inside that range, so no fixed detection bias can be
% claimed; the earlier "5.5 % low" came from the 09-07 session alone.
% The saved config (03_hardware/vesc/MOTOR_1.9.xml, 2026-11-06) now holds the
% measured 16.855 mWb, so the VESC observer and the plant use the same value.
mot.lambda_m_vesc = 0.016855;      % [Wb] what the controller's config holds

% Back-EMF waveform is not a pure sinusoid. MEASURED harmonic content of the
% line-to-line voltage, identical in both captures (share of the fundamental):
%    5th  4.0 %   7th  8.1 %   11th  2.0 %   13th  1.4 %   -> THD 9.2-9.6 %
% No 3rd and no 9th, as it must be: triplen harmonics are in phase in all
% three phases and cancel in any line-to-line voltage. Their absence is a
% check that the measurement itself is sound.
% A dq model assumes a sinusoid, so it will not reproduce the torque ripple
% these produce (mainly 6th-order in the rotor frame, from the 5th and 7th).
% Fine at vehicle level; remember it before blaming a correlation gap on
% something else.
mot.bemf_thd     = 0.094;          % [-] MEASURED

% Derived constants (do not edit - computed from the above)
mot.Kt           = 1.5 * mot.p * mot.lambda_m;   % [Nm/A] torque per amp of iq
mot.Ke_phase_pk  = mot.lambda_m;                 % [V*s/rad_elec] peak phase BEMF
mot.tau_e_d      = mot.Ld / mot.Rs;              % [s] 5.24 ms
mot.tau_e_q      = mot.Lq / mot.Rs;              % [s] 6.01 ms
% Kt = 0.0758 Nm/A  ->  40 A = 3.03 Nm, 120 A = 9.10 Nm.
% (0.0716 with the single 09-07 detection, 15.92 mWb: the reason the detection
%  is not used.)
% Kt scales linearly with p, so the whole torque axis of the model is only as
% good as the pole-pair measurement.

% Rotor inertia and drag, motor alone (chain off).
% MEASURED 2026-09-07 from a VESC log: three spin-ups to the no-load speed
% followed by free coast-downs. 06_data/inercia/2026-09-07_inertia_test.csv
% Script: 04_model/scripts/inertia_from_vesc_log.py
%
% Drag model:  T_drag(w) = T0 + b*w
%   Coast-down gives the RATIOS  T0/J = 405 s^-2  and  b/J = 0.89 s^-1
%   Steady no-load gives the SCALE: Kt*iq_ss = 0.1427 Nm at 573.9 rad/s
%   Two relations, three unknowns collapse to one solution.
mot.J            = 1.558e-4;       % [kg*m^2]   MEASURED, +/- 14 %
mot.T_coulomb    = 63.1e-3;        % [Nm]       MEASURED
mot.b_visc       = 138.8e-6;       % [Nm*s/rad] MEASURED
% At the no-load speed the drag splits 44 % dry / 56 % viscous.
% Mechanical time constant J/b = 1.12 s.
%
% ACCURACY: the 14 % is the spread between the three coast-downs, each with
% only 12-13 samples because the VESC logs at 15 Hz. J is NOT from the clean
% two-test subtraction (accelerate at known current, then coast): the spin-up
% lasted ~0.3 s and produced 3 aliased samples, useless. It is instead the
% coast-down slope anchored on the steady-state drag, which is a sound method
% but leans on Kt, hence on lambda_m.
% To tighten it: cap l_current_max to ~10 A so the spin-up takes 2-3 s, and
% log as fast as the tool allows. Then the subtraction method works and J
% stops depending on Kt at all.
%
% VESC no-load current si_motor_nl_current = 1 A is a CONFIG placeholder. The
% real no-load current at 5480 rpm is 1.88 A.

mot.mass         = 4.0;            % [kg]  CONFIG (motor_weight = 4000 g)

%% ------------------------------------------------------------------
%% 2. Inverter / PWM
%% ------------------------------------------------------------------
inv.f_sw         = 30e3;           % [Hz]  CONFIG  foc_f_zv
inv.t_deadtime   = 0.12e-6;        % [s]   CONFIG  foc_dt_us
inv.modulation   = 'SVPWM';        % max norm(v_dq) = v_bus/sqrt(3)  (mcpwm_foc.c:4684)
inv.overmod_fact = 1.0;            % CONFIG  foc_overmod_factor
inv.v_mag_max_fn = @(vbus,duty) (1/sqrt(3)) * duty * vbus * inv.overmod_fact;

% Control loop period. The firmware picks this in mcpwm_foc_get_ts() (:1091):
%   HW with phase shunts + sample mode V0 only  ->  Ts = 2/f_sw = 66.7 us (15 kHz)
%   otherwise                                   ->  Ts = 1/f_sw = 33.3 us (30 kHz)
% foc_control_sample_mode = 0 (V0). Whether the FSESC 6.7 Mini Pro build
% defines HW_HAS_PHASE_SHUNTS is not determinable from the XML.
inv.Ts_control   = 2/inv.f_sw;     % [s]  ASSUMED 15 kHz  <<< OPEN: confirm on device

%% ------------------------------------------------------------------
%% 3. VESC current controller (what the real hardware actually runs)
%% ------------------------------------------------------------------
% Parallel-form PI on id and iq, no D term (mcpwm_foc.c:4639-4644):
%   v_int += err * ki * dt ;  v = v_int + err * kp
% Values on the device after the 2026-09-07 detections: kp 0.2119, ki 56.20,
% observer gain 3.95e6. The three runs gave kp 0.2119/0.2122/0.2119 and
% ki 55.66/56.28/56.20 - the same 0.5 % spread as R and L, as expected since
% the firmware derives them as kp = L*bw and ki = R*bw with bw = 2000 rad/s.
ctrl.kp          = 0.2119;         % [V/A]     CONFIG  foc_current_kp
ctrl.ki          = 56.20;          % [V/(A*s)] CONFIG  foc_current_ki
% Self-consistency check against conf_general_calc_apply_foc_cc_kp_ki_gain():
%   kp = L*bw and ki = R*bw  ->  bw = 2000 rad/s (tc = 500 us) for BOTH gains.
%   Closed-loop current bandwidth ~= 2000 rad/s = 318 Hz.
ctrl.bw_current  = 2000;           % [rad/s]  DERIVED, cross-checked

ctrl.decoupling  = 0;              % CONFIG foc_cc_decoupling = DISABLED.
                                   % No cross-term and no back-EMF feedforward:
                                   % the PI has to reject we*lambda_m as a
                                   % disturbance. Model it that way or the
                                   % simulated tracking will look optimistic.
ctrl.mtpa_mode   = 0;              % CONFIG  MTPA off -> id_ref = 0 always
ctrl.fw_current  = 0;              % [A] CONFIG  field weakening disabled
ctrl.temp_comp   = 0;              % CONFIG  no R(T) compensation

% Sensors and observer
ctrl.sensor_mode   = 'HALL';       % CONFIG foc_sensor_mode = 2
ctrl.hall_sl_erpm  = [2500 4000];  % [ERPM] hall -> sensorless blend window
ctrl.observer_type = 3;            % CONFIG foc_observer_type = 3 (MXLEMMING_LAMBDA_COMP)
ctrl.observer_gain = 3.95e6;       % CONFIG. Check: 1e3/lambda_vesc^2 = 3.946e6. OK.
ctrl.pll_kp        = 2000;
ctrl.pll_ki        = 30000;

%% ------------------------------------------------------------------
%% 4. Limits actually enforced by the VESC (the model must respect these)
%% ------------------------------------------------------------------
lim.i_motor_max  = 120;            % [A] CONFIG  l_current_max
lim.i_motor_min  = -120;           % [A] CONFIG  l_current_min (regen)
lim.i_abs_max    = 160;            % [A] CONFIG  l_abs_current_max
lim.i_batt_max   = 40;             % [A] CONFIG  l_in_current_max - equals the
                                   %     JK BMS continuous rating. Do not raise.
lim.i_batt_min   = -35;            % [A] CONFIG  l_in_current_min
lim.duty_max     = 0.95;           % [-] CONFIG
lim.v_batt_cut   = [44.2 39.0];    % [V] CONFIG  fold-back start/end (3.40/3.00 V/cell)
lim.T_fet        = [85 100];       % [degC] CONFIG fold-back start/end

% m_motor_temp_sens_type = 8 = TEMP_SENSOR_DISABLED, because no sensor is
% fitted to the motor. The limits l_temp_motor_start/end (85/100 degC) are
% therefore dead code. Consequences for the model, not for the vehicle:
%   - no thermal derating branch to simulate or validate
%   - foc_temp_comp = 0, so Rs is fixed; the value below is whatever the
%     winding temperature happened to be during the detection run, unknown
%   - Rs rises ~0.39 %/K in copper, so a hot motor can be 20-30 % above this
lim.T_motor_active = false;        % see 03_hardware/open-questions.md, Riesgo 4
