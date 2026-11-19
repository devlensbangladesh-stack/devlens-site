---
name: "cli-anything-devlens"
description: "Update the Devlens Bangladesh website (Astro, JSON content) from the command line: add or edit stories, jobs, homepage lead/also-today/specials, key numbers, funding calls and images; prune expired jobs and funding; validate content; run the real Astro build and check every page; undo changes. Use for any Devlens site content update or scheduled news run."
---

# cli-anything-devlens

Command-line harness for the Devlens Bangladesh website. It edits the site's JSON data
(`src/data/...`) and images (`public/media/...`) safely, checks the content, and runs the
real `astro build` to prove the site still builds. Every change can be undone.

## Installation

```bash
cd <site>/agent-harness && pip install -e .
```

**Prerequisites:**
- Python 3.10+
- For `build ...` only: Node.js 20+ and `npm ci` run in the site folder

## Finding the site

`--site PATH`, else `$DEVLENS_SITE`, else the nearest parent folder of the current
directory that contains `src/data/home.json`.

## Usage

```bash
cli-anything-devlens --help                  # all groups
cli-anything-devlens <group> <command> --help
cli-anything-devlens                         # interactive REPL
cli-anything-devlens --json site info        # JSON output for agents
cli-anything-devlens --dry-run job prune     # show changes, write nothing
```

## Command Groups

### Cli

Manage the Devlens Bangladesh website: stories, jobs, homepage, images and builds.

| Command | Description |
|---------|-------------|
| `repl` | Interactive mode (the default when no command is given). |

### Site

Site overview and content checks.

| Command | Description |
|---------|-------------|
| `info` | Counts of stories, jobs, funding calls and current homepage picks. |
| `validate` | Check all content: JSON, slugs, dates, categories, images, homepage links, jobs. |

### Post

Stories in src/data/posts.

| Command | Description |
|---------|-------------|
| `list` | List stories, newest first. |
| `show` | Show one story. |
| `add` | Add a new story. |
| `update` | Change fields of a story. |
| `remove` | Delete a story. |
| `slugify` | Show the slug a title would get. |

### Category

Story categories.

| Command | Description |
|---------|-------------|
| `list` | List categories. |

### Tag

Story tags.

| Command | Description |
|---------|-------------|
| `list` | List tags. |
| `add` | Add a tag. |

### Job

Job listings in src/data/jobs.json.

| Command | Description |
|---------|-------------|
| `list` | List jobs (index, title, org, deadline...). |
| `sectors` | List job sectors. |
| `add` | Add a job at the top of the list. |
| `update` | Change fields of a job. |
| `remove` | Remove a job. |
| `prune` | Remove jobs whose deadline has passed. |

### Home

Homepage picks, numbers, funding calls and spotlight (src/data/home.json).

| Command | Description |
|---------|-------------|
| `show` | Show the homepage data, or one section of it. |
| `set-lead` | Make a story the homepage lead. |
| `set-also` | Make a story the 'Also today' feature. |
| `set-special` | Set the Devlens Special feature. |
| `pills` | Set the counter pills (no options: just show them). |
| `spotlight-today` | Replace the spotlight's 'today' update. |

### Home Plus

The extra 'Also today' story list.

| Command | Description |
|---------|-------------|
| `list` | List the extra stories in order. |
| `add` | Add a story to the list (top by default). |
| `remove` | Remove a story from the list. |
| `trim` | Keep only the first N stories. |

### Home Number

Homepage key numbers.

| Command | Description |
|---------|-------------|
| `list` | List the key numbers. |
| `add` | Add a key number. |
| `remove` | Remove a key number by index. |

### Home Funding

Funding calls with deadlines.

| Command | Description |
|---------|-------------|
| `list` | List funding calls. |
| `add` | Add a funding call (kept sorted by deadline). |
| `remove` | Remove a funding call. |
| `prune` | Remove funding calls whose deadline has passed. |

### Media

Images in public/media/YYYY/MM.

| Command | Description |
|---------|-------------|
| `add` | Copy an image into the site and report its src and size. |
| `info` | Format and size of an image, e.g. /media/2026/11/x.jpg |
| `list` | List images. |

### Build

Build the site with Astro and check the output.

| Command | Description |
|---------|-------------|
| `run` | Validate content, run 'astro build', then check the generated pages. |
| `verify` | Check an existing build folder against the content. |
| `backend` | Show the Node and Astro versions the build uses. |

### Session

Undo, redo and history of changes made with this CLI.

| Command | Description |
|---------|-------------|
| `status` | Site path and undo/redo depth. |
| `history` | List recorded changes, oldest first. |
| `undo` | Undo the last change. |
| `redo` | Redo the last undone change. |

## Examples

### A scheduled news run

```bash
export DEVLENS_SITE=/home/user/devlens-site
D="cli-anything-devlens --json"
$D job prune                                   # drop jobs past deadline (Dhaka date)
$D home funding prune
$D media add /tmp/photo.jpg --name mugda-hospital.jpg     # returns src, width, height
$D post add --title "Dengue admissions rise to 1,674 in a day" \
   --excerpt "One more death took this year's toll to 508." \
   --category news --tag health-nutrition \
   --content-file /tmp/story.html \
   --image /media/2026/11/mugda-hospital.jpg --image-alt "Mugda hospital in Dhaka" \
   --credit "Name / Wikimedia Commons, CC0" --credit-url https://commons.wikimedia.org/wiki/File:...
$D home set-lead dengue-admissions-rise-to-1674-in-a-day --label "Health · Dengue" --demote
$D home plus add <another-slug>
$D job add --title "Field Officer" --org BRAC --sector health-nutrition \
   --url https://... --location "Cox's Bazar" --deadline 2026-12-10
$D home funding add --title "..." --funder "..." --deadline 2026-12-01 --url https://...
$D home pills --funding-open 7
$D site validate                               # exit 1 if any error
$D build run                                   # real Astro build + page checks
```

### Fix a story, then roll back a bad homepage change

```bash
cli-anything-devlens post update <slug> --title "Corrected title" --excerpt "..."
cli-anything-devlens home set-lead <slug>
cli-anything-devlens session undo              # restores home.json exactly
cli-anything-devlens session history
```

## Content rules the CLI enforces

- Story slugs are lowercase words joined by hyphens; the file name equals the slug. The
  slug is made from the title unless `--slug` is given (`post slugify "Title"` to preview).
- Dates are Dhaka time. `--date 2026-11-19` means 09:00; the story URL is
  `/YYYY/MM/DD/<slug>/`.
- Categories must exist (`category list`). Tags must exist (`tag list`; add with `tag add`).
- Images must be under `/media/` and exist; width and height are read from the file.
- Job sectors must exist (`job sectors`); `deadlineText` is filled in from `deadline`.
- `post remove` refuses while the homepage uses the story; `--force` also removes it
  from the homepage lists.

## For AI Agents

1. **Use `--json`.** Results are JSON on stdout. Errors are `{"error": "..."}` on stdout
   with exit code 1 (without `--json`, errors go to stderr).
2. **Every changing command reports** `changes` (path + create/modify/delete), `saved`
   and `dry_run`. Use `--dry-run` first when unsure.
3. **Inspect before changing:** `site info`, `post list --since`, `home show lead`,
   `job list --status expired`, `session status`.
4. **Run `site validate` then `build run` before committing.** `build run` exits 1 and
   lists `problems` if a page is missing or the build fails.
5. **Undo with `session undo`.** It refuses if the file was changed outside the CLI
   (for example by git) since that step; pass `--force` only if you mean it.
6. The CLI never runs git. Commit and push the changed files yourself.
7. There is no preview group: the built site (`build run --out DIR`) is the preview.

## Version

1.0.0
