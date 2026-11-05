"""Build the artifact page and the two standalone repo SVGs from draw.py's fragments.

usage: python build.py <frag_dir> <page.html> <repo_docs_dir or ->
"""
import io, os, sys

frag_dir, page, repo = sys.argv[1], sys.argv[2], sys.argv[3]
arch = io.open(os.path.join(frag_dir, "arch.svgfrag"), encoding="utf-8").read()
schem = io.open(os.path.join(frag_dir, "schem.svgfrag"), encoding="utf-8").read()

LIGHT = """--paper:#ffffff; --bg:#f4f6f8; --fg:#121820; --muted:#566273; --line:#c9d0da; --soft:#eef1f6;
  --hv:#fff4f2; --lv:#f1f6ff; --hvline:#e4a79c; --lvline:#9db7e6;
  --pwr:#c62828; --phase:#8e24aa; --mech:#6b7280; --sig:#1f5fd6; --can:#0a8a5a; --warn:#a14b00;
  --ok:#0f7a4a; --plan:#9a5b00;"""
DARK = """--paper:#141a21; --bg:#0e1217; --fg:#e6eaf0; --muted:#9aa6b6; --line:#334050; --soft:#1b222c;
  --hv:#22181a; --lv:#151c29; --hvline:#8a4a40; --lvline:#3d5a8c;
  --pwr:#ff7a6e; --phase:#d58cf0; --mech:#9aa3b0; --sig:#7aa7ff; --can:#3fd49a; --warn:#ffb15c;
  --ok:#4ade80; --plan:#fbbf24; color-scheme:dark;"""

# Drawing classes, shared by the page and the standalone SVGs
DRAW = """
.paper { fill:var(--paper); }
.comp { fill:var(--soft); stroke:var(--fg); stroke-width:1.6; }
.comp.plan { stroke-dasharray:6 4; }
.board, .notes { fill:none; stroke:var(--line); stroke-width:1.2; stroke-dasharray:4 3; }
.title { fill:var(--soft); stroke:var(--fg); stroke-width:1.4; }
.tline { fill:none; stroke:var(--fg); stroke-width:1; }
.wire, .stub { fill:none; stroke:var(--fg); stroke-width:1.6; stroke-linejoin:round; }
.wire.plan { stroke-dasharray:6 4; }
.wire.can { stroke:var(--can); stroke-width:2.2; }
.sym, .plate { stroke:var(--fg); stroke-width:1.6; fill:none; }
.plate { stroke-width:2.4; }
.part { fill:var(--paper); stroke:var(--fg); stroke-width:1.6; }
.pinc { fill:var(--paper); stroke:var(--fg); stroke-width:1.4; }
.dot { fill:var(--fg); }
.diode { fill:var(--fg); }
text { fill:var(--fg); }
.lbl { font-size:11.5px; fill:var(--muted); }
.net { font-size:11px; font-weight:600; letter-spacing:.04em; fill:var(--sig); }
.ref { font-size:11.5px; font-weight:700; fill:var(--fg); }
.val { font-size:11px; fill:var(--muted); }
.icname { font-size:13px; font-weight:700; }
.pinl { font-size:11px; font-family:"IBM Plex Mono", Consolas, monospace; }
.pinn { font-size:9.5px; fill:var(--muted); font-family:"IBM Plex Mono", Consolas, monospace; }
.warn { font-size:11px; font-style:italic; fill:var(--warn); }
.note { font-size:12px; }
.ttl { font-size:15px; font-weight:700; }
.tsm { font-size:11.5px; fill:var(--muted); }
.t { font-size:13px; font-weight:700; }
.s { font-size:11px; fill:var(--muted); }
.dom { font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; fill:var(--muted); }
.domain { stroke-width:1.4; stroke-dasharray:8 5; }
.domain.hv { fill:var(--hv); stroke:var(--hvline); }
.domain.lv { fill:var(--lv); stroke:var(--lvline); }
.blk { fill:var(--paper); stroke:var(--fg); stroke-width:1.4; }
.blk.ext, .blk.planc { stroke-dasharray:5 4; }
.blk.vcu { stroke-width:2.4; }
.pwr { fill:none; stroke:var(--pwr); stroke-width:4; }
.pwr.thin { stroke-width:2.2; }
.phase { fill:none; stroke:var(--phase); stroke-width:3; }
.mech { fill:none; stroke:var(--mech); stroke-width:5; stroke-linecap:round; }
.sig { fill:none; stroke:var(--sig); stroke-width:1.8; }
.can { fill:none; stroke:var(--can); stroke-width:2.6; }
.plan { stroke-dasharray:6 4; }
.radio { fill:none; stroke:var(--muted); stroke-width:1.6; stroke-dasharray:2 4; }
.ahp { fill:var(--sig); }
.ahc { fill:var(--can); }
"""

def standalone(svg):
    style = f"<style>svg{{{LIGHT}}}{DRAW}</style>"
    return svg.replace("<defs>", style + "<defs>", 1)

if repo != "-":
    io.open(os.path.join(repo, "vehicle-architecture.svg"), "w", encoding="utf-8").write(standalone(arch))
    io.open(os.path.join(repo, "vcu-schematic.svg"), "w", encoding="utf-8").write(standalone(schem))

pins = [
    ("34", "Wheel speed", "sig", "digital · interrupt", "H1 3144 Hall, front wheel",
     "R3 10 kΩ to +3V3 (GPIO 34 has no internal pull-up). C1 100 nF at the sensor.", "wired"),
    ("35", "Throttle", "ana", "analog · ADC1", "J2 Hall grip",
     "Grip powered from +3V3: 0.80 V rest, 2.60 V full, no divider. RC filter R4 1 k + C2 100 nF (1.6 kHz). R5 100 k pull-down: a cut wire reads 0 V. Out of window → zero torque.", "planned"),
    ("32", "Brake, left", "sig", "digital · active low", "SW1 on/off switch",
     "Switch to GND. R6 10 kΩ to +3V3 + C3 100 nF. Debounce 10–20 ms in code.", "planned"),
    ("33", "Brake, right", "sig", "digital · active low", "SW2 on/off switch", "R7 + C4, same as GPIO 32.", "planned"),
    ("21 · 22", "IMU SDA · SCL", "bus", "I2C", "U4 LSM6DS3, 0x6A",
     "R8 / R9 10 kΩ to +3V3, unless the module has them. C5 100 nF.", "planned"),
    ("14 · 13 · 26 · 27", "CAN SCK · SI · CS · SO", "bus", "SPI (HSPI) 4 MHz", "U2 MCP2515 + TJA1050",
     "SO is 5 V: R1 1 k / R2 2 k divider into GPIO 27. INT not used.", "wired"),
    ("18 · 19 · 23 · 5", "SD SCK · MISO · MOSI · CS", "bus", "SPI (VSPI)", "U3 microSD module",
     "GPIO 5 is a boot strap pin; fine, CS idles high.", "wired"),
    ("0 · 2", "BOOT · LED", "brd", "on the board", "DevKit", "Start/stop the log · idle/rec/error.", "wired"),
]
cards = "\n".join(
    f'<li class="pin"><div class="gpio">{g}</div><div class="body">'
    f'<div class="row"><strong>{s}</strong><span class="chip {c}">{t}</span>'
    f'<span class="st {st}">{st}</span></div>'
    f'<div class="dev">{d}</div><div class="cond">{cond}</div></div></li>'
    for g, s, c, t, d, cond, st in pins)

css = f"""
/* Layout: drawing sheets, full width and scrollable; reference notes below in one column */
:root {{ {LIGHT}
  --sans:"IBM Plex Sans", "Segoe UI", Helvetica, Arial, sans-serif;
  --mono:"IBM Plex Mono", Consolas, Menlo, monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {DARK} }} }}
:root[data-theme="dark"] {{ {DARK} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.55 var(--sans); }}
main {{ max-width:1300px; margin:0 auto; padding-block:24px 48px;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px));
  display:grid; gap:32px; }}
main > * {{ min-width:0; }}
h1 {{ font-size:26px; margin:0; text-wrap:balance; }}
h2 {{ font-size:14px; margin:0 0 10px; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); }}
p {{ margin:0; max-width:72ch; }}
.lede {{ color:var(--muted); }}
figure {{ margin:0; display:grid; gap:8px; }}
.sheet {{ overflow-x:auto; border:1px solid var(--line); border-radius:6px; background:var(--paper); }}
.sheet svg {{ display:block; min-width:1100px; width:100%; height:auto; }}
figcaption {{ font-size:14px; color:var(--muted); max-width:90ch; }}
{DRAW}
.narrow {{ max-width:900px; display:grid; gap:28px; }}
ul.pins {{ list-style:none; margin:0; padding:0; display:grid; gap:8px; }}
li.pin {{ display:grid; grid-template-columns:140px 1fr; gap:12px; background:var(--paper);
  border:1px solid var(--line); border-radius:6px; padding:10px 12px; }}
.gpio {{ font:600 14px/1.3 var(--mono); }}
.body {{ min-width:0; display:grid; gap:2px; }}
.row {{ display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; }}
.dev {{ color:var(--muted); font-size:13px; }}
.cond {{ font-size:14px; }}
.chip {{ font:600 11px/1 var(--mono); padding:4px 7px; border-radius:4px; border:1.5px solid currentColor; }}
.chip.sig {{ color:var(--sig); }} .chip.ana {{ color:var(--warn); }} .chip.bus {{ color:var(--phase); }}
.chip.brd {{ color:var(--muted); }}
.st {{ font:600 11px/1 var(--mono); text-transform:uppercase; letter-spacing:.05em; }}
.st.wired {{ color:var(--ok); }} .st.planned {{ color:var(--plan); }}
.tablewrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:420px; font-size:14px; background:var(--paper); }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:12px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }}
td.n {{ font-family:var(--mono); white-space:nowrap; font-variant-numeric:tabular-nums; }}
ol.check {{ margin:0; padding-left:22px; display:grid; gap:8px; max-width:75ch; }}
.tocard {{ display:grid; gap:2px; margin-top:6px; padding:12px 14px; border:1px solid var(--sig); border-radius:6px;
  background:var(--paper); color:var(--fg); text-decoration:none; max-width:72ch; }}
.tocard strong {{ color:var(--sig); }} .tocard span {{ font-size:14px; color:var(--muted); }}
.note2 {{ font-size:13px; color:var(--muted); margin-top:8px; }}
@media (max-width:560px) {{ li.pin {{ grid-template-columns:1fr; gap:4px; }} }}
"""

html = f"""<title>ePWT VCU Pinout</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>{css}</style>
<main>
<header style="display:grid;gap:6px">
  <h1>ePWT electrical architecture</h1>
  <p class="lede">Two sheets. Sheet 1 is the whole quad: power, mechanics, sensors and the two ground domains. Sheet 2 is the vehicle control unit wired part by part. Rev B, 5 November 2026 (throttle on 3V3 with an RC filter), DEC-005. On a phone, swipe each sheet sideways.</p>
  <a class="tocard" href="perfboard.html"><strong>Sheet 3 · Perfboard layout →</strong><span>The same VCU hole by hole, interactive: tap a wire or a part to see what it is. Build order and parts list.</span></a>
</header>

<figure>
  <div class="sheet">{arch}</div>
  <figcaption><strong>Sheet 1 · Vehicle.</strong> The pack feeds the VESC directly on the positive side and through the BMS on the negative side (common-port BMS). The VESC keeps the rotor Halls and gets the new motor NTC. Everything the VCU reads lives in a separate low-voltage domain on its own 12 V battery; CAN is the only wire between the two domains. Main fuse and main switch are not in the hardware records.</figcaption>
</figure>

<figure>
  <div class="sheet">{schem}</div>
  <figcaption><strong>Sheet 2 · VCU.</strong> Every connection drawn. Power pins end in rail symbols (+5V, +3V3) and ground symbols, so each one is a real wire to that net. Crossing lines without a dot do not connect. Dashed parts are planned; solid parts are on the bench today.</figcaption>
</figure>

<div class="narrow">
<section>
  <h2>Pin by pin</h2>
  <ul class="pins">
{cards}
  </ul>
  <p class="note2"><strong>Free:</strong> 36, 39 (analog in) · 4, 16, 17, 25. <strong>Never:</strong> 6–11 (flash), 1 / 3 (USB serial), 12 (boot strap), any ADC2 pin for analog with Wi-Fi on.</p>
</section>

<section>
  <h2>Throttle from +3V3, filter R4 1 k + C2 100 nF</h2>
  <div class="tablewrap"><table>
    <thead><tr><th>Throttle out</th><th>At GPIO 35</th><th>Code does</th></tr></thead>
    <tbody>
      <tr><td class="n">signal cut</td><td class="n">0 V (R5)</td><td>out of window → zero torque</td></tr>
      <tr><td class="n">0.80 V (rest)</td><td class="n">0.80 V</td><td>zero demand (≤ 0.90 V)</td></tr>
      <tr><td class="n">2.60 V (full)</td><td class="n">2.60 V</td><td>full demand (≥ 2.55 V). Just above the 2.45 V linear limit: calibrated, so it is read correctly</td></tr>
      <tr><td class="n">short to 3V3, or GND cut</td><td class="n">~3.3 V</td><td>out of window (&gt; 2.80 V) → zero torque. Below the 3.6 V absolute max</td></tr>
    </tbody>
  </table></div>
  <p class="note2">Measured 2026-11-05. The filter cuts the inverter's 30 kHz PWM by ~19× before the ADC; a software filter alone cannot, because slow sampling aliases it. R5 value to check: rest and full readings must not move more than 10 mV with it fitted.</p>
</section>

<section>
  <h2>Before wiring anything new</h2>
  <ol class="check">
    <li><strong>Throttle:</strong> measured 2026-11-05 on +3V3: 0.80 V rest, 2.60 V full. Keep it unplugged from the VESC ADC: tied to both, it makes a second ground path.</li>
    <li><strong>Brakes:</strong> check each switch is a dry contact (no voltage from the old 36 V system) and whether it is normally open. With normally open, a cut wire reads “not braking” and silently drops the brake + throttle check.</li>
    <li><strong>VESC:</strong> CAN timeout 100 ms, tested 2026-11-05 with the wheel in the air: 105–121 ms over 5 runs (REQ-VCU-03).</li>
    <li><strong>Motor NTC:</strong> wire it to TEMP and GND of the VESC Hall plug (check the pin on the board) and set its beta in VESC Tool.</li>
    <li><strong>5 V budget:</strong> the DC-DC rating is not recorded. Check it covers the ESP32 with Wi-Fi (~250 mA peaks) plus the modules.</li>
  </ol>
</section>
</div>
</main>
"""
io.open(page, "w", encoding="utf-8").write(html)

# preview file: same page with a light body, for a headless screenshot
io.open(page.replace(".html", "_preview.html"), "w", encoding="utf-8").write(
    "<!doctype html><meta charset='utf-8'>" + html)
