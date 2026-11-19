"""Content checks that catch what breaks or degrades the site build."""

from __future__ import annotations

import json
import re
from collections import Counter

from cli_anything.devlens.core.site import (DATA, DATE_RE, DATETIME_RE, SLUG_RE, Site,
                                            today_dhaka)

POST_REQUIRED = ["slug", "date", "modified", "title", "excerpt", "categories", "tags", "content"]
JOB_REQUIRED = ["title", "org", "sector", "url", "location", "deadlineText", "added"]


def run(site: Site, today: str | None = None) -> dict:
    today = today or today_dhaka()
    errors: list[dict] = []
    warnings: list[dict] = []
    err = lambda where, msg: errors.append({"where": where, "problem": msg})
    warn = lambda where, msg: warnings.append({"where": where, "problem": msg})

    # 1. every JSON file parses (same check as the auto-merge workflow)
    for p in sorted((site.root / DATA).rglob("*.json")):
        rel = p.relative_to(site.root).as_posix()
        raw = site.session.read_bytes(rel)
        if raw is None:
            continue
        try:
            json.loads(raw.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            err(rel, f"invalid JSON: {e}")
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings, "checked": {}}

    cats = {c["slug"] for c in site.categories()}
    tags = {t["slug"] for t in site.tags()}
    posts = site.posts()
    slugs = {p.get("slug") for p in posts}

    # 2. stories
    for slug_file in site.post_slugs():
        p = site.read_json(site.post_path(slug_file))
        where = f"post {slug_file}"
        missing = [k for k in POST_REQUIRED if k not in p]
        if missing:
            err(where, f"missing fields: {', '.join(missing)}")
            continue
        if p["slug"] != slug_file:
            err(where, f"slug {p['slug']!r} does not match the file name")
        if not SLUG_RE.match(p["slug"]):
            err(where, "slug must be lowercase words joined by hyphens")
        for k in ("date", "modified"):
            if not DATETIME_RE.match(str(p[k])):
                err(where, f"{k} must be YYYY-MM-DDTHH:MM:SS, got {p[k]!r}")
        if DATETIME_RE.match(str(p["date"])) and DATETIME_RE.match(str(p["modified"])) \
                and p["modified"] < p["date"]:
            warn(where, "modified is earlier than date")
        if not str(p["title"]).strip():
            err(where, "empty title")
        if not str(p["excerpt"]).strip():
            warn(where, "empty excerpt")
        if not str(p["content"]).strip():
            err(where, "empty content")
        if not p["categories"]:
            err(where, "no categories")
        for c in p["categories"]:
            if c not in cats:
                err(where, f"unknown category {c!r}")
        for t in p["tags"]:
            if t not in tags:
                warn(where, f"tag {t!r} is not in tags.json (shown with a generated name)")
        img = p.get("image")
        if img:
            src = img.get("src", "")
            if src.startswith("/media/") and not site.session.exists(site.public_file(src)):
                err(where, f"image file not found: public{src}")
            if not img.get("alt"):
                warn(where, "image has no alt text")
            if img.get("credit") is None and "commons.wikimedia" in str(img.get("creditUrl", "")):
                warn(where, "Wikimedia image without a credit line")
        else:
            warn(where, "no image")
        for src in re.findall(r'<img[^>]+src="(/media/[^"?]+)', p["content"]):
            if not site.session.exists(site.public_file(src)):
                err(where, f"image in content not found: public{src}")

    dupes = [t for t, n in Counter(p["title"] for p in posts if "title" in p).items() if n > 1]
    for t in dupes:
        warn("posts", f"duplicate title: {t}")

    # 3. homepage
    home = site.home()
    for key in ("lead", "alsoToday", "special"):
        s = (home.get(key) or {}).get("slug")
        if not s:
            err(f"home.{key}", "missing slug")
        elif s not in slugs:
            err(f"home.{key}", f"story not found: {s}")
    plus = (home.get("alsoToday") or {}).get("plus", [])
    for s in plus:
        if s not in slugs:
            err("home.alsoToday.plus", f"story not found: {s}")
    for s, n in Counter(plus).items():
        if n > 1:
            warn("home.alsoToday.plus", f"listed {n} times: {s}")
    for m in home.get("pinnedSpecials", []):
        if m.get("slug") not in slugs:
            err("home.pinnedSpecials", f"story not found: {m.get('slug')}")
    sp = home.get("special") or {}
    if sp.get("published") and not DATE_RE.match(sp["published"]):
        err("home.special", "published must be YYYY-MM-DD")
    for i, f in enumerate(home.get("funding", [])):
        where = f"home.funding[{i}]"
        if not DATE_RE.match(str(f.get("deadline", ""))):
            err(where, f"deadline must be YYYY-MM-DD, got {f.get('deadline')!r}")
        elif f["deadline"] < today:
            warn(where, f"deadline passed ({f['deadline']}): {f.get('title')}")
        if not str(f.get("url", "")).startswith(("http://", "https://")):
            err(where, "url must start with http(s)://")
    for i, n in enumerate(home.get("numbers", [])):
        for k in ("value", "label", "source"):
            if not n.get(k):
                err(f"home.numbers[{i}]", f"missing {k}")

    # 4. jobs
    jd = site.jobs_data()
    sectors = {s["id"] for s in jd.get("sectors", [])}
    expired = 0
    for i, j in enumerate(jd.get("jobs", [])):
        where = f"job[{i}] {j.get('title', '')[:50]}"
        missing = [k for k in JOB_REQUIRED if k not in j]
        if missing:
            err(where, f"missing fields: {', '.join(missing)}")
        if j.get("sector") not in sectors:
            err(where, f"unknown sector {j.get('sector')!r}")
        d = j.get("deadline")
        if d is not None and not DATE_RE.match(str(d)):
            err(where, f"deadline must be YYYY-MM-DD or null, got {d!r}")
        elif d and d < today:
            expired += 1
        if not str(j.get("url", "")).startswith(("http://", "https://")):
            err(where, "url must start with http(s)://")
    if expired:
        warn("jobs", f"{expired} job(s) past their deadline; run 'job prune'")
    for u, n in Counter(j.get("url") for j in jd.get("jobs", [])).items():
        if n > 1:
            warn("jobs", f"url listed {n} times: {u}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": {"posts": len(posts), "jobs": len(jd.get("jobs", [])),
                    "funding": len(home.get("funding", [])), "today": today},
    }
