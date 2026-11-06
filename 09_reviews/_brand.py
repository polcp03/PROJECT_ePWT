"""Brand system for OFF-ROAD EV PLATFORM decks.

Single source of truth for colours, fonts and slide geometry. Both the figure
generator (_figures.py) and the deck builder (C00_kickoff.py) import from here,
so a colour is never written twice.

Derived from the DYN-09 corporate template (photo strip / blue title band /
body / blue footer) with the palette re-anchored on the vehicle's own blue,
sampled from 09_assets/photos/IMG_7163.jpg.
"""

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
BLUE = "1D4E9C"      # primary. Bands, headers, key figures.
BLUE_DK = "0F2E63"   # cover, section dividers, statement slide
BLUE_LT = "E8EFF9"   # tinted card fill
CYAN = "2E9BD6"      # accent, kept from DYN-09
INK = "14181F"       # body text on white
GREY = "6B7480"      # secondary text, captions
PANEL = "F2F5F9"     # card fill on white
LINE = "CBD5E1"      # hairlines, table borders
WHITE = "FFFFFF"

OK = "2E7D32"        # MEASURED / confirmed
WARN = "E29A2C"      # ESTIMATE / open
RISK = "C0392B"      # finding / risk

# Status tag -> colour, used for the MEASURED/ESTIMATE/CONFIG/ASSUMED chips
TAG = {
    "MEASURED": OK,
    "VESC EST.": WARN,
    "VESC ESTIMATE": WARN,
    "CONFIG": RISK,
    "ASSUMED": GREY,
    "MISSING": RISK,
    "OPEN": RISK,
}


def rgb(hexstr):
    """'1D4E9C' -> (29, 78, 156). For python-pptx RGBColor."""
    return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))


def mpl(hexstr):
    """'1D4E9C' -> '#1D4E9C'. For matplotlib."""
    return "#" + hexstr


# --------------------------------------------------------------------------
# Typography
# --------------------------------------------------------------------------
FONT = "Arial"       # DYN-09 major font; ships with Office, safe metrics

SZ_TITLE = 26        # slide title, in the blue band
SZ_COVER = 40        # cover title
SZ_H2 = 15           # block header inside the body
SZ_BODY = 12         # body text
SZ_SMALL = 10        # captions, sources
SZ_TAG = 8           # status chips
SZ_STAT = 30         # big number callouts
SZ_FOOT = 8          # footer

# --------------------------------------------------------------------------
# Geometry, in inches. Slide is 10.0 x 5.625 (16:9), same as DYN-09.
# --------------------------------------------------------------------------
W = 10.0
H = 5.625

STRIP_H = 1.4625     # top photo band              0.000 -> 1.4625  (26 %)
BAND_Y = 1.4625      # blue title band
BAND_H = 0.4800      #                             1.4625 -> 1.9425
BODY_Y = 1.9425      # white body
FOOT_Y = 5.1400      # blue footer band
FOOT_H = H - FOOT_Y  # 0.485

BODY_H = FOOT_Y - BODY_Y          # 3.1975, layout "standard"
TALL_Y = BAND_H                   # layout "tall": band at the very top
TALL_BODY_Y = BAND_H + 0.10
TALL_BODY_H = FOOT_Y - TALL_BODY_Y

M = 0.62             # left/right margin, matches DYN-09 title indent
CW = W - 2 * M       # content width, 8.76

BADGE_W = 1.15       # chevron badge, top-left
BADGE_H = 1.30
