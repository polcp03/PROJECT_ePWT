"""Generate the two ePWT drawings as SVG fragments styled by class.

Sheet 1: vehicle architecture (power, mechanical, signal paths, ground domains).
Sheet 2: VCU wiring schematic, every connection, with reference designators.
"""
import io, sys

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class Sheet:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.o = w, h, label, []

    def add(self, s):
        self.o.append(s)

    # primitives --------------------------------------------------------
    def line(self, pts, cls="wire"):
        d = " ".join(f"{x},{y}" for x, y in pts)
        m = ""
        if "arrow" in cls.split():
            m = ' marker-end="url(#ahc)"' if "can" in cls.split() else ' marker-end="url(#ah)"'
        self.add(f'<polyline class="{cls}" points="{d}"{m}/>')

    def rect(self, x, y, w, h, cls="comp", rx=0):
        self.add(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def text(self, x, y, s, cls="lbl", anchor="start"):
        self.add(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(s)}</text>')

    def dot(self, x, y):
        self.add(f'<circle class="dot" cx="{x}" cy="{y}" r="3.2"/>')

    def svg(self):
        defs = ('<defs>'
                '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path class="ahp" d="M0,0 L10,5 L0,10 z"/></marker>'
                '<marker id="ahc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                '<path class="ahc" d="M0,0 L10,5 L0,10 z"/></marker>'
                '</defs>')
        body = "\n".join(self.o)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{esc(self.label)}" font-family="IBM Plex Sans, Segoe UI, Arial, sans-serif">'
                f'{defs}<rect class="paper" x="0" y="0" width="{self.w}" height="{self.h}"/>{body}</svg>')

    # schematic symbols -------------------------------------------------
    def gnd(self, x, y, cls="wire"):
        self.line([(x, y), (x, y + 8)], cls)
        self.add(f'<line class="sym" x1="{x-10}" y1="{y+8}" x2="{x+10}" y2="{y+8}"/>'
                 f'<line class="sym" x1="{x-6}" y1="{y+12}" x2="{x+6}" y2="{y+12}"/>'
                 f'<line class="sym" x1="{x-2}" y1="{y+16}" x2="{x+2}" y2="{y+16}"/>')

    def rail(self, x, y, name, cls="wire"):
        self.line([(x, y), (x, y - 10)], cls)
        self.add(f'<line class="sym" x1="{x-9}" y1="{y-10}" x2="{x+9}" y2="{y-10}"/>')
        self.text(x, y - 15, name, "net", "middle")

    def res_v(self, x, y1, y2, ref, val, cls="wire", side="r"):
        m = (y1 + y2) / 2
        self.line([(x, y1), (x, m - 15)], cls)
        self.line([(x, m + 15), (x, y2)], cls)
        self.add(f'<rect class="part" x="{x-5}" y="{m-15}" width="10" height="30"/>')
        if side == "r":
            self.text(x + 9, m - 2, ref, "ref"); self.text(x + 9, m + 11, val, "val")
        else:
            self.text(x - 9, m - 2, ref, "ref", "end"); self.text(x - 9, m + 11, val, "val", "end")

    def res_h(self, x1, x2, y, ref, val, cls="wire"):
        m = (x1 + x2) / 2
        self.line([(x1, y), (m - 15, y)], cls)
        self.line([(m + 15, y), (x2, y)], cls)
        self.add(f'<rect class="part" x="{m-15}" y="{y-5}" width="30" height="10"/>')
        self.text(m, y - 10, f"{ref} {val}", "ref", "middle")

    def cap_v(self, x, y1, y2, ref, val, cls="wire", side="r"):
        m = (y1 + y2) / 2
        self.line([(x, y1), (x, m - 3)], cls)
        self.line([(x, m + 3), (x, y2)], cls)
        self.add(f'<line class="plate" x1="{x-9}" y1="{m-3}" x2="{x+9}" y2="{m-3}"/>'
                 f'<line class="plate" x1="{x-9}" y1="{m+3}" x2="{x+9}" y2="{m+3}"/>')
        if side == "r":
            self.text(x + 13, m - 2, ref, "ref"); self.text(x + 13, m + 11, val, "val")
        else:
            self.text(x - 13, m - 2, ref, "ref", "end"); self.text(x - 13, m + 11, val, "val", "end")

    def switch_h(self, x1, x2, y, ref, val, cls="wire"):
        self.add(f'<circle class="pinc" cx="{x1}" cy="{y}" r="3"/><circle class="pinc" cx="{x2}" cy="{y}" r="3"/>'
                 f'<line class="sym" x1="{x1+3}" y1="{y-1}" x2="{x2-4}" y2="{y-14}"/>')
        self.text((x1 + x2) / 2, y + 18, ref, "ref", "middle")
        self.text((x1 + x2) / 2, y + 30, val, "val", "middle")

    def nc(self, x, y):
        self.add(f'<line class="sym" x1="{x-5}" y1="{y-5}" x2="{x+5}" y2="{y+5}"/>'
                 f'<line class="sym" x1="{x-5}" y1="{y+5}" x2="{x+5}" y2="{y-5}"/>')

    def ic(self, x, y, w, h, ref, name, left=(), right=(), cls="comp", sub=None):
        """Box with pins. left/right: (pin label, y, pin number or '').
        Returns dict label -> outer pin end."""
        self.rect(x, y, w, h, cls)
        self.text(x, y - 8, ref, "ref")
        self.text(x + w / 2, y + 18, name, "icname", "middle")
        if sub:
            self.text(x + w / 2, y + 32, sub, "val", "middle")
        p = {}
        for lab, py, num in left:
            self.add(f'<line class="stub" x1="{x-20}" y1="{py}" x2="{x}" y2="{py}"/>')
            self.text(x + 6, py + 4, lab, "pinl")
            if num != "":
                self.text(x - 4, py - 4, str(num), "pinn", "end")
            p[lab] = (x - 20, py)
        for lab, py, num in right:
            self.add(f'<line class="stub" x1="{x+w}" y1="{py}" x2="{x+w+20}" y2="{py}"/>')
            self.text(x + w - 6, py + 4, lab, "pinl", "end")
            if num != "":
                self.text(x + w + 4, py - 4, str(num), "pinn")
            p[lab] = (x + w + 20, py)
        return p


# ======================================================================
# Sheet 2 — VCU wiring schematic
# ======================================================================
def schematic():
    s = Sheet(1260, 1020, "VCU wiring schematic: ESP32, CAN controller, microSD, wheel Hall, throttle, "
                          "two brake switches and IMU, with every pull-up, divider and decoupling part")
    P = "wire plan"   # planned, not yet wired

    # U1 ESP32 ---------------------------------------------------------
    L = [("5V", 150, ""), ("GND", 190, ""), ("3V3", 250, ""),
         ("GPIO34", 320, ""), ("GPIO35", 400, ""), ("GPIO32", 540, ""),
         ("GPIO33", 660, ""), ("GPIO21", 790, ""), ("GPIO22", 830, "")]
    R = [("GPIO14", 160, ""), ("GPIO13", 200, ""), ("GPIO26", 240, ""), ("GPIO27", 280, ""),
         ("GPIO18", 420, ""), ("GPIO19", 460, ""), ("GPIO23", 500, ""), ("GPIO5", 540, ""),
         ("GPIO0", 680, ""), ("GPIO2", 740, "")]
    u1 = s.ic(520, 110, 200, 750, "U1", "ESP32-DevKit", L, R, sub="WROOM-32 · 3.3 V logic")
    s.text(620, 880, "pins drawn by function, not by header position", "val", "middle")

    # U1 power pins
    x, y = u1["5V"]; s.line([(x, y), (470, y)]); s.rail(470, y, "+5V")
    x, y = u1["GND"]; s.line([(x, y), (470, y)]); s.gnd(470, y)
    x, y = u1["3V3"]; s.line([(x, y), (470, y)]); s.rail(470, y, "+3V3")

    # J1 aux battery + U5 DC-DC ---------------------------------------
    s.ic(40, 80, 90, 80, "J1", "12 V aux", right=[("+", 105, ""), ("−", 140, "")], sub="battery")
    u5 = s.ic(220, 70, 110, 100, "U5", "DC-DC", left=[("IN+", 105, ""), ("IN−", 140, "")],
              right=[("OUT+", 105, ""), ("OUT−", 140, "")], sub="set 5.3 V")
    s.line([(150, 105), (200, 105)]); s.line([(150, 140), (200, 140)])
    s.line([(350, 105), (380, 105)]); s.rail(380, 105, "+5V")
    s.line([(350, 140), (380, 140)]); s.gnd(380, 140)
    s.text(275, 190, "rating not recorded", "warn", "middle")

    # H1 wheel Hall -----------------------------------------------------
    s.ic(150, 270, 100, 80, "H1", "3144 Hall", left=[("VCC", 300, 1), ("GND", 335, 2)],
         right=[("OUT", 320, 3)])
    s.text(200, 366, "front wheel, 10 magnets", "val", "middle")
    s.line([(130, 300), (90, 300)]); s.rail(90, 300, "+5V")
    s.cap_v(90, 300, 335, "C1", "100n", side="l"); s.dot(90, 300)
    s.line([(130, 335), (90, 335)]); s.gnd(90, 335); s.dot(90, 335)
    s.line([(270, 320), (500, 320)])
    s.res_v(420, 320, 270, "R3", "10k"); s.rail(420, 270, "+3V3"); s.dot(420, 320)
    s.text(300, 314, "WHEEL", "net")

    # J2 throttle (planned) ---------------------------------------------
    s.ic(140, 400, 100, 85, "J2", "Throttle", right=[("+5V", 437, 1), ("SIG", 455, 2), ("GND", 473, 3)],
         cls="comp plan", sub="Hall grip")
    s.line([(260, 437), (275, 437)], P); s.rail(275, 437, "+5V", P)
    s.line([(260, 473), (275, 473)], P); s.gnd(275, 473, P)
    s.line([(260, 455), (300, 455), (300, 400), (310, 400)], P)
    s.res_h(310, 370, 400, "R4", "10k", P)
    s.line([(370, 400), (500, 400)], P)
    s.dot(390, 400); s.res_v(390, 400, 470, "R5", "12k", P, side="l"); s.gnd(390, 470, P)
    s.dot(455, 400); s.cap_v(455, 400, 470, "C2", "100n", P); s.gnd(455, 470, P)
    s.text(470, 393, "THR ×0.545", "net", "end")
    s.text(140, 503, "unplug from VESC ADC", "warn")

    # SW1 / SW2 brakes (planned) ----------------------------------------
    for i, (gp, yb, name) in enumerate([("GPIO32", 540, "brake left"), ("GPIO33", 660, "brake right")]):
        n = i + 1
        rref, cref = f"R{6+i}", f"C{3+i}"
        s.line([(170, yb), (170, yb + 20)], P); s.gnd(170, yb + 20, P)
        s.line([(170, yb), (205, yb)], P)
        s.switch_h(205, 265, yb, f"SW{n}", name + ", NO?")
        s.line([(265, yb), (500, yb)], P)
        s.dot(350, yb); s.res_v(350, yb, yb - 50, rref, "10k", P, side="l"); s.rail(350, yb - 50, "+3V3", P)
        s.dot(420, yb); s.cap_v(420, yb, yb + 50, cref, "100n", P); s.gnd(420, yb + 50, P)
        s.text(490, yb - 6, f"BRK_{'L' if n == 1 else 'R'}", "net", "end")

    # U4 IMU (planned) --------------------------------------------------
    s.ic(130, 770, 120, 85, "U4", "LSM6DS3", left=[("VCC", 815, ""), ("GND", 840, "")],
         right=[("SDA", 790, ""), ("SCL", 830, "")], cls="comp plan", sub="I2C 0x6A")
    s.line([(110, 815), (80, 815)], P); s.rail(80, 815, "+3V3", P)
    s.cap_v(80, 815, 840, "C5", "100n", P, side="l"); s.dot(80, 815)
    s.line([(110, 840), (80, 840)], P); s.gnd(80, 840, P); s.dot(80, 840)
    s.line([(270, 790), (500, 790)], P)
    s.line([(270, 830), (500, 830)], P)
    s.dot(460, 790); s.res_v(460, 790, 740, "R8", "10k", P); s.rail(460, 740, "+3V3", P)
    s.dot(380, 830); s.res_v(380, 830, 740, "R9", "10k", P); s.rail(380, 740, "+3V3", P)
    s.text(290, 784, "SDA", "net"); s.text(290, 824, "SCL", "net")
    s.text(130, 885, "skip R8/R9 if the module has them", "warn")

    # U2 MCP2515 --------------------------------------------------------
    u2 = s.ic(860, 95, 150, 245, "U2", "MCP2515 + TJA1050",
              left=[("SCK", 160, ""), ("SI", 200, ""), ("CS", 240, ""), ("SO", 280, ""), ("INT", 305, "")],
              right=[("VCC", 140, ""), ("CANH", 200, ""), ("CANL", 240, ""), ("GND", 320, "")],
              sub="5 V module")
    s.text(950, 290, "J1 = 120 Ω fitted", "val", "middle")
    s.line([(1030, 140), (1050, 140)]); s.rail(1050, 140, "+5V")
    s.line([(1030, 320), (1050, 320)]); s.gnd(1050, 320)
    for gp, lab in [("GPIO14", "SCK"), ("GPIO13", "SI"), ("GPIO26", "CS")]:
        s.line([u1[gp], u2[lab]])
    s.line([(740, 280), (780, 280)])
    s.dot(780, 280); s.res_h(780, 840, 280, "R1", "1k")
    s.res_v(780, 280, 340, "R2", "2k", side="l"); s.gnd(780, 340)
    s.nc(840, 305)
    s.text(760, 274, "SO 3.3 V", "net", "middle")

    # J5 CAN to VESC
    j5 = s.ic(1100, 160, 110, 150, "J5", "to VESC CAN",
              left=[("CAH", 200, ""), ("CAL", 240, ""), ("− (GND)", 270, ""), ("5V", 295, "")])
    s.line([u2["CANH"], j5["CAH"]], "wire can")
    s.line([u2["CANL"], j5["CAL"]], "wire can")
    s.line([(1080, 270), (1068, 270)]); s.gnd(1068, 270)
    s.nc(1080, 295)
    s.text(1055, 224, "500 kbit/s", "net", "middle")
    s.text(1155, 330, "VESC 5V pin unused", "val", "middle")

    # U3 microSD --------------------------------------------------------
    u3 = s.ic(860, 380, 150, 220, "U3", "microSD module",
              left=[("SCK", 420, ""), ("MISO", 460, ""), ("MOSI", 500, ""), ("CS", 540, "")],
              right=[("VCC", 430, ""), ("GND", 570, "")], sub="own 3.3 V reg.")
    s.line([(1030, 430), (1050, 430)]); s.rail(1050, 430, "+5V")
    for gp, lab in [("GPIO18", "SCK"), ("GPIO19", "MISO"), ("GPIO23", "MOSI"), ("GPIO5", "CS")]:
        s.line([u1[gp], u3[lab]])
    s.line([(1030, 570), (1050, 570)]); s.gnd(1050, 570)
    s.text(780, 414, "VSPI", "net", "middle"); s.text(780, 154, "HSPI 4 MHz", "net", "middle")

    # on-board parts
    s.rect(760, 630, 200, 140, "board")
    s.text(770, 648, "on the DevKit board", "val")
    s.line([(740, 680), (790, 680)])
    s.switch_h(790, 840, 680, "SW3", "BOOT")
    s.line([(840, 680), (900, 680), (900, 700)]); s.gnd(900, 700)
    s.line([(740, 740), (780, 740)])
    s.res_h(780, 840, 740, "R", "", "wire")
    s.add('<polygon class="diode" points="850,732 850,748 864,740"/><line class="sym" x1="864" y1="732" x2="864" y2="748"/>')
    s.line([(840, 740), (850, 740)]); s.line([(864, 740), (920, 740), (920, 750)]); s.gnd(920, 750)
    s.text(857, 762, "LED", "val", "middle")

    # notes + title block
    s.rect(40, 910, 760, 95, "notes")
    notes = ["1  Dashed = planned, not wired yet. Solid = on the bench today (2026-11-01).",
             "2  Every pull-up goes to +3V3, never +5V: ESP32 inputs are not 5 V tolerant.",
             "3  GND is one net. It meets the vehicle only at J5 pin − (CAN ground), DEC-004.",
             "4  To confirm: throttle full-scale, brake NO/NC and dry contact, DC-DC rating."]
    for i, n in enumerate(notes):
        s.text(52, 932 + i * 19, n, "note")
    s.rect(830, 910, 390, 95, "title")
    s.line([(830, 942), (1220, 942)], "tline"); s.line([(830, 974), (1220, 974)], "tline")
    s.line([(1080, 942), (1080, 1005)], "tline")
    s.text(842, 932, "ePWT · VCU wiring schematic", "ttl")
    s.text(842, 963, "Sheet 2 of 2 · Rev A", "tsm"); s.text(1092, 963, "2026-11-02", "tsm")
    s.text(842, 995, "Drawn: Claude · Checked: Pol (open)", "tsm"); s.text(1092, 995, "DEC-005", "tsm")
    return s.svg()


# ======================================================================
# Sheet 1 — vehicle architecture
# ======================================================================
def architecture():
    s = Sheet(1260, 720, "Vehicle architecture: high-voltage power path from pack through BMS and VESC to motor, "
                         "chain and rear axle; signals into the VESC and the VCU; CAN as the only link "
                         "between the two ground domains")

    # domains
    s.rect(20, 40, 940, 290, "domain hv", 10)
    s.text(36, 62, "HV domain · 13S pack, 39–54.6 V", "dom")
    s.rect(20, 390, 1220, 280, "domain lv", 10)
    s.text(36, 412, "LV domain · floats on its own 12 V battery", "dom")

    # power path
    s.rect(40, 90, 150, 100, "blk"); s.text(115, 112, "Battery pack", "t", "middle")
    s.text(115, 130, "13S5P · 65 cells", "s", "middle"); s.text(115, 146, "48 V · ~13 Ah", "s", "middle")
    s.text(115, 162, "≈ 0.18 Ω", "s", "middle")
    s.rect(270, 130, 150, 80, "blk"); s.text(345, 152, "BMS", "t", "middle")
    s.text(345, 170, "JK-BD4A17S4P", "s", "middle"); s.text(345, 186, "40 A cont. · backup", "s", "middle")
    s.text(345, 202, "untouched", "s", "middle")
    s.rect(500, 90, 220, 220, "blk"); s.text(610, 112, "VESC", "t", "middle")
    s.text(610, 130, "Flipsky 6.7 Mini Pro · FW 7.01", "s", "middle")
    s.text(610, 146, "FOC, current control", "s", "middle")
    s.text(610, 162, "40 A battery · ±120 A motor", "s", "middle")
    s.text(610, 178, "CAN ID 15", "s", "middle")
    s.rect(800, 90, 140, 100, "blk"); s.text(870, 112, "PMSM", "t", "middle")
    s.text(870, 130, "inner rotor · p = 3", "s", "middle"); s.text(870, 146, "λm 16.9 mWb", "s", "middle")
    s.text(870, 162, "Kt 0.076 Nm/A", "s", "middle")
    s.rect(1020, 90, 200, 70, "blk"); s.text(1120, 112, "Chain 11T / 92T", "t", "middle")
    s.text(1120, 130, "i = 8.364 · 25H", "s", "middle")
    s.rect(1020, 220, 200, 80, "blk"); s.text(1120, 242, "Rear axle, rigid", "t", "middle")
    s.text(1120, 260, "2 driven wheels", "s", "middle"); s.text(1120, 276, "r_roll ≈ 155 mm (assumed)", "s", "middle")

    s.line([(190, 105), (500, 105)], "pwr"); s.text(345, 99, "DC+ (pack +)", "lbl", "middle")
    s.line([(190, 160), (270, 160)], "pwr"); s.text(230, 154, "B−", "lbl", "middle")
    s.line([(420, 160), (500, 160)], "pwr"); s.text(460, 154, "P−", "lbl", "middle")
    s.line([(190, 180), (230, 180), (230, 195), (270, 195)], "sig")
    s.text(198, 232, "13 balance + 2 NTC", "lbl")
    for i, (ph, y) in enumerate([("A", 115), ("B", 135), ("C", 155)]):
        s.line([(720, y), (800, y)], "phase")
        s.text(735, y - 4, ph, "lbl")
    s.text(760, 180, "3-phase AC", "lbl", "middle")
    s.line([(940, 125), (1020, 125)], "mech"); s.text(980, 118, "shaft", "lbl", "middle")
    s.line([(1120, 160), (1120, 220)], "mech"); s.text(1128, 195, "chain", "lbl")

    s.rect(40, 250, 150, 50, "blk ext"); s.text(115, 272, "Charger", "t", "middle")
    s.text(115, 288, "only supervised", "s", "middle")
    s.line([(115, 250), (115, 190)], "pwr thin"); s.text(122, 232, "charge", "lbl")
    s.rect(270, 250, 150, 50, "blk ext"); s.text(345, 272, "Phone app", "t", "middle")
    s.text(345, 288, "cell V, temps", "s", "middle")
    s.line([(345, 210), (345, 250)], "radio"); s.text(352, 236, "Bluetooth", "lbl")

    # motor sensors into VESC
    s.line([(850, 190), (850, 240), (720, 240)], "sig arrow"); s.text(785, 234, "rotor Halls H1–H3", "lbl", "middle")
    s.line([(900, 190), (900, 275), (720, 275)], "sig plan arrow"); s.text(810, 269, "motor NTC 10k → TEMP (new)", "lbl", "middle")
    s.text(610, 232, "Hall plug: 5V H1 H2 H3 TEMP GND", "s", "middle")
    s.text(610, 290, "CAN timeout → zero torque", "s", "middle")

    # CAN between domains
    s.line([(545, 310), (545, 450)], "can arrow")
    s.line([(675, 450), (675, 310)], "can plan arrow")
    s.text(537, 356, "status 1–6 @ 50 Hz", "lbl", "end")
    s.text(537, 371, "erpm · I · duty · V · temps", "lbl", "end")
    s.text(683, 356, "current request", "lbl")
    s.text(683, 371, "(planned)", "lbl")
    s.text(610, 350, "CAN", "net", "middle")
    s.text(610, 366, "500 kbit/s", "lbl", "middle")
    s.text(610, 381, "H · L · GND", "lbl", "middle")
    s.text(780, 348, "the only link between domains", "warn")

    # VCU
    s.rect(500, 450, 260, 190, "blk vcu"); s.text(630, 472, "VCU", "t", "middle")
    s.text(630, 490, "ESP32 + MCP2515 + microSD", "s", "middle")
    s.text(630, 514, "today: logs CAN + wheel", "s", "middle")
    s.text(630, 530, "next: torque request,", "s", "middle")
    s.text(630, 546, "brake + throttle = zero torque", "s", "middle")
    s.text(630, 562, "later: traction control", "s", "middle")

    ins = [("Throttle", "5 V Hall grip", "analog · GPIO35", 470, True),
           ("Brake left", "on/off switch", "digital · GPIO32", 515, True),
           ("Brake right", "on/off switch", "digital · GPIO33", 560, True),
           ("IMU LSM6DS3", "ax, pitch, yaw rate", "I2C · GPIO21/22", 605, True)]
    for name, sub, sig, y, plan in ins:
        s.rect(250, y - 20, 150, 40, "blk" + (" planc" if plan else ""))
        s.text(262, y - 3, name, "t"); s.text(262, y + 13, sub, "s")
        s.line([(400, y), (500, y)], "sig" + (" plan" if plan else "") + " arrow")
        s.text(450, y - 6, sig, "lbl", "middle")
    s.text(250, 437, "today wired to the VESC ADC → moves to the VCU", "warn")

    s.rect(40, 600, 160, 50, "blk"); s.text(120, 621, "Front wheel", "t", "middle")
    s.text(120, 637, "undriven · speed reference", "s", "middle")
    s.rect(250, 630, 150, 30, "blk"); s.text(262, 650, "3144 Hall · 10 magnets", "t")
    s.line([(200, 640), (250, 645)], "mech")
    s.line([(400, 645), (500, 630)], "sig arrow"); s.text(455, 656, "digital · GPIO34", "lbl", "middle")

    s.rect(860, 460, 160, 50, "blk"); s.text(940, 481, "microSD", "t", "middle")
    s.text(940, 497, "CSV log · card dead", "s", "middle")
    s.line([(760, 485), (860, 485)], "sig arrow"); s.text(810, 479, "SPI", "lbl", "middle")
    s.rect(1060, 580, 160, 50, "blk"); s.text(1140, 601, "12 V aux battery", "t", "middle")
    s.text(1140, 617, "separate from pack", "s", "middle")
    s.rect(860, 580, 160, 50, "blk"); s.text(940, 601, "DC-DC", "t", "middle")
    s.text(940, 617, "5.3 V out", "s", "middle")
    s.line([(1060, 605), (1020, 605)], "pwr thin arrow")
    s.line([(860, 605), (760, 605)], "pwr thin arrow"); s.text(810, 599, "5.3 V", "lbl", "middle")

    # legend
    lg = [("pwr", "HV DC power"), ("phase", "3-phase AC"), ("mech", "mechanical"), ("sig", "signal"),
          ("can", "CAN bus"), ("sig plan", "planned"), ("radio", "wireless")]
    x0 = 30
    for i, (c, t) in enumerate(lg):
        x = x0 + i * 175
        s.line([(x, 695), (x + 40, 695)], c)
        s.text(x + 48, 699, t, "lbl")
    s.text(1240, 30, "Sheet 1 of 2 · Rev A · 2026-11-02", "lbl", "end")
    s.text(20, 28, "ePWT · vehicle architecture", "ttl")
    return s.svg()


if __name__ == "__main__":
    out = sys.argv[1]
    io.open(out + "/arch.svgfrag", "w", encoding="utf-8").write(architecture())
    io.open(out + "/schem.svgfrag", "w", encoding="utf-8").write(schematic())
