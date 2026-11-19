"""Stories in src/data/posts/<slug>.json."""

from __future__ import annotations

from pathlib import Path

from cli_anything.devlens.core import media
from cli_anything.devlens.core.site import (DATETIME_RE, HOME, SLUG_RE, Site,
                                            SiteError, now_dhaka, slugify)

FIELDS = ["slug", "date", "modified", "title", "excerpt", "categories", "tags", "image", "content"]


def _now() -> str:
    return now_dhaka().strftime("%Y-%m-%dT%H:%M:%S")


def _norm_datetime(value: str | None) -> str:
    if not value:
        return _now()
    if len(value) == 10:
        value += "T09:00:00"
    elif len(value) == 16:
        value += ":00"
    if not DATETIME_RE.match(value):
        raise SiteError(f"Date must be YYYY-MM-DD or YYYY-MM-DDTHH:MM[:SS], got {value!r}")
    return value


def get(site: Site, slug: str) -> dict:
    rel = site.post_path(slug)
    if not site.session.exists(rel):
        raise SiteError(f"No story with slug {slug!r}")
    return site.read_json(rel)


def summary(p: dict) -> dict:
    return {"slug": p["slug"], "date": p["date"], "title": p["title"],
            "categories": p.get("categories", []), "image": (p.get("image") or {}).get("src")}


def list_posts(site: Site, category=None, tag=None, since=None, search=None, limit=None) -> list[dict]:
    out = []
    for p in site.posts():
        if category and category not in p.get("categories", []):
            continue
        if tag and tag not in p.get("tags", []):
            continue
        if since and p["date"][:10] < since:
            continue
        if search and search.lower() not in (p["title"] + " " + p.get("excerpt", "")).lower():
            continue
        out.append(summary(p))
    return out[:limit] if limit else out


def _check_terms(site: Site, categories, tags):
    cats = {c["slug"] for c in site.categories()}
    bad = [c for c in categories if c not in cats]
    if bad:
        raise SiteError(f"Unknown categories: {', '.join(bad)} (see 'category list')")
    known = {t["slug"] for t in site.tags()}
    bad = [t for t in tags if t not in known]
    if bad:
        raise SiteError(f"Unknown tags: {', '.join(bad)} (see 'tag list', or add with 'tag add')")


def _image(site: Site, src, alt, credit=None, credit_url=None, title=""):
    if not src:
        return None
    if not src.startswith("/media/"):
        raise SiteError(f"Image src must start with /media/, got {src!r}")
    meta = media.info(site, src)
    img = {"src": meta["src"], "alt": alt or f"Illustration for the story: {title}",
           "width": meta["width"], "height": meta["height"]}
    if credit:
        img["credit"] = credit
    if credit_url:
        img["creditUrl"] = credit_url
    return img


def _content(content=None, content_file=None) -> str | None:
    if content_file:
        p = Path(content_file).expanduser()
        if not p.is_file():
            raise SiteError(f"No such file: {content_file}")
        return p.read_text(encoding="utf-8")
    return content


def add(site: Site, title: str, excerpt: str, categories: list[str], tags: list[str] = (),
        content: str | None = None, content_file: str | None = None, slug: str | None = None,
        date: str | None = None, image: str | None = None, image_alt: str | None = None,
        credit: str | None = None, credit_url: str | None = None) -> dict:
    slug = slug or slugify(title)
    if not SLUG_RE.match(slug):
        raise SiteError(f"Slug must be lowercase words joined by hyphens, got {slug!r}")
    if site.session.exists(site.post_path(slug)):
        raise SiteError(f"A story with slug {slug!r} already exists; use 'post update'")
    if not title.strip() or not excerpt.strip():
        raise SiteError("Title and excerpt are required")
    if not categories:
        raise SiteError("At least one --category is required")
    body = _content(content, content_file)
    if not body or not body.strip():
        raise SiteError("Story content is required (--content or --content-file)")
    _check_terms(site, categories, list(tags))
    when = _norm_datetime(date)
    post = {
        "slug": slug, "date": when, "modified": when, "title": title.strip(),
        "excerpt": excerpt.strip(), "categories": list(dict.fromkeys(categories)),
        "tags": sorted(set(tags)),
        "image": _image(site, image, image_alt, credit, credit_url, title),
        "content": body,
    }
    site.write_json(site.post_path(slug), post)
    return post


def update(site: Site, slug: str, title=None, excerpt=None, content=None, content_file=None,
           add_categories=(), remove_categories=(), add_tags=(), remove_tags=(),
           image=None, image_alt=None, credit=None, credit_url=None, date=None,
           touch: bool = True) -> dict:
    post = get(site, slug)
    changed = []
    if title is not None:
        post["title"] = title.strip(); changed.append("title")
    if excerpt is not None:
        post["excerpt"] = excerpt.strip(); changed.append("excerpt")
    body = _content(content, content_file)
    if body is not None:
        post["content"] = body; changed.append("content")
    if add_categories or remove_categories:
        cats = [c for c in post["categories"] if c not in remove_categories]
        cats += [c for c in add_categories if c not in cats]
        if not cats:
            raise SiteError("A story needs at least one category")
        post["categories"] = cats; changed.append("categories")
    if add_tags or remove_tags:
        post["tags"] = sorted((set(post["tags"]) - set(remove_tags)) | set(add_tags))
        changed.append("tags")
    _check_terms(site, list(add_categories), list(add_tags))
    if image is not None:
        post["image"] = _image(site, image, image_alt or (post.get("image") or {}).get("alt"),
                               credit, credit_url, post["title"])
        changed.append("image")
    elif any(v is not None for v in (image_alt, credit, credit_url)):
        if not post.get("image"):
            raise SiteError("The story has no image; pass --image first")
        if image_alt is not None:
            post["image"]["alt"] = image_alt
        if credit is not None:
            post["image"]["credit"] = credit
        if credit_url is not None:
            post["image"]["creditUrl"] = credit_url
        changed.append("image")
    if date is not None:
        post["date"] = _norm_datetime(date); changed.append("date")
    if not changed:
        raise SiteError("Nothing to update; pass at least one field")
    if touch:
        post["modified"] = max(_now(), post["date"])
    site.write_json(site.post_path(slug), post)
    return {"slug": slug, "changed": changed, "modified": post["modified"]}


def references(site: Site, slug: str) -> list[str]:
    home = site.home()
    refs = []
    for key in ("lead", "alsoToday", "special"):
        if (home.get(key) or {}).get("slug") == slug:
            refs.append(key)
    if slug in (home.get("alsoToday") or {}).get("plus", []):
        refs.append("alsoToday.plus")
    if any(p.get("slug") == slug for p in home.get("pinnedSpecials", [])):
        refs.append("pinnedSpecials")
    return refs


def remove(site: Site, slug: str, force: bool = False) -> dict:
    get(site, slug)
    refs = references(site, slug)
    if refs and not force:
        raise SiteError(f"{slug} is used on the homepage ({', '.join(refs)}); "
                        "change the homepage first or pass --force")
    if refs:
        home = site.home()
        plus = home.get("alsoToday", {}).get("plus", [])
        if slug in plus:
            plus.remove(slug)
        home["pinnedSpecials"] = [p for p in home.get("pinnedSpecials", []) if p.get("slug") != slug]
        site.write_json(HOME, home)
    site.session.delete(site.post_path(slug))
    return {"removed": slug, "homepage_refs": refs}
