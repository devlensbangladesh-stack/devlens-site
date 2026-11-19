"""Build the site with Astro and check the generated HTML."""

from __future__ import annotations

import html
import re
from pathlib import Path

from cli_anything.devlens.core.site import Site, SiteError, today_dhaka
from cli_anything.devlens.utils import astro_backend


def post_page(out: Path, post: dict) -> Path:
    y, m, d = post["date"][:10].split("-")
    return out / y / m / d / post["slug"] / "index.html"


def _text(path: Path) -> str:
    return html.unescape(path.read_text(encoding="utf-8", errors="replace"))


def verify(site: Site, out_dir: str | None = None, slugs: list[str] | None = None) -> dict:
    """Check a built site folder against the content in src/data."""
    out = Path(out_dir).resolve() if out_dir else site.root / "dist"
    if not out.is_dir():
        raise SiteError(f"No build output at {out}; run 'build run' first")
    problems = []
    index = out / "index.html"
    if not index.is_file():
        problems.append("index.html missing")
        index_text = ""
    else:
        index_text = _text(index)
        if not index_text.lstrip().lower().startswith("<!doctype html"):
            problems.append("index.html does not start with <!DOCTYPE html>")
    home = site.home()
    for key in ("lead", "alsoToday"):
        h = (home.get(key) or {}).get("headline")
        if h and h not in index_text:
            problems.append(f"homepage does not show the {key} headline: {h}")

    posts = site.posts()
    if slugs:
        posts = [p for p in posts if p["slug"] in slugs]
        missing = set(slugs) - {p["slug"] for p in posts}
        problems += [f"no such story: {s}" for s in sorted(missing)]
    checked = 0
    for p in posts:
        page = post_page(out, p)
        if not page.is_file():
            problems.append(f"page missing for {p['slug']}: {page.relative_to(out)}")
            continue
        if p["title"] not in _text(page):
            problems.append(f"page for {p['slug']} does not contain its title")
        checked += 1

    sitemap = out / "sitemap.xml"
    feed = out / "feed.xml"
    for f in (sitemap, feed):
        if not f.is_file():
            problems.append(f"{f.name} missing")
        elif not f.read_text(encoding="utf-8")[:200].lstrip().startswith("<?xml"):
            problems.append(f"{f.name} is not XML")
    jobs_page = out / "jobs" / "index.html"
    if not jobs_page.is_file():
        problems.append("jobs/index.html missing")

    pages = list(out.rglob("index.html"))
    return {
        "ok": not problems,
        "out_dir": str(out),
        "html_pages": len(pages),
        "stories_checked": checked,
        "bytes": sum(f.stat().st_size for f in out.rglob("*") if f.is_file()),
        "problems": problems,
    }


def run(site: Site, out_dir: str | None = None, today: str | None = None) -> dict:
    out = Path(out_dir).resolve() if out_dir else None
    res = astro_backend.build(site.root, out)
    m = re.search(r"(\d+) page\(s\) built", res["log"])
    report = verify(site, out_dir)
    report.update({"astro_pages": int(m.group(1)) if m else None,
                   "seconds": res["seconds"], "command": res["command"],
                   "today": today or today_dhaka()})
    return report
