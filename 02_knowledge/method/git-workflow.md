# Git, explained from zero

A learning note. Written because I got lost with Git and needed to understand **what it is**
before memorising commands.

## 1. What problem Git solves

Without Git, versions get saved like this: `model_v1.slx`, `model_v2.slx`,
`model_v2_good.slx`, `model_final_DEFINITIVE.slx`. Everyone has done this.
It fails for three reasons:

1. You don't know **what changed** between v1 and v2. You only have two files.
2. You don't know **why** it changed. The reason was in your head and you have forgotten it.
3. If v3 breaks something, you can't go back to v2 without losing the good parts of v3.

Git stores **the sequence of changes**, not copies of the file. And every change carries a
message explaining why. That is the whole invention.

For this project it is directly an engineering tool: in six months I will want to know *why*
I changed a model parameter, and the answer will be written down.

## 2. The four places your work lives

This is the hardest concept, and without it nothing makes sense.

```
  Working directory  ->  Staging area  ->  Local repository  ->  Remote (GitHub)
   (your files)          (git add)         (git commit)          (git push)
```

- **Working directory** — the files as they are on your disk right now.
- **Staging area** — the "outbox". Here you choose *which part* of your work goes into the
  next snapshot. It exists because sometimes you touch 5 files and only 3 belong to the same
  logical change.
- **Local repository** — the history, on your PC, in the `.git` folder. This is where your
  project really lives.
- **Remote (GitHub)** — a copy of the history on a server. It is a backup and a shop window,
  but **it is not Git**: Git works fully without internet.

## 3. The five commands that cover 95 %

```bash
git status
```
"Where am I and what have I touched?" Run it constantly. It changes nothing, it only reports.

```bash
git add 04_model/params/vehicle.m
```
Moves that file to the outbox. `git add .` puts in everything modified.

```bash
git commit -m "Add measured phase resistance from C01"
```
Takes the snapshot and attaches the message. **The message is the valuable part**, not the
command. A commit should be *one logical change*: if the message needs an "and", it is
probably two commits.

```bash
git push
```
Uploads your commits to GitHub.

```bash
git log --oneline
```
See the history. This is where all the effort pays off.

## 4. Branches: what they really are

A branch **is not a copy of the folder**. It is just a label pointing at a commit. That is
why creating a branch is instant even if the project weighs 2 GB.

It is for this: I want to try a different tyre model without breaking the one that works. I
create a branch, experiment, and if it goes badly I delete it and nothing has happened. If it
goes well, I merge it.

```bash
git switch -c model/tyre-slip     # create a branch and jump to it
git switch master                  # go back
```

Naming convention I will use: `area/short-description`, for example `model/longitudinal-v1`,
`firmware/can-logger`, `docs/cycle-01`.

## 5. Pull Request: what it is and why I do it working alone

A PR is a **merge proposal**: "I want to put this branch into `master`, shall we review it?".
In a team it is for someone else to review the code.

Working alone it looks pointless. It isn't, for two reasons:

1. **It forces you to look at your own diff before it becomes permanent.** Seeing all your
   changes together, in red and green, finds mistakes you don't see while writing.
2. **The PR is documentation.** Its description explains *why* this block of work exists. In a
   year, the PR history tells the story of the project much better than loose commits.

And for this project in particular: learning the PR flow **is a stated goal**. Practising it
alone, without a team's pressure, is the best way to arrive prepared.

## 6. The full flow, one real work cycle

```bash
git fetch origin                           # 1-2. bring in the latest from GitHub
git switch -c model/longitudinal-v1 origin/master   # 3. new branch from GitHub's master
# ... work ...
git add .                                  # 4. select
git commit -m "Add longitudinal vehicle model"   # 5. snapshot + why
git push -u origin model/longitudinal-v1   # 6. upload the branch
gh pr create --fill                        # 7. open the PR (GitHub CLI)
gh pr merge --merge                        # 8. merge once reviewed (merge commit, never squash)
```

## 7. Typical mistakes and how to get out

| Situation | What to do |
|---|---|
| I ran `add` on something I didn't want | `git restore --staged file` |
| I want to discard a file's changes | `git restore file` (**destroys** the work) |
| The last commit has a bad message | `git commit --amend -m "good message"` (only if you haven't pushed) |
| I'm lost | `git status`. Always. It tells you where you are and what options you have |

## 8. What NOT to put in Git

- Executables and downloaded programs (VESC Tool) → `_tools/`, ignored.
- Python virtual environments (`.venv/`) → rebuilt with one command.
- Build outputs (`slprj/`, `build/`, `.pio/`).
- Huge files. Git never forgets: if you put in 1 GB, the repo weighs 1 GB forever, even if
  you delete it later.

**Rule:** the repository holds what I create, not what I download or what can be regenerated.
