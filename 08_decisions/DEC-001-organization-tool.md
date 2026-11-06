# DEC-001: Personal organisation tool

> **Replaced by [DEC-003](DEC-003-no-obsidian.md) (2026-10-25).** Obsidian was never used.

**Date:** 2026-09-01

## Decision

**Obsidian, pointed straight at the repository folder.** No Notion. No Tana. No content
migration. No second source of truth.

## Context

The repository is already a set of plain Markdown files. Obsidian **has no format of its
own**: it opens a folder of `.md` files and that's it. That means pointing it at
`PROJECT_ePWT/` costs literally 30 seconds and zero migration.

What I gain: graph view, backlinks between notes, fast search, a comfortable editor, a mobile
app. What I **don't** lose: the files stay the same, Git keeps versioning them, and I keep
reading and writing them with no layer in between.

## Alternatives considered

**Notion.** Rejected. It keeps the content in its database, not in files. That creates a second
source of truth that drifts from the repo, and takes the knowledge out of the place where the
work lives. Also, its structure (databases, relations, templates) has to be designed and
maintained, and it only stays useful while someone looks after it — it is permanent work, not a
tool that works for you.

**Tana.** Rejected, and it is the most tempting because it is the most modern. Reasons: it is
web-only without good offline support, it is expensive, its mobile app is immature, and the
"supertags" model demands changing how you think about information. Learning Tana would be a
project in itself. It is not the project I want to do.

**Nothing / just the repo.** Viable, and it is what there is today. Obsidian only adds a reading
layer on top; if it doesn't help, it is uninstalled and nothing is lost. That total
reversibility is the main reason to try it.

## Reasoning

The criterion is: **one single source of truth, and the rest are viewers.** Obsidian meets it
because it does not own the data. Notion and Tana don't, because they do.

There is a second criterion, more important for me in particular. My documented pattern is
looking for the perfect system instead of executing. Exploring productivity apps is
**procrastination disguised as progress**: it feels productive and real progress is zero. That
risk, in my case, is greater than the benefit of any tool.

Obsidian on the folder that already exists is the option with the most benefit and the least
surface for distraction: nothing to configure, nothing to migrate, nothing to decide.

## Consequences

- Add to `.gitignore`: `.obsidian/workspace.json` and `.obsidian/workspace-mobile.json`. They
  store the window layout and change all the time; without ignoring them, constant merge
  conflicts appear. It is the documented no. 1 mistake of this setup.
- The rest of `.obsidian/` (configuration, plugins) **is** versioned: that way the
  configuration travels with the repo.
- Don't use Obsidian Sync or iCloud/OneDrive on the folder at the same time as Git. Two sync
  systems on the same files fight each other.
- The personal second brain (university, Formula Student, calibration) remains a separate
  project, in another folder. See `01_plan/backlog.md`.

## Review

If in two cycles I haven't opened Obsidian once, it is uninstalled and the matter is closed.
