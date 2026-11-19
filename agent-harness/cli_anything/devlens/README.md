# cli-anything-devlens

A command-line tool for updating the Devlens Bangladesh website (an Astro site) without
hand-editing JSON. It adds and edits stories, jobs, homepage picks, funding calls and
images, checks the content, and runs the real Astro build to confirm the site still builds
and every story page exists.

Every change is recorded, so `session undo` can step back.

## Requirements

- Python 3.10 or newer
- Node.js 20 or newer, and the site's packages installed (`npm ci` in the site folder).
  Only `build ...` commands need these; everything else works on the JSON files alone.

## Install

```bash
cd agent-harness
pip install -e .            # add '.[test]' to also install pytest
cli-anything-devlens --help
```

## Point it at the site

The tool finds the site in this order: `--site PATH`, then `$DEVLENS_SITE`, then the
current folder and its parents (any folder that contains `src/data/home.json`).

## Usage

```bash
cli-anything-devlens site info                 # counts and current homepage picks
cli-anything-devlens site validate             # content checks (exit 1 on errors)

# stories
cli-anything-devlens post list --since 2026-11-18
cli-anything-devlens post add --title "..." --excerpt "..." --category news \
    --tag health --content-file story.html --image /media/2026/11/photo.jpg --image-alt "..."
cli-anything-devlens post update <slug> --title "Corrected title"
cli-anything-devlens post remove <slug>

# images
cli-anything-devlens media add ~/photo.jpg --name dengue-ward.jpg   # -> /media/YYYY/MM/dengue-ward.jpg

# homepage
cli-anything-devlens home set-lead <slug> --label "Health · Dengue" --demote
cli-anything-devlens home plus add <slug>
cli-anything-devlens home funding add --title "..." --funder "..." --deadline 2026-12-01 --url https://...
cli-anything-devlens home funding prune
cli-anything-devlens home number add --value "71%" --label "..." --source "ADB, Nov 2026" --keep 3

# jobs
cli-anything-devlens job add --title "..." --org BRAC --sector health-nutrition \
    --url https://... --location Dhaka --deadline 2026-12-10
cli-anything-devlens job prune                 # drop jobs past their deadline

# build with the real Astro build and check the output
cli-anything-devlens build run

# undo
cli-anything-devlens session history
cli-anything-devlens session undo
```

Run `cli-anything-devlens` with no command for the interactive REPL.

## Options for every command

- `--json`: machine-readable output. Errors become `{"error": "..."}` with exit code 1.
- `--dry-run`: run the command and show the files it would change, but write nothing.
- `--site PATH`: the site folder.

Each changing command reports `changes` (files created, modified or deleted) and `saved`.

## How changes are saved

Changes are staged in memory, then written in one step when the command finishes. Files
are written atomically and in the same JSON style they were read in (indent, trailing
newline, non-ASCII kept), so `git diff` only shows real edits. A copy of each changed
file's previous version is kept in `<site>/.devlens-cli/session.json` (git-ignored, last
30 steps) for `session undo` and `session redo`. Undo refuses to overwrite a file that was
changed outside the tool since that step, unless you pass `--force`.

In the REPL each command is saved as soon as it runs.

## Previews

There is no `preview` command group. The truthful view of this software is the built
site itself: `build run` produces it, and `build verify` checks it.

## Tests

```bash
cd agent-harness
python -m pytest cli_anything/devlens/tests -v -s
CLI_ANYTHING_FORCE_INSTALLED=1 python -m pytest cli_anything/devlens/tests -v -s   # release check
```

The end-to-end tests copy the whole site to a temp folder (they never touch your
checkout) and run the real Astro build, so Node.js and `node_modules` must be present.
