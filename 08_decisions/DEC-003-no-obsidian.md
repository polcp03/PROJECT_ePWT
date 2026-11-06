# DEC-003: Obsidian out, the repo is read in VS Code and GitHub

**Date:** 2026-10-25 · **Replaces:** [DEC-001](DEC-001-organization-tool.md)

## Decision

Obsidian is removed from the project: the `.obsidian/` folder, the install note and the
`[[wikilink]]` links, which become normal Markdown links.

## Why

- **It wasn't used.** In two cycles not a single note was created from Obsidian. DEC-001
  assumed the graph and backlinks would help navigation; the real navigation was `01_plan/`
  from the file explorer and the artifacts on claude.ai.
- `[[wikilinks]]` and `[!todo]` callouts don't work on GitHub, and the repo is public: it is
  part of the portfolio. What shows on GitHub has to look right.

## Alternatives

Keep it "just in case": rejected. A small but real cost (a format only one tool understands)
in exchange for zero use.

## Consequences

- The `.md` files stay plain Markdown; DEC-001 was right that leaving costs nothing.
- Some files still have `> [!...]` callouts: on GitHub they show as a normal quote. They are
  not converted in bulk; they get fixed whenever each file is touched.
