"""cli-anything-devlens: manage the Devlens Bangladesh website from the command line.

Run with no arguments for the interactive REPL, or use one-shot subcommands:

    cli-anything-devlens --site ~/devlens-site --json site info
    cli-anything-devlens post add --title ... --excerpt ... --category news --content-file story.html
    cli-anything-devlens job prune
    cli-anything-devlens build run
"""

from __future__ import annotations

import json
import shlex
import sys

import click

from cli_anything.devlens import __version__
from cli_anything.devlens.core import build as build_mod
from cli_anything.devlens.core import home as home_mod
from cli_anything.devlens.core import jobs as jobs_mod
from cli_anything.devlens.core import media as media_mod
from cli_anything.devlens.core import posts as posts_mod
from cli_anything.devlens.core import validate as validate_mod
from cli_anything.devlens.core.session import Session, SessionError
from cli_anything.devlens.core.site import (CATEGORIES, TAGS, Site, SiteError, find_site,
                                            slugify)
from cli_anything.devlens.utils.astro_backend import BackendError

KNOWN_ERRORS = (SiteError, SessionError, BackendError)

_repl_mode = False
_site_cache: dict[str, Site] = {}


class State:
    def __init__(self, site_path, use_json, dry_run):
        self.site_path = site_path
        self.use_json = use_json
        self.dry_run = dry_run
        self._site = None

    @property
    def site(self) -> Site:
        if self._site is None:
            root = str(find_site(self.site_path))
            if _repl_mode and root in _site_cache:
                self._site = _site_cache[root]
            else:
                self._site = Site(root, Session(root))
                _site_cache[root] = self._site
            self._site._styles.clear()
        return self._site


pass_state = click.make_pass_decorator(State)


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------
def _scalar(v, width=60):
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    s = "" if v is None else str(v)
    return s if len(s) <= width else s[: width - 1] + "…"


def emit(result, use_json: bool) -> None:
    if result is None:
        return
    if use_json:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if isinstance(result, list):
        if not result:
            click.echo("(none)")
            return
        if all(isinstance(r, dict) for r in result):
            cols = [k for k, v in result[0].items() if not isinstance(v, (dict, list)) or k in ("categories",)]
            cols = cols[:6]
            widths = {c: min(60, max(len(c), *(len(_scalar(r.get(c))) for r in result))) for c in cols}
            click.echo("  ".join(c.ljust(widths[c]) for c in cols))
            click.echo("  ".join("-" * widths[c] for c in cols))
            for r in result:
                click.echo("  ".join(_scalar(r.get(c), widths[c]).ljust(widths[c]) for c in cols))
        else:
            for r in result:
                click.echo(_scalar(r, 200))
        return
    if isinstance(result, dict):
        for k, v in result.items():
            if k == "changes" and v:
                click.echo("changes:")
                for c in v:
                    click.echo(f"  {c['action']:<7} {c['path']}")
            elif isinstance(v, list) and v and all(isinstance(x, dict) for x in v) and k in ("errors", "warnings", "problems"):
                click.echo(f"{k}: {len(v)}")
                for x in v:
                    click.echo(f"  - {x.get('where', '')}: {x.get('problem', '')}")
            elif isinstance(v, list) and k in ("problems",):
                click.echo(f"{k}: {len(v)}")
                for x in v:
                    click.echo(f"  - {x}")
            else:
                click.echo(f"{k}: {_scalar(v, 160)}")
        return
    click.echo(str(result))


def fail(message: str, use_json: bool) -> None:
    if use_json:
        click.echo(json.dumps({"error": message}, ensure_ascii=False))
    else:
        click.echo(f"Error: {message}", err=True)


# ---------------------------------------------------------------------------
# root group
# ---------------------------------------------------------------------------
@click.group(invoke_without_command=True)
@click.option("--site", "site_path", default=None, metavar="PATH",
              help="Site folder (default: $DEVLENS_SITE, or the nearest folder with src/data/home.json).")
@click.option("--json", "use_json", is_flag=True, help="Machine-readable JSON output.")
@click.option("--dry-run", "dry_run", is_flag=True, help="Show what would change without writing files.")
@click.version_option(__version__, prog_name="cli-anything-devlens")
@click.pass_context
def cli(ctx, site_path, use_json, dry_run):
    """Manage the Devlens Bangladesh website: stories, jobs, homepage, images and builds."""
    ctx.obj = State(site_path, use_json, dry_run)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.result_callback()
@click.pass_context
def finish(ctx, result, site_path, use_json, dry_run):
    state: State = ctx.obj
    site = state._site
    if site is not None and site.session.pending():
        changes = site.session.pending()
        if dry_run:
            site.session.discard()
            saved = False
        else:
            command = " ".join(ctx.meta.get("devlens_argv", sys.argv[1:]))
            site.session.commit(command)
            saved = True
        if isinstance(result, dict):
            result = {**result, "changes": changes, "saved": saved, "dry_run": dry_run}
        else:
            result = {"result": result, "changes": changes, "saved": saved, "dry_run": dry_run}
    elif site is not None:
        site.session.discard()
    ctx.meta["devlens_result"] = result
    emit(result, use_json)


# ---------------------------------------------------------------------------
# site
# ---------------------------------------------------------------------------
@cli.group()
def site():
    """Site overview and content checks."""


@site.command("info")
@click.option("--today", default=None, help="Treat this date (YYYY-MM-DD) as today.")
@pass_state
def site_info(state, today):
    """Counts of stories, jobs, funding calls and current homepage picks."""
    return state.site.info(today)


@site.command("validate")
@click.option("--today", default=None, help="Treat this date (YYYY-MM-DD) as today.")
@click.option("--strict", is_flag=True, help="Fail on warnings too.")
@click.pass_context
def site_validate(ctx, today, strict):
    """Check all content: JSON, slugs, dates, categories, images, homepage links, jobs."""
    state = ctx.obj
    res = validate_mod.run(state.site, today)
    if strict and res["warnings"]:
        res["ok"] = False
    if not res["ok"]:
        emit(res, state.use_json)
        ctx.exit(1)
    return res


# ---------------------------------------------------------------------------
# post
# ---------------------------------------------------------------------------
@cli.group()
def post():
    """Stories in src/data/posts."""


@post.command("list")
@click.option("--category", default=None)
@click.option("--tag", default=None)
@click.option("--since", default=None, help="Only stories on or after YYYY-MM-DD.")
@click.option("--search", default=None, help="Text to find in title or excerpt.")
@click.option("--limit", type=int, default=20, show_default=True, help="0 for all.")
@pass_state
def post_list(state, category, tag, since, search, limit):
    """List stories, newest first."""
    return posts_mod.list_posts(state.site, category, tag, since, search, limit or None)


@post.command("show")
@click.argument("slug")
@click.option("--no-content", is_flag=True, help="Leave out the HTML body.")
@pass_state
def post_show(state, slug, no_content):
    """Show one story."""
    p = posts_mod.get(state.site, slug)
    if no_content:
        p = {k: v for k, v in p.items() if k != "content"}
    return p


@post.command("add")
@click.option("--title", required=True)
@click.option("--excerpt", required=True, help="One- or two-sentence summary.")
@click.option("--category", "categories", multiple=True, required=True, help="Repeat for more.")
@click.option("--tag", "tags", multiple=True, help="Repeat for more.")
@click.option("--content", default=None, help="HTML body.")
@click.option("--content-file", default=None, type=click.Path(), help="File holding the HTML body.")
@click.option("--slug", default=None, help="Default: made from the title.")
@click.option("--date", default=None, help="YYYY-MM-DD[THH:MM[:SS]] Dhaka time. Default: now.")
@click.option("--image", default=None, help="Image src under /media/, e.g. /media/2026/11/x.jpg")
@click.option("--image-alt", default=None)
@click.option("--credit", default=None, help="Photo credit line.")
@click.option("--credit-url", default=None)
@pass_state
def post_add(state, title, excerpt, categories, tags, content, content_file, slug, date,
             image, image_alt, credit, credit_url):
    """Add a new story."""
    p = posts_mod.add(state.site, title, excerpt, list(categories), list(tags), content,
                      content_file, slug, date, image, image_alt, credit, credit_url)
    return {"added": p["slug"], "date": p["date"], "url": _post_url(p)}


def _post_url(p):
    y, m, d = p["date"][:10].split("-")
    return f"/{y}/{m}/{d}/{p['slug']}/"


@post.command("update")
@click.argument("slug")
@click.option("--title", default=None)
@click.option("--excerpt", default=None)
@click.option("--content", default=None)
@click.option("--content-file", default=None, type=click.Path())
@click.option("--add-category", multiple=True)
@click.option("--remove-category", multiple=True)
@click.option("--add-tag", multiple=True)
@click.option("--remove-tag", multiple=True)
@click.option("--image", default=None)
@click.option("--image-alt", default=None)
@click.option("--credit", default=None)
@click.option("--credit-url", default=None)
@click.option("--date", default=None, help="Change the publish date (moves the URL).")
@click.option("--no-touch", is_flag=True, help="Do not update the 'modified' time.")
@pass_state
def post_update(state, slug, title, excerpt, content, content_file, add_category, remove_category,
                add_tag, remove_tag, image, image_alt, credit, credit_url, date, no_touch):
    """Change fields of a story."""
    return posts_mod.update(state.site, slug, title, excerpt, content, content_file,
                            add_category, remove_category, add_tag, remove_tag, image,
                            image_alt, credit, credit_url, date, touch=not no_touch)


@post.command("remove")
@click.argument("slug")
@click.option("--force", is_flag=True, help="Also drop it from homepage lists.")
@pass_state
def post_remove(state, slug, force):
    """Delete a story."""
    return posts_mod.remove(state.site, slug, force)


@post.command("slugify")
@click.argument("title")
def post_slugify(title):
    """Show the slug a title would get."""
    return {"slug": slugify(title)}


# ---------------------------------------------------------------------------
# category / tag
# ---------------------------------------------------------------------------
@cli.group()
def category():
    """Story categories."""


@category.command("list")
@pass_state
def category_list(state):
    """List categories."""
    return state.site.categories()


@cli.group()
def tag():
    """Story tags."""


@tag.command("list")
@click.option("--search", default=None)
@pass_state
def tag_list(state, search):
    """List tags."""
    tags = state.site.tags()
    if search:
        tags = [t for t in tags if search.lower() in (t["slug"] + t["name"]).lower()]
    return tags


@tag.command("add")
@click.option("--name", required=True)
@click.option("--slug", default=None)
@click.option("--description", default="")
@pass_state
def tag_add(state, name, slug, description):
    """Add a tag."""
    slug = slug or slugify(name)
    tags = state.site.tags()
    if any(t["slug"] == slug for t in tags):
        raise SiteError(f"Tag {slug!r} already exists")
    tags.append({"slug": slug, "name": name, "description": description})
    tags.sort(key=lambda t: t["slug"])
    state.site.write_json(TAGS, tags)
    return {"added": slug, "name": name}


# ---------------------------------------------------------------------------
# job
# ---------------------------------------------------------------------------
@cli.group()
def job():
    """Job listings in src/data/jobs.json."""


@job.command("list")
@click.option("--sector", default=None)
@click.option("--org", default=None, help="Text to find in the organisation name.")
@click.option("--status", type=click.Choice(["all", "open", "expired"]), default="all", show_default=True)
@click.option("--today", default=None)
@pass_state
def job_list(state, sector, org, status, today):
    """List jobs (index, title, org, deadline...)."""
    rows = jobs_mod.list_jobs(state.site, sector, status, org, today)
    if state.use_json:
        return rows
    return [{"index": r["index"], "title": r["title"], "org": r["org"], "sector": r["sector"],
             "deadline": r.get("deadline"), "open": r["open"]} for r in rows]


@job.command("sectors")
@pass_state
def job_sectors(state):
    """List job sectors."""
    return jobs_mod.sectors(state.site)


@job.command("add")
@click.option("--title", required=True)
@click.option("--org", required=True)
@click.option("--sector", required=True, help="Sector id (see 'job sectors').")
@click.option("--url", required=True)
@click.option("--location", required=True)
@click.option("--deadline", default=None, help="YYYY-MM-DD; leave out for open-ended.")
@click.option("--deadline-text", default=None, help="Default: '26 November 2026'.")
@click.option("--contract", default="Full-time", show_default=True)
@click.option("--ref", default="")
@click.option("--badge", default=None, help="Default: the organisation name.")
@click.option("--nationals", is_flag=True, help="Open to Bangladeshi nationals only.")
@click.option("--consultancy", is_flag=True)
@click.option("--button", default="View advert", show_default=True)
@click.option("--featured", default=None, help="Ribbon text, e.g. 'UN AGENCY'.")
@click.option("--added", default=None, help="YYYY-MM-DD. Default: today in Dhaka.")
@pass_state
def job_add(state, title, org, sector, url, location, deadline, deadline_text, contract, ref,
            badge, nationals, consultancy, button, featured, added):
    """Add a job at the top of the list."""
    j = jobs_mod.add(state.site, title, org, sector, url, location, deadline, contract, ref,
                     badge, nationals, consultancy, button, featured, added, deadline_text)
    return {"added": j["title"], "org": j["org"], "deadline": j["deadline"]}


@job.command("update")
@click.option("--url", default=None, help="Find the job by its url.")
@click.option("--index", type=int, default=None, help="Or by its index from 'job list'.")
@click.option("--title", default=None)
@click.option("--org", default=None)
@click.option("--sector", default=None)
@click.option("--location", default=None)
@click.option("--deadline", default=None)
@click.option("--contract", default=None)
@click.option("--featured", default=None)
@click.option("--new-url", default=None)
@pass_state
def job_update(state, url, index, title, org, sector, location, deadline, contract, featured, new_url):
    """Change fields of a job."""
    return jobs_mod.update(state.site, url, index, title=title, org=org, sector=sector,
                           location=location, deadline=deadline, contract=contract,
                           featured=featured, url=new_url)


@job.command("remove")
@click.option("--url", default=None)
@click.option("--index", type=int, default=None)
@pass_state
def job_remove(state, url, index):
    """Remove a job."""
    return jobs_mod.remove(state.site, url, index)


@job.command("prune")
@click.option("--today", default=None, help="Default: today in Dhaka.")
@pass_state
def job_prune(state, today):
    """Remove jobs whose deadline has passed."""
    return jobs_mod.prune(state.site, today)


# ---------------------------------------------------------------------------
# home
# ---------------------------------------------------------------------------
@cli.group()
def home():
    """Homepage picks, numbers, funding calls and spotlight (src/data/home.json)."""


@home.command("show")
@click.argument("section", required=False)
@pass_state
def home_show(state, section):
    """Show the homepage data, or one section of it."""
    return home_mod.show(state.site, section)


def _feature_opts(f):
    f = click.option("--summary", default=None, help="Default: the story's excerpt.")(f)
    f = click.option("--headline", default=None, help="Default: the story's title.")(f)
    f = click.option("--label", default=None, help="e.g. 'Humanitarian · Rohingya'.")(f)
    return f


@home.command("set-lead")
@click.argument("slug")
@_feature_opts
@click.option("--demote", is_flag=True, help="Move the old lead to the top of 'Also today' extras.")
@pass_state
def home_set_lead(state, slug, label, headline, summary, demote):
    """Make a story the homepage lead."""
    return home_mod.set_lead(state.site, slug, label, headline, summary, demote)


@home.command("set-also")
@click.argument("slug")
@_feature_opts
@pass_state
def home_set_also(state, slug, label, headline, summary):
    """Make a story the 'Also today' feature."""
    return home_mod.set_also(state.site, slug, label, headline, summary)


@home.command("set-special")
@click.argument("slug")
@_feature_opts
@click.option("--published", default=None, help="YYYY-MM-DD; shown for 7 days. Default: today.")
@pass_state
def home_set_special(state, slug, label, headline, summary, published):
    """Set the Devlens Special feature."""
    return home_mod.set_special(state.site, slug, label, headline, summary, published)


@home.group("plus")
def home_plus():
    """The extra 'Also today' story list."""


@home_plus.command("list")
@pass_state
def home_plus_list(state):
    """List the extra stories in order."""
    return home_mod.plus_list(state.site)


@home_plus.command("add")
@click.argument("slug")
@click.option("--position", type=int, default=0, show_default=True)
@pass_state
def home_plus_add(state, slug, position):
    """Add a story to the list (top by default)."""
    return home_mod.plus_add(state.site, slug, position)


@home_plus.command("remove")
@click.argument("slug")
@pass_state
def home_plus_remove(state, slug):
    """Remove a story from the list."""
    return home_mod.plus_remove(state.site, slug)


@home_plus.command("trim")
@click.option("--keep", type=int, required=True)
@pass_state
def home_plus_trim(state, keep):
    """Keep only the first N stories."""
    return home_mod.plus_trim(state.site, keep)


@home.group("number")
def home_number():
    """Homepage key numbers."""


@home_number.command("list")
@pass_state
def home_number_list(state):
    """List the key numbers."""
    return home_mod.show(state.site, "numbers")


@home_number.command("add")
@click.option("--value", required=True, help="e.g. '71.0%'")
@click.option("--label", required=True)
@click.option("--source", required=True, help="e.g. 'ADB, Nov 2026'")
@click.option("--position", type=int, default=0, show_default=True)
@click.option("--keep", type=int, default=None, help="Then keep only the first N.")
@pass_state
def home_number_add(state, value, label, source, position, keep):
    """Add a key number."""
    return home_mod.number_add(state.site, value, label, source, position, keep)


@home_number.command("remove")
@click.argument("index", type=int)
@pass_state
def home_number_remove(state, index):
    """Remove a key number by index."""
    return home_mod.number_remove(state.site, index)


@home.group("funding")
def home_funding():
    """Funding calls with deadlines."""


@home_funding.command("list")
@pass_state
def home_funding_list(state):
    """List funding calls."""
    return home_mod.show(state.site, "funding")


@home_funding.command("add")
@click.option("--title", required=True)
@click.option("--funder", required=True)
@click.option("--deadline", required=True, help="YYYY-MM-DD")
@click.option("--url", required=True)
@pass_state
def home_funding_add(state, title, funder, deadline, url):
    """Add a funding call (kept sorted by deadline)."""
    return home_mod.funding_add(state.site, title, funder, deadline, url)


@home_funding.command("remove")
@click.option("--url", required=True)
@pass_state
def home_funding_remove(state, url):
    """Remove a funding call."""
    return home_mod.funding_remove(state.site, url)


@home_funding.command("prune")
@click.option("--today", default=None)
@pass_state
def home_funding_prune(state, today):
    """Remove funding calls whose deadline has passed."""
    return home_mod.funding_prune(state.site, today)


@home.command("pills")
@click.option("--funding-open", type=int, default=None)
@click.option("--new-reports", type=int, default=None)
@click.option("--key-numbers", type=int, default=None)
@pass_state
def home_pills(state, funding_open, new_reports, key_numbers):
    """Set the counter pills (no options: just show them)."""
    if funding_open is None and new_reports is None and key_numbers is None:
        return home_mod.show(state.site, "pills")
    return home_mod.pills_set(state.site, funding_open, new_reports, key_numbers)


@home.command("spotlight-today")
@click.option("--date", "date_label", required=True, help="Display date, e.g. '19 Nov'.")
@click.option("--text", required=True)
@click.option("--source", "sources", multiple=True, help="'Name|https://url', repeat for more.")
@pass_state
def home_spotlight_today(state, date_label, text, sources):
    """Replace the spotlight's 'today' update."""
    return home_mod.spotlight_set_today(state.site, date_label, text, list(sources))


# ---------------------------------------------------------------------------
# media
# ---------------------------------------------------------------------------
@cli.group()
def media():
    """Images in public/media/YYYY/MM."""


@media.command("add")
@click.argument("file", type=click.Path())
@click.option("--month", default=None, help="YYYY-MM folder. Default: this month.")
@click.option("--name", default=None, help="File name to use.")
@click.option("--overwrite", is_flag=True)
@pass_state
def media_add(state, file, month, name, overwrite):
    """Copy an image into the site and report its src and size."""
    return media_mod.add(state.site, file, month, name, overwrite)


@media.command("info")
@click.argument("src")
@pass_state
def media_info(state, src):
    """Format and size of an image, e.g. /media/2026/11/x.jpg"""
    return media_mod.info(state.site, src)


@media.command("list")
@click.option("--month", default=None, help="YYYY-MM")
@pass_state
def media_list(state, month):
    """List images."""
    return media_mod.list_media(state.site, month)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
@cli.group()
def build():
    """Build the site with Astro and check the output."""


@build.command("run")
@click.option("--out", "out_dir", default=None, help="Output folder. Default: <site>/dist")
@click.option("--skip-validate", is_flag=True)
@click.pass_context
def build_run(ctx, out_dir, skip_validate):
    """Validate content, run 'astro build', then check the generated pages."""
    state = ctx.obj
    if not skip_validate:
        v = validate_mod.run(state.site)
        if not v["ok"]:
            emit({"ok": False, "stage": "validate", "errors": v["errors"]}, state.use_json)
            ctx.exit(1)
    res = build_mod.run(state.site, out_dir)
    if not res["ok"]:
        emit(res, state.use_json)
        ctx.exit(1)
    return res


@build.command("verify")
@click.option("--out", "out_dir", default=None)
@click.option("--slug", "slugs", multiple=True, help="Only check these stories.")
@click.pass_context
def build_verify(ctx, out_dir, slugs):
    """Check an existing build folder against the content."""
    state = ctx.obj
    res = build_mod.verify(state.site, out_dir, list(slugs) or None)
    if not res["ok"]:
        emit(res, state.use_json)
        ctx.exit(1)
    return res


@build.command("backend")
@pass_state
def build_backend(state):
    """Show the Node and Astro versions the build uses."""
    from cli_anything.devlens.utils import astro_backend
    return astro_backend.version(state.site.root)


# ---------------------------------------------------------------------------
# session
# ---------------------------------------------------------------------------
@cli.group()
def session():
    """Undo, redo and history of changes made with this CLI."""


@session.command("status")
@pass_state
def session_status(state):
    """Site path and undo/redo depth."""
    h = state.site.session.history()
    return {"site": str(state.site.root), "undo_steps": len(h["undo"]), "redo_steps": len(h["redo"]),
            "last": h["undo"][-1]["command"] if h["undo"] else None}


@session.command("history")
@pass_state
def session_history(state):
    """List recorded changes, oldest first."""
    h = state.site.session.history()
    return [{"step": i + 1, "time": t["time"], "command": t["command"],
             "files": len(t["files"])} for i, t in enumerate(h["undo"])]


@session.command("undo")
@click.option("--force", is_flag=True, help="Undo even if files changed outside the CLI.")
@pass_state
def session_undo(state, force):
    """Undo the last change."""
    if state.dry_run:
        h = state.site.session.history()
        return {"would_undo": h["undo"][-1]["command"] if h["undo"] else None, "dry_run": True}
    return state.site.session.undo(force)


@session.command("redo")
@click.option("--force", is_flag=True)
@pass_state
def session_redo(state, force):
    """Redo the last undone change."""
    if state.dry_run:
        h = state.site.session.history()
        return {"would_redo": h["redo"][-1]["command"] if h["redo"] else None, "dry_run": True}
    return state.site.session.redo(force)


# ---------------------------------------------------------------------------
# repl
# ---------------------------------------------------------------------------
REPL_HELP = {
    "site info | validate": "Overview and content checks",
    "post list|show|add|update|remove": "Stories",
    "job list|sectors|add|update|remove|prune": "Job listings",
    "home show|set-lead|set-also|set-special|plus|number|funding|pills": "Homepage",
    "media add|info|list": "Images in public/media",
    "category list | tag list|add": "Categories and tags",
    "build run|verify|backend": "Astro build and output checks",
    "session status|history|undo|redo": "Undo and history",
    "help | exit": "This help, or leave",
}


def run_args(args: list[str], use_json_default: bool = False) -> int:
    """Run one command line; return an exit code. Used by main() and the REPL."""
    use_json = "--json" in args or use_json_default
    try:
        ctx = cli.make_context("cli-anything-devlens", list(args))
        ctx.meta["devlens_argv"] = list(args)
        with ctx:
            cli.invoke(ctx)
        return 0
    except click.exceptions.Exit as e:
        return e.exit_code
    except click.ClickException as e:
        if use_json:
            fail(e.format_message(), True)
        else:
            e.show()
        return e.exit_code
    except click.exceptions.Abort:
        return 1
    except KNOWN_ERRORS as e:
        fail(str(e), use_json)
        return 1


@cli.command()
@click.pass_context
def repl(ctx):
    """Interactive mode (the default when no command is given)."""
    global _repl_mode
    from cli_anything.devlens.utils.repl_skin import ReplSkin

    state: State = ctx.obj
    base = []
    if state.site_path:
        base += ["--site", state.site_path]
    if state.use_json:
        base += ["--json"]
    if state.dry_run:
        base += ["--dry-run"]
    _repl_mode = True
    skin = ReplSkin("devlens", version=__version__)
    skin.print_banner()
    try:
        skin.info(f"Site: {state.site.root}")
    except SiteError as e:
        skin.warning(str(e))
    skin.info("Each command writes its changes straight away; use 'session undo' to step back.")
    pt = skin.create_prompt_session()
    while True:
        try:
            line = skin.get_input(pt, project_name="devlens", modified=False)
        except (EOFError, KeyboardInterrupt):
            break
        line = (line or "").strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            break
        if line in ("help", "?"):
            skin.help(REPL_HELP)
            continue
        try:
            args = shlex.split(line)
        except ValueError as e:
            skin.error(str(e))
            continue
        run_args(base + args)
    skin.print_goodbye()
    _repl_mode = False


def main(argv=None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    sys.exit(run_args(args))


if __name__ == "__main__":
    main()
