"""Build the ePWT Bench learning app from lessons/*.md into app.html.

Usage (from PROJECT_ePWT/):  ./.venv/Scripts/python.exe 01_plan/app/build.py

The lesson format is described in README.md next to this file. Never edit app.html
by hand: change a lesson .md, or the engine (engine.js, motor3d.js, labs.js, style.css),
and rebuild.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LESSONS = HERE / "lessons"
OUT = HERE / "app.html"

# Facts about Pol's motor that the grader may use. Values from 04_model/params/*.m.
FACTS = (
    "Pol's quad motor: radial-flux PMSM, inner rotor, outer slotted stator, 3 pole pairs (p = 3, "
    "6 magnets, measured by Hall pulse counting). Magnets probably interior or inset: saliency "
    "Lq/Ld = 1.14, so not pure surface; exact magnet layout and slot count NOT measured. "
    "lambda_m = 16.855 mWb (measured, back-EMF spin test with a drill, motor disconnected, 7-Sep-2026). "
    "Rs = 28 mOhm per phase (VESC estimate, includes MOSFETs). Ld = 99 uH, Lq = 113 uH. "
    "Kt = 1.5*p*lambda_m = 0.0758 N*m/A of iq. Bus 52 V nominal (13S5P Li-ion), pack resistance "
    "measured 0.18 Ohm. VESC in FOC, current control: the throttle asks for amps. Limits: motor "
    "120 A, battery 40 A (BMS continuous). PWM 30 kHz. Field weakening OFF (fw_current = 0). "
    "Max sinusoidal phase voltage with SVPWM = Vbus/sqrt(3) = 30 V peak. Measured no-load speed "
    "5480 rpm. Gear 92/11 = 8.364. Wheel radius 0.155 m (assumed). 110 kg with rider. "
    "Amplitude-invariant Clarke/Park (VESC convention)."
)

INLINE = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])"), r"<em>\1</em>"),
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
]


def inline(text):
    out = html.escape(text, quote=False)
    for rx, rep in INLINE:
        out = rx.sub(rep, out)
    return out


def parse_attrs(s):
    return {k: v.strip('"') for k, v in re.findall(r"(\w+)=(\"[^\"]*\"|\S+)", s)}


def prose(lines):
    """Paragraphs, lists, equations (= ...), 'in your motor' notes (> ...), sources (src: ...)."""
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>" + inline(i) + "</li>" for i in items) + "</ul>")
            items.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush()
        elif line.startswith("= "):
            flush()
            out.append('<div class="eq">' + inline(line[2:]) + "</div>")
        elif line.startswith("> "):
            flush()
            out.append('<aside class="mine"><span>In your motor</span>' + inline(line[2:]) + "</aside>")
        elif line.startswith("src: "):
            flush()
            out.append('<p class="src">' + inline(line[5:]) + "</p>")
        elif line.startswith("- "):
            if para:
                flush()
            items.append(line[2:])
        else:
            if items:
                flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


def parse_question(attrs, body, lesson_id, where):
    q = {"kind": attrs.get("kind", "check"), "prompt": "", "key": [], "traps": [], "solution": ""}
    mode, prompt, sol = "prompt", [], []
    for line in body:
        s = line.strip()
        if s in ("key:", "traps:"):
            mode = s[:-1]
        elif s.startswith("solution:"):
            mode = "solution"
            if s[9:].strip():
                sol.append(s[9:].strip())
        elif mode == "prompt":
            prompt.append(line)
        elif mode in ("key", "traps") and s.startswith("- "):
            q[mode].append(s[2:])
        elif mode == "solution":
            sol.append(line)
    q["prompt"] = prose(prompt)
    q["prompt_text"] = re.sub(r"\s+", " ", " ".join(l.strip() for l in prompt)).strip()
    q["solution"] = prose(sol)
    if q["kind"] not in ("doubt",) and not q["key"]:
        sys.exit(f"{where}: question {attrs.get('id')} in {lesson_id} has no key: list")
    return q


def parse_lesson(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front matter")
    meta = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    for k in ("id", "title", "date"):
        if k not in meta:
            sys.exit(f"{path.name}: front matter needs {k}")
    lines = m.group(2).split("\n")
    parts, questions, buf = [], {}, []
    open_idea = open_sec = False
    idea_n = 0
    i = 0

    def flush():
        if buf:
            parts.append(prose(buf))
            buf.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith(":::"):
            flush()
            head = line[3:].strip()
            kind, _, rest = head.partition(" ")
            attrs = parse_attrs(rest) or {}
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            if kind == "q":
                qid = attrs.get("id")
                if not qid or qid in questions:
                    sys.exit(f"{path.name}: question id missing or repeated: {qid}")
                questions[qid] = parse_question(attrs, body, meta["id"], path.name)
                parts.append(f'<div class="qa" data-q="{qid}"></div>')
            elif kind == "scene":
                # the preset belongs to the idea it sits in; body lines are a caption
                parts.append(
                    "<div class=\"scene-ref\" data-scene='" + html.escape(json.dumps(attrs), quote=True)
                    + "'><button type=\"button\" class=\"btn ghost show-scene\">Show it in the motor</button>"
                    + ("<p>" + inline(" ".join(b.strip() for b in body if b.strip())) + "</p>" if any(b.strip() for b in body) else "")
                    + "</div>"
                )
            elif kind == "lab":
                name = rest.split()[0] if rest else ""
                title = " ".join(b.strip() for b in body if b.strip())
                parts.append(f'<div class="labbox" data-lab="{html.escape(name)}" data-title="{html.escape(title)}"></div>')
            else:
                sys.exit(f"{path.name}: unknown block :::{kind}")
        elif line.startswith("## "):
            flush()
            if open_idea:
                parts.append("</div></article>")
                open_idea = False
            if open_sec:
                parts.append("</section>")
            title, _, sid = line[3:].partition("{#")
            sid = sid.rstrip("}").strip() or re.sub(r"\W+", "-", title.lower()).strip("-")
            parts.append(f'<section class="sec" id="s-{sid}"><h2>{inline(title.strip())}</h2>')
            open_sec = True
        elif line.startswith("### "):
            flush()
            if open_idea:
                parts.append("</div></article>")
            idea_n += 1
            parts.append(f'<article class="idea"><span class="n">{idea_n}</span><div><h3>{inline(line[4:].strip())}</h3>')
            open_idea = True
        else:
            buf.append(line)
        i += 1
    flush()
    if open_idea:
        parts.append("</div></article>")
    if open_sec:
        parts.append("</section>")
    meta["html"] = "\n".join(parts)
    meta["questions"] = questions
    meta["hasScene"] = "data-scene=" in meta["html"]
    return meta


def main():
    lessons = [parse_lesson(p) for p in sorted(LESSONS.glob("*.md"))]
    if not lessons:
        sys.exit("no lessons in lessons/")
    data = {"facts": FACTS, "lessons": lessons}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = (HERE / "template.html").read_text(encoding="utf-8")
    for name in ("style.css", "motor3d.js", "labs.js", "engine.js"):
        page = page.replace("/*{{" + name + "}}*/", (HERE / name).read_text(encoding="utf-8"))
    page = page.replace("{{DATA}}", blob)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    nq = sum(len(l["questions"]) for l in lessons)
    print(f"app.html: {len(lessons)} lesson(s), {nq} questions, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
