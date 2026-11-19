# Devlens website: harness analysis and SOP

## The software

The Devlens Bangladesh website is an Astro 5 static site deployed on Cloudflare Pages.
Every push to `main` rebuilds it. Scheduled Claude runs push update branches named
`auto/...`; `.github/workflows/auto-merge.yml` checks that the JSON parses, builds the
site and merges the branch into `main`.

There is no GUI and no database: the "project" is the folder of JSON data files, and
the "renderer" is `astro build`.

## Data model

| File | What it holds | CLI group |
|---|---|---|
| `src/data/posts/<slug>.json` | One story: `slug, date, modified, title, excerpt, categories, tags, image{src,alt,width,height,credit?,creditUrl?}, content` (HTML). File name must equal the slug. Dates are Dhaka local time `YYYY-MM-DDTHH:MM:SS`. | `post` |
| `src/data/home.json` | `lead`, `alsoToday` (with `plus` list of slugs), `special` (shown 7 days after `published`), `pills`, `numbers`, `funding`, `pinnedSpecials`, `spotlight` | `home` |
| `src/data/jobs.json` | `sectors` and `jobs`. Jobs past `deadline` are hidden in the browser and left out of the next build. | `job` |
| `src/data/categories.json`, `tags.json` | Term lists. Unknown tags still render, with a generated name. | `category`, `tag` |
| `src/data/pages/*.json` | Fixed pages (About, Funding...). Read-only in this CLI. | `site info` |
| `public/media/YYYY/MM/` | Images, referenced as `/media/YYYY/MM/file.jpg` | `media` |

URLs: a story is served at `/YYYY/MM/DD/<slug>/`, from the date part of `date`.

## How the site uses the data (from `src/lib/data.js` and `src/pages/index.astro`)

- Stories are sorted by `date`, newest first. A story without `image` uses the first
  `<img>` in its content.
- "Today" is the date in Asia/Dhaka. The CLI uses the same rule for defaults
  (`added`, prune dates, new story dates).
- The homepage lead/also-today/special and every `plus` slug must exist, or
  `bySlug()` returns nothing and the page breaks or drops the item. `site validate`
  checks this; `post remove` refuses to delete a story the homepage still uses.

## Backend

`utils/astro_backend.py` runs `node node_modules/astro/astro.js build [--outDir]` in the
site folder: the same build Cloudflare runs. `core/build.py` then checks the output:
`index.html` is HTML and shows the lead and also-today headlines, every story has its
page and the page contains its title, `sitemap.xml` and `feed.xml` are XML, and
`/jobs/` exists. If Node or Astro is missing, the command fails with install steps.

## Design choices

- **Staged writes, one commit per command.** Reads see staged changes, so a command can
  make several edits and validate them before anything touches disk. `--dry-run`
  discards the stage and reports what would have changed.
- **Style-preserving JSON.** The repo mixes indent 1 and 2, with and without a trailing
  newline. The writer keeps each file's style, so a round trip of all real files is
  byte-identical (tested).
- **Undo by file snapshots.** Each commit stores before/after bytes and hashes. Undo
  checks the hash first, so it never silently overwrites edits made by hand or by git.
- **No preview group.** The built site is the only truthful view; screenshots are not
  produced by the CLI.

## Mapping to the standard harness layout

| Standard piece | Here |
|---|---|
| `core/project.py` (open, info) | `core/site.py` (find, read, write, info) |
| `core/export.py` (render) | `core/build.py` (Astro build + output checks) |
| `utils/<software>_backend.py` | `utils/astro_backend.py` |
| `--project FILE` | `--site PATH` (the project is a folder) |
| domain modules | `core/posts.py`, `jobs.py`, `home.py`, `media.py`, `validate.py` |

## Typical scheduled-run workflow

```bash
export DEVLENS_SITE=/path/to/devlens-site
cli-anything-devlens job prune
cli-anything-devlens home funding prune
cli-anything-devlens media add photo.jpg --name story-photo.jpg
cli-anything-devlens post add ... --image /media/2026/11/story-photo.jpg
cli-anything-devlens home set-lead <slug> --label "..." --demote
cli-anything-devlens job add ...
cli-anything-devlens site validate
cli-anything-devlens build run
git add -A && git commit -m "..." && git push origin HEAD:auto/<date>-<run>
```
