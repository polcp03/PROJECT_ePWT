%% VEHICLE_PARAMS  Longitudinal dynamics, transmission and DC bus
%
%  Level 1 of the build order in 04_model/CLAUDE.md.
%  Same tagging rules as motor_params.m.
%
%  Sources: 03_hardware/baseline.md, 03_hardware/vesc/MOTOR_1.9.xml
%
%  READ THIS FIRST: almost nothing in this file is measured. The electrical
%  machine is well characterised; the vehicle is not. Level 1 cannot be
%  correlated against 06_data/ until the MISSING entries below are filled.

%% ------------------------------------------------------------------
%% 1. Transmission
%% ------------------------------------------------------------------
% Chain 25H, 11T motor sprocket / 92T rear sprocket. Counted teeth, so this
% is a hard number - the only genuinely MEASURED value in this file.
veh.z_motor      = 11;             % [-] MEASURED
veh.z_wheel      = 92;             % [-] MEASURED
veh.i_gear       = veh.z_wheel / veh.z_motor;   % 8.3636 [-]

% >>> LOGGING HAZARD - status 2026-10-09 <<<
% An older note here said the VESC had si_gear_ratio = 6.5 (the old 72/11
% setup), i.e. speed channels 28 % high. The exports in 03_hardware/vesc/
% (2026-09-09 and the re-export of 2026-10-01) both read si_gear_ratio = 8.363,
% so that note was stale. The 2026-10-01 re-export also fixed
% si_motor_poles 14 -> 6 (p = 3 MEASURED), which DOES enter the speed channel.
% Still open: si_wheel_diameter = 0.30 m on the device vs 2*r_roll = 0.31 m
% here (~3 %). The VESC speed comes from motor rpm, i.e. the REAR (driven)
% wheel, so this needs the rear roll-out, not the front one of 2026-11-06. For logs taken BEFORE 2026-10-01 the poles error applies; the
% factor depends on the formula the firmware uses - check before rescaling.
% (the old 6.5/8.3636 correction factor was removed: it was based on the stale note)

veh.eta_drive    = 0.95;           % [-] ASSUMED (C01) chain + bearings, typical roller chain
veh.eta_drive_range = [0.90 0.97]; % [-] plausible band - replace with coastdown

%% ------------------------------------------------------------------
%% 2. Wheels and tyres
%% ------------------------------------------------------------------
% Rear (driven): 13 x 5.00-6 TR13 on a 6 in rim, pneumatic knobby.
% 13 in nominal -> 330.2 mm outer diameter, 165.1 mm unloaded radius.
veh.d_wheel_nom  = 0.3302;         % [m] MEASURED (nominal tyre size, 13 in)
veh.r_wheel_nom  = veh.d_wheel_nom / 2;        % 165.1 mm

% Loaded rolling radius. NOT the nominal radius.
% Pol's observation 2026-09-07: most of the mass sits on the rear axle and the
% tyres run at low pressure, so the rear tyre visibly squashes ("cae bastante").
% Typical deflection for a low-pressure knobby under this kind of load is
% 5-10 % of the unloaded radius. Taking ~6 %:
veh.r_roll       = 0.155;          % [m] ASSUMED (REAR, driven), 165.1 mm - 6 %
veh.r_roll_range = [0.150 0.160];  % [m] plausible band until measured
% The front roll-out of 2026-11-06 (below) gave 146 mm on the FRONT tyre, a
% different size (4.10 wide, not 5.00) carrying about half the load of a rear
% one. It does not carry over to the rear: r_roll stays ASSUMED until the rear
% wheel is rolled out the same way (mark on the tyre, count turns).

% Front-left loaded rolling radius: the wheel with the Hall speed sensor.
% MEASURED 2026-11-06, Pol seated, straight 4.5 m by tape, 4.9 turns counted
% (49 magnets), pressure ~1.5 bar. r = 4.5 / (4.9 * 2*pi) = 0.1462 m.
% Uncertainty ~+/-2 mm: the last 1/10 turn was read by eye (~1 %).
% Use it for every speed and distance computed from the wheel sensor:
%   one magnet = 2*pi*r_front_roll/10 = 91.7 mm
veh.r_front_roll       = 0.146;            % [m] MEASURED 2026-11-06 (06_data/2026-11-06_rollout)
veh.r_front_roll_range = [0.144 0.148];    % [m] counting resolution
% >>> This is the single most leveraged unmeasured number in the vehicle. <<<
% It divides torque to give tractive force AND multiplies speed, so a 6 % error
% is a 6 % error in predicted acceleration and in predicted top speed at once.
%
% HOW TO MEASURE IT (5 minutes, needs the rear wheels back on):
%   1. Rider seated on the quad, normal tyre pressure.
%   2. Mark the rear tyre and the ground at the contact patch.
%   3. Push the quad in a straight line for exactly 10 wheel revolutions.
%   4. Measure the distance travelled, D.
%   5. r_roll = D / (10 * 2*pi)
% This measures the radius the vehicle actually rolls on, deflection included.
% Rolling, not a ruler: a ruler measures the deformed shape, not the effective
% radius, and those are not the same thing.

%% ------------------------------------------------------------------
%% 3. Masses
%% ------------------------------------------------------------------
% Vehicle mass without rider. History - it was ESTIMATED from two sources:
%   - 45 kg stock platform minus ~5 kg from the lead-acid -> Li-ion swap
%   - Pol lifted the quad 2026-09-07 and judged it "about 40 kg"
% Two independent estimates landing on the same number is worth more than one,
% but neither is a scale. Weigh it when convenient - see the sensitivity note
% at the bottom of this file for how much it is worth.
% 2026-10-08: WEIGHED on a scale -> 38 kg. The 40 kg estimate was 5 % high,
% i.e. inside its own declared +/-5 % band.
veh.m_vehicle    = 38;             % [kg] MEASURED (scale, tyres flat)
veh.m_driver     = 74.5;           % [kg] MEASURED (scale, clothed, 2026-11-06; was 72)
veh.m_total      = veh.m_vehicle + veh.m_driver;   % 112.5 kg

veh.wheelbase    = 0.72;           % [m] MEASURED (tape, hub to hub, 2026-11-06)
veh.track_front  = 0.46;           % [m] MEASURED (tape, tyre centres, 2026-11-06)
veh.track_rear   = 0.44;           % [m] MEASURED (tape, tyre centres, 2026-11-06)
veh.h_cg         = 0.51;           % [m] CG height with rider  ESTIMATED [0.45-0.55]
                                   %     empty 0.31 m MEASURED (tilt test 2026-11-06)
                                   %     + seated rider CG ~0.62 m. See 06_data/2026-11-06_mass-cg
veh.x_cg         = 0.66;           % [-] static rear weight fraction, with rider
                                   %     MEASURED 2026-11-06 (two scales per axle):
                                   %     80.0 / 120.7 kg. Empty quad: 0.50.
veh.x_cg_range   = [0.63 0.69];    % [-] bathroom scales; fractions trusted, kg are not
veh.mu           = 0.60;           % [-] tyre-road peak friction  ASSUMED (C01)
veh.mu_range     = [0.45 0.75];    % [-] dirt / loose ground, where the quad is
                                   %     driven. Textbook order of magnitude, no
                                   %     tyre data. v2 used 0.75 [0.60 0.90] =
                                   %     dry asphalt: wrong surface (Pol, 9 oct)
% Rotating inertia of the 4 wheels, as an equivalent translating mass J/r^2.
% Not weighed, not measured. Order of magnitude only.
veh.m_rot_wheels = 4;              % [kg] ASSUMED (C01)
veh.m_rot_wheels_range = [2 8];    % [kg]

%% ------------------------------------------------------------------
%% 4. Road and aerodynamic loads
%% ------------------------------------------------------------------
veh.Crr          = 0.030;          % [-]     rolling resistance  ASSUMED (C01)
veh.Crr_range    = [0.020 0.045];  % [-]     low-pressure knobby on asphalt; no source measured
veh.CdA          = 0.60;           % [m^2]   drag area          ASSUMED (C01)
veh.CdA_range    = [0.45 0.80];    % [m^2]   upright rider + quad; no CFD, no test
veh.rho_air      = 1.20;           % [kg/m^3] ASSUMED, ~20 degC sea level
veh.g            = 9.81;           % [m/s^2]
veh.slope        = 0;              % [rad]   test surface assumed flat
% Crr and CdA come out of one coastdown test together. At the speeds this quad
% reaches (< 50 km/h) rolling resistance dominates and CdA is weakly observable
% - expect a wide confidence interval on CdA and do not over-trust it.

%% ------------------------------------------------------------------
%% 5. Battery / DC bus
%% ------------------------------------------------------------------
bat.n_series     = 13;             % [-] MEASURED  13S5P
bat.n_parallel   = 5;              % [-] MEASURED
bat.cell         = 'SINC ISR18650-26A';   % Li-ion, no verified datasheet
bat.capacity_Ah  = 13;             % [Ah] ASSUMED (5 x 2.6 Ah nominal)
bat.v_nom        = 48.1;           % [V] 13 x 3.70
bat.v_max        = 54.6;           % [V] 13 x 4.20
bat.v_min        = 39.0;           % [V] 13 x 3.00, matches the VESC cut-off end
bat.R_int        = 0.10;           % [Ohm] pack internal resistance  ASSUMED (C01)
bat.R_int_range  = [0.06 0.15];    % [Ohm] no cell datasheet; needs V-sag vs I from logs
bat.OCV_soc      = NaN;            % [V] OCV vs SoC curve            MISSING
% R_int is what turns a battery-current limit into a voltage sag, which is what
% actually clips available torque at high current. Without it the model will
% predict a stiffer bus than reality and overstate peak performance.

%% ------------------------------------------------------------------
%% 6. Derived quantities
%% ------------------------------------------------------------------
veh.v_per_wrad = veh.r_roll / veh.i_gear;      % [m/s per motor rad/s]
veh.F_per_Nm   = veh.i_gear / veh.r_roll;      % [N per Nm of motor torque]

% Vehicle inertia seen from the motor shaft, i.e. the translating mass turned
% into an equivalent rotating inertia:  J_eq = m * r_roll^2 / i_gear^2
veh.J_equiv    = veh.m_total * veh.r_roll^2 / veh.i_gear^2;   % ~0.0378 kg*m^2 (110 kg)

%% ------------------------------------------------------------------
%% 7. WHERE THE MODEL ERROR ACTUALLY COMES FROM
%% ------------------------------------------------------------------
% Run this once mot is loaded (motor_params.m) and the priorities are obvious:
%
%   rotor inertia            1.558e-4 kg*m^2      0.4 % of the total
%   vehicle, seen from motor 3.78e-2  kg*m^2     99.6 % of the total
%
% The rotor is 250 times lighter than the vehicle it has to accelerate. So:
%   - refining J_rotor beyond its current +/-14 % changes the answer by 0.06 %
%   - a 10 % error in m_total or r_roll changes it by 10 %
%
% Sensitivity of predicted acceleration, in descending order:
%   r_roll     +/-6 %   ASSUMED   <- REAR roll-out still to do (front done 2026-11-06: 146 mm)
%   m_total    done     MEASURED  2026-10-08, scale (38 + 72 kg)
%   Crr        range    ASSUMED   <- coastdown
%   eta_drive  range    ASSUMED   <- coastdown
%   CdA        range    ASSUMED   <- coastdown, weakly observable below 50 km/h
%   J_rotor    +/-14 %  MEASURED  <- already far better than needed
% The full one-at-a-time sweep over these ranges, with numbers, is in
% 04_model/results/C01_predictions_table.md (scripts/run_predictions_L1.m).
%
% Every hour spent on the motor from here buys less than a minute spent on the
% chassis. The machine is now the best-characterised part of this vehicle.
