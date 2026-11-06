"""Find text that overflows its box, before rendering anything.

python-pptx does not measure text, so a box that is too small produces a file
that opens fine and looks broken. This walks the built .pptx, re-wraps every
paragraph with the real Arial metrics, and reports the shapes whose text does
not fit. It is the only reliable guard against the one defect that keeps
coming back.

    ./.venv/Scripts/python.exe 09_reviews/_check.py [deck.pptx]
"""
from __future__ import annotations

import os
import sys

from pptx import Presentation
from pptx.util import Emu
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# Measure at a large size and scale down: TrueType hinting makes tiny sizes
# non-linear, and we only need relative widths.
REF = 200
FONTS = {}


def _font(bold, italic):
    key = (bool(bold), bool(italic))
    if key not in FONTS:
        name = {(False, False): "arial.ttf", (True, False): "arialbd.ttf",
                (False, True): "ariali.ttf", (True, True): "arialbi.ttf"}[key]
        FONTS[key] = ImageFont.truetype(os.path.join(
            os.environ.get("WINDIR", "C:/Windows"), "Fonts", name), REF)
    return FONTS[key]


def text_width_pt(s, size_pt, bold=False, italic=False):
    if not s:
        return 0.0
    return _font(bold, italic).getlength(s) * size_pt / REF


def wrapped_lines(text, size_pt, width_pt, bold=False, italic=False):
    """Greedy word wrap, the same way PowerPoint breaks on spaces."""
    if not text.strip():
        return 1
    lines = 0
    for hard in text.split("\n"):
        words, cur = hard.split(), ""
        if not words:
            lines += 1
            continue
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width_pt(trial, size_pt, bold, italic) <= width_pt or not cur:
                cur = trial
            else:
                lines += 1
                cur = wd
        lines += 1
    return lines


# PowerPoint's single line spacing for Arial is ~1.15 em; a lnSpc percentage
# multiplies that. Calibrated against the PowerPoint renders of this deck.
EM_PER_LINE = 1.17


def para_height_pt(p, width_pt):
    runs = p.runs
    if not runs:
        return 0.0
    size = max((r.font.size.pt for r in runs if r.font.size), default=18.0)
    bold = any(r.font.bold for r in runs)
    italic = any(r.font.italic for r in runs)
    text = "".join(r.text for r in runs)
    ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
    n = wrapped_lines(text, size, width_pt, bold, italic)
    h = n * size * EM_PER_LINE * ls
    if p.space_before is not None:
        h += p.space_before.pt
    if p.space_after is not None:
        h += p.space_after.pt
    return h


FOOT_TOP_IN = 5.14      # the blue footer band; text must stay above it
SLIDE_H_IN = 5.625


def check(path, slack_in=0.02):
    """A text box growing downward into empty space is fine — PowerPoint does
    that by design. Only two things are actually broken, and both are here:

      SPILL   text leaves the coloured card it belongs to
      FOOTER  text runs into the footer band or off the bottom of the slide
    """
    prs = Presentation(path)
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        # containers: filled shapes carrying no text of their own
        boxes = []
        for sh in slide.shapes:
            if sh.shape_type is None or not hasattr(sh, "fill"):
                continue
            if sh.has_text_frame and sh.text_frame.text.strip():
                continue
            try:
                if sh.fill.type is None or sh.fill.type == 5:   # 5 = background
                    continue
            except (TypeError, ValueError):
                continue
            bx, by = Emu(sh.left).inches, Emu(sh.top).inches
            bw, bh = Emu(sh.width).inches, Emu(sh.height).inches
            boxes.append((bx, by, bw, bh))
            # A card that itself runs under the footer band is a defect even
            # when the text inside it fits.
            # A panel that runs to the very bottom of the slide is a
            # deliberate full-height block (the cover), not a spill.
            full_bleed = by + bh > SLIDE_H_IN - 0.05
            is_footer = abs(by - FOOT_TOP_IN) < 0.05
            if not full_bleed and not is_footer and by + bh > FOOT_TOP_IN + 0.02:
                bad.append((i, "BOX/FOOT", by + bh - FOOT_TOP_IN,
                            f"filled box at ({bx:.2f}, {by:.2f}) "
                            f"{bw:.2f}×{bh:.2f}\""))

        for sh in slide.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip():
                continue
            tf = sh.text_frame
            li = tf.margin_left.pt if tf.margin_left is not None else 7.2
            ri = tf.margin_right.pt if tf.margin_right is not None else 7.2
            wpt = Emu(sh.width).pt - li - ri
            if wpt <= 4:
                continue
            need_in = sum(para_height_pt(p, wpt) for p in tf.paragraphs) / 72.0
            top = Emu(sh.top).inches
            left = Emu(sh.left).inches
            bottom = top + need_in
            txt = tf.text.replace("\n", " ⏎ ")[:66]

            # does it belong to a card, and does it stay inside it?
            host = None
            for bx, by, bw, bh in boxes:
                if bx - 0.02 <= left <= bx + bw and by - 0.02 <= top <= by + bh:
                    if host is None or bh < host[3]:
                        host = (bx, by, bw, bh)
            if host:
                # Text that lives in a card is judged against the card, and
                # against nothing else — the footer rule does not apply to it.
                if bottom > host[1] + host[3] + slack_in:
                    bad.append((i, "SPILL", bottom - (host[1] + host[3]), txt))
                continue

            # Free-standing text may grow downward into white space, but not
            # into the next card. This is the defect that hides best: the
            # card is drawn on top, so the tail of the sentence disappears.
            right = left + Emu(sh.width).inches
            hit = None
            for bx, by, bw, bh in boxes:
                if by <= top + 0.02 or by >= bottom - slack_in:
                    continue
                if bx < right - 0.05 and bx + bw > left + 0.05:
                    if hit is None or by < hit:
                        hit = by
            if hit is not None:
                bad.append((i, "COLLIDE", bottom - hit, txt))
                continue
            if bottom > FOOT_TOP_IN + slack_in:
                where = "FOOTER" if bottom <= SLIDE_H_IN else "OFF-SLIDE"
                bad.append((i, where, bottom - FOOT_TOP_IN, txt))

    bad.sort(key=lambda r: -r[2])
    if not bad:
        print(f"OK — nothing spills in {os.path.basename(path)}")
        return 0
    print(f"{len(bad)} problem(s) in {os.path.basename(path)}\n")
    print(f"{'sl':>3}  {'what':<10} {'over':>7}   text")
    print("-" * 96)
    for sl, what, over, txt in bad:
        print(f"{sl:>3}  {what:<10} {over:>6.2f}\"   {txt}")
    return len(bad)


if __name__ == "__main__":
    # Slide text carries −, ≤, μ...: the Windows console codepage cannot print them.
    sys.stdout.reconfigure(encoding="utf-8")
    deck = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "C00-kickoff.pptx")
    sys.exit(1 if check(deck) else 0)
