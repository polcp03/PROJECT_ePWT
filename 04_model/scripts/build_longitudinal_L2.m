%% BUILD_LONGITUDINAL_L2  Level 1 physics, re-organised into readable blocks.
%
%  NOT new physics. L2 starts as an exact copy of L1, grouped into the four
%  blocks of the C01 deck (Driver+VESC, Motor, Battery, Vehicle), plus two
%  EMPTY hooks for the next steps:
%
%    Launch control hook   pass-through today. Sits between the driver's
%                          current command and the motor.
%    F_grip                still the static value. Load transfer goes here.
%
%  The hooks are deliberately left for Pol to fill (C01 exam, G9 and the
%  L2 questions in 01_plan/C01-exam.md). The agent built the scaffolding
%  only, on request (2026-10-09).
%
%  Regression: run_regression_L1_L2.m must show L2 == L1 until a hook is
%  filled. If it does not, the re-organisation broke something.

here = fileparts(mfilename('fullpath'));
mdir = fullfile(here, '..', 'models');
src = 'longitudinal_L1';
mdl = 'longitudinal_L2';

if bdIsLoaded(mdl), close_system(mdl, 0); end
if bdIsLoaded(src), close_system(src, 0); end
load_system(fullfile(mdir, [src '.slx']));
save_system(src, fullfile(mdir, [mdl '.slx']));   % L2 starts as a copy of L1
close_system(src, 0);
load_system(fullfile(mdir, [mdl '.slx']));

groups = {
    '1 Driver + VESC', {'Throttle 0..1', 'VESC ramp', 'I_motor_max'}
    '2 Motor',         {'Motor + VESC limits'}
    '3 Battery',       {'I_bat prev', 'R_int', 'V_oc', 'V_bat'}
    '4 Vehicle',       {'F_trac', 'F_grip', 'Grip limit', 'F_roll', 'v squared', ...
                        'F_aero', 'Force balance', '1 over m_eq', 'Integrator v', ...
                        'w_m from v'}
    };
for k = 1:size(groups, 1)
    h = cellfun(@(n) get_param([mdl '/' n], 'Handle'), groups{k, 2});
    before = find_system(mdl, 'SearchDepth', 1, 'BlockType', 'SubSystem');
    Simulink.BlockDiagram.createSubsystem(h);
    after = find_system(mdl, 'SearchDepth', 1, 'BlockType', 'SubSystem');
    new = setdiff(after, before);
    set_param(new{1}, 'Name', groups{k, 1});
end

%% Hook 1: launch control, between the driver command and the motor
drv = [mdl '/1 Driver + VESC'];
% (the motor block keeps its name: '2 Motor')
ph = get_param(drv, 'PortHandles');
ln = get_param(ph.Outport(1), 'Line');
dst = get_param(ln, 'DstPortHandle');
delete_line(ln);
lc = [mdl '/Launch control hook'];
add_block('built-in/Subsystem', lc);
add_block('simulink/Sources/In1', [lc '/iq_cmd in'], 'Position', [40 48 70 62]);
add_block('simulink/Sinks/Out1', [lc '/iq_cmd out'], 'Position', [220 48 250 62]);
add_line(lc, 'iq_cmd in/1', 'iq_cmd out/1');
set_param(lc, 'Description', ['L2 HOOK - pass-through today. ', ...
    'Launch control limits the current command while the wheel would slip. ', ...
    'Needs: what signal tells you it is slipping? Pol to design.']);
lph = get_param(lc, 'PortHandles');
add_line(mdl, ph.Outport(1), lph.Inport(1), 'autorouting', 'smart');
for d = dst(:)'
    add_line(mdl, lph.Outport(1), d, 'autorouting', 'smart');
end

%% Hook 2: load transfer, marked on the F_grip block inside the vehicle
set_param([mdl '/4 Vehicle/F_grip'], 'Description', ['L2 HOOK - static rear ', ...
    'load today: mu * x_cg * m * g. Under acceleration the rear normal force ', ...
    'changes. Which extra term, and which parameter is still MISSING for it? ', ...
    'Pol to add (see 01_plan/C01-exam.md, block H).']);
set_param([mdl '/4 Vehicle/F_grip'], 'Name', 'F_grip (static - L2 hook)');

%% Name the ports after the signals they carry, so the top level reads alone
set_param([mdl '/3 Battery/V_bat'], 'Name', 'V_oc - R_int x I_bat');
ports = {
    '1 Driver + VESC', 'Outport', {'iq_cmd'}
    '3 Battery',       'Inport',  {'I_bat'}
    '3 Battery',       'Outport', {'V_bat'}
    '4 Vehicle',       'Inport',  {'T_shaft'}
    '4 Vehicle',       'Outport', {'v', 'w_m', 'F_wheel'}
    };
for k = 1:size(ports, 1)
    for n = 1:numel(ports{k, 3})
        blk = find_system([mdl '/' ports{k, 1}], 'SearchDepth', 1, ...
            'BlockType', ports{k, 2}, 'Port', num2str(n));
        set_param(blk{1}, 'Name', ports{k, 3}{n});
    end
end
subs = find_system(mdl, 'SearchDepth', 1, 'BlockType', 'SubSystem');
for k = 1:numel(subs)
    set_param(subs{k}, 'ContentPreviewEnabled', 'off');
end

Simulink.BlockDiagram.arrangeSystem(mdl);
save_system(mdl);
fprintf('Built %s\n', fullfile(mdir, [mdl '.slx']));
