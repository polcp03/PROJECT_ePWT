"""Build the Quad Tasks page (tasks.html) from tasks.md.

Usage (from PROJECT_ePWT/):  ./.venv/Scripts/python.exe 01_plan/tasks/build.py

tasks.md is the source. The page shows it and stores Pol's ticks in the artifact
database (collection `status`, one doc per task id; collection `inbox` for new tasks
typed on the phone). The Sunday sync copies those back into tasks.md.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "tasks.md"
TEMPLATE = HERE / "template.html"
OUT = HERE / "tasks.html"

TASK = re.compile(r"^- \[( |~|x)\] (.+?)\s*\{#([a-z0-9-]+)(?: (buy))?\}\s*$")
HEAD = re.compile(r"^(##|###) (.+?)(?:\s*\{#([a-z0-9-]+)\})?\s*$")
STATE = {" ": "todo", "~": "ordered", "x": "done"}


def inline(text):
    """Markdown inline → safe HTML. Relative links become plain text."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def parse(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    doc = {"title": "", "intro": [], "sections": []}
    sec = sub = task = None
    seen = set()
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            doc["title"] = line[2:].strip()
            continue
        if not doc["sections"] and line.startswith(">"):
            body = line.lstrip(">").strip()
            if not body or not doc["intro"]:
                doc["intro"].append("")
            if body:
                doc["intro"][-1] = (doc["intro"][-1] + " " + body).strip()
            continue
        m = HEAD.match(line)
        if m:
            task = None
            if m.group(1) == "##":
                sec = {"id": m.group(3) or re.sub(r"\W+", "-", m.group(2).lower()).strip("-"),
                       "title": m.group(2).strip(), "note": [], "groups": [], "list": []}
                doc["sections"].append(sec)
                sub = {"title": "", "tasks": []}
                sec["groups"].append(sub)
            else:
                sub = {"title": m.group(2).strip(), "tasks": []}
                sec["groups"].append(sub)
            continue
        m = TASK.match(line)
        if m:
            if sec is None:
                sys.exit(f"task before any section: {line}")
            state, title, tid, buy = m.groups()
            if tid in seen:
                sys.exit(f"repeated task id: {tid}")
            seen.add(tid)
            if state == "~" and not buy:
                sys.exit(f"{tid}: '[~] ordered' is only for buy items")
            task = {"id": tid, "title": inline(title), "state": STATE[state],
                    "buy": bool(buy), "detail": []}
            sub["tasks"].append(task)
            continue
        if task and line.startswith("  ") and line.strip():
            task["detail"].append(inline(line.strip()))
            continue
        if not line.strip():
            if task:
                task = None
            continue
        if sec is not None:
            task = None
            m2 = re.match(r"^\d+\. (.+)", line)
            if m2:
                sec["list"].append(inline(m2.group(1)))
            elif sec["list"] and line.startswith("   "):
                sec["list"][-1] += " " + inline(line.strip())
            elif sub["tasks"] or (sub["title"] and sub is not sec["groups"][0]):
                sub.setdefault("note", []).append(inline(line.strip()))
            else:
                sec["note"].append(inline(line.strip()))
    for s in doc["sections"]:
        s["groups"] = [g for g in s["groups"] if g["tasks"] or g["title"]]
        s["note"] = " ".join(s["note"])
    intro = [x for x in doc["intro"] if x]
    nxt = [x for x in intro if x.startswith("**Next up:**")]
    doc["next"] = inline(nxt[0][len("**Next up:**"):].strip()) if nxt else ""
    doc["updated"] = (re.search(r"Updated ([^.]+)\.", " ".join(intro)) or [None, ""])[1]
    del doc["intro"]
    return doc


def main():
    doc = parse(SRC.read_text(encoding="utf-8"))
    n = sum(len(g["tasks"]) for s in doc["sections"] for g in s["groups"])
    page = TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(doc, ensure_ascii=False).replace("</", "<\\/")
    page = page.replace("/*__DATA__*/null", data)
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT.relative_to(HERE.parents[1])}: {len(doc['sections'])} sections, {n} tasks")


if __name__ == "__main__":
    main()
