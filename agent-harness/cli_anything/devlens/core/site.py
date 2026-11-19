"""Locate a Devlens site checkout and read/write its JSON data files.

JSON files are written back in the same style they were read in (indent
width, trailing newline), with non-ASCII characters kept as-is, so diffs only
show real content changes.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cli_anything.devlens.core.session import Session

DHAKA = timezone(timedelta(hours=6))
DATA = "src/data"
HOME = f"{DATA}/home.json"
JOBS = f"{DATA}/jobs.json"
CATEGORIES = f"{DATA}/categories.json"
TAGS = f"{DATA}/tags.json"
POSTS_DIR = f"{DATA}/posts"
PAGES_DIR = f"{DATA}/pages"
MEDIA_DIR = "public/media"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")


class SiteError(RuntimeError):
    pass


def is_site(path: Path) -> bool:
    return (path / HOME).is_file() and (path / POSTS_DIR).is_dir()


def find_site(explicit: str | None = None) -> Path:
    """--site, then $DEVLENS_SITE, then the current directory and its parents."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not is_site(p):
            raise SiteError(f"Not a Devlens site (no {HOME}): {p}")
        return p
    env = os.environ.get("DEVLENS_SITE")
    if env:
        return find_site(env)
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if is_site(p):
            return p
    raise SiteError(
        "Could not find the Devlens site. Pass --site PATH or set DEVLENS_SITE "
        "to the folder that contains src/data/home.json."
    )


def now_dhaka() -> datetime:
    return datetime.now(DHAKA).replace(tzinfo=None, microsecond=0)


def today_dhaka() -> str:
    return now_dhaka().date().isoformat()


def check_date(value: str, what: str = "date") -> str:
    if not DATE_RE.match(value or ""):
        raise SiteError(f"{what} must be YYYY-MM-DD, got {value!r}")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as e:
        raise SiteError(f"{what} is not a real date: {value!r}") from e
    return value


def long_date(iso: str) -> str:
    """2026-11-26 -> '26 November 2026' (the format jobs.json uses)."""
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{d.day} {d.strftime('%B %Y')}"


def slugify(text: str, max_len: int = 90) -> str:
    s = text.lower().replace("&", " and ").replace("%", " percent ")
    s = re.sub(r"(?<=\d),(?=\d)", "", s)  # 1,674 -> 1674
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0]
    return s


def _detect_style(text: str) -> dict:
    m = re.search(r"\n( +)\S", text)
    return {"indent": len(m.group(1)) if m else 1, "newline": text.endswith("\n")}


class Site:
    """A Devlens site checkout, accessed through a Session."""

    def __init__(self, root: str | os.PathLike, session: Session | None = None):
        self.root = Path(root).resolve()
        if not is_site(self.root):
            raise SiteError(f"Not a Devlens site: {self.root}")
        self.session = session or Session(self.root)
        self._styles: dict[str, dict] = {}

    # ---- JSON -----------------------------------------------------------
    def read_json(self, rel: str):
        raw = self.session.read_bytes(rel)
        if raw is None:
            raise SiteError(f"Missing file: {rel}")
        text = raw.decode("utf-8")
        self._styles.setdefault(rel, _detect_style(text))
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise SiteError(f"{rel} is not valid JSON: {e}") from e

    def write_json(self, rel: str, data) -> None:
        style = self._styles.get(rel, {"indent": 1, "newline": True})
        text = json.dumps(data, ensure_ascii=False, indent=style["indent"])
        if style["newline"]:
            text += "\n"
        self.session.write_bytes(rel, text.encode("utf-8"))

    # ---- collections ----------------------------------------------------
    def post_path(self, slug: str) -> str:
        return f"{POSTS_DIR}/{slug}.json"

    def post_slugs(self) -> list[str]:
        names = {p.stem for p in (self.root / POSTS_DIR).glob("*.json")}
        for rel, data in self.session._staged.items():
            if rel.startswith(POSTS_DIR + "/") and rel.endswith(".json"):
                stem = rel[len(POSTS_DIR) + 1:-5]
                if data is None:
                    names.discard(stem)
                else:
                    names.add(stem)
        return sorted(names)

    def posts(self) -> list[dict]:
        out = [self.read_json(self.post_path(s)) for s in self.post_slugs()]
        return sorted(out, key=lambda p: p.get("date", ""), reverse=True)

    def categories(self) -> list[dict]:
        return self.read_json(CATEGORIES)

    def tags(self) -> list[dict]:
        return self.read_json(TAGS)

    def home(self) -> dict:
        return self.read_json(HOME)

    def jobs_data(self) -> dict:
        return self.read_json(JOBS)

    def page_slugs(self) -> list[str]:
        return sorted(p.stem for p in (self.root / PAGES_DIR).glob("*.json"))

    def public_file(self, src: str) -> str:
        """'/media/2026/11/x.jpg' -> 'public/media/2026/11/x.jpg'."""
        return "public/" + src.split("?")[0].lstrip("/")

    # ---- summary --------------------------------------------------------
    def info(self, today: str | None = None) -> dict:
        today = today or today_dhaka()
        posts = self.posts()
        jobs = self.jobs_data()["jobs"]
        home = self.home()
        open_jobs = [j for j in jobs if not j.get("deadline") or j["deadline"] >= today]
        return {
            "site": str(self.root),
            "today": today,
            "posts": len(posts),
            "latest_post": posts[0]["slug"] if posts else None,
            "latest_post_date": posts[0]["date"] if posts else None,
            "pages": len(self.page_slugs()),
            "categories": len(self.categories()),
            "tags": len(self.tags()),
            "jobs": len(jobs),
            "jobs_open": len(open_jobs),
            "jobs_expired": len(jobs) - len(open_jobs),
            "funding_calls": len(home.get("funding", [])),
            "funding_open": len([f for f in home.get("funding", []) if f.get("deadline", "") >= today]),
            "lead": home.get("lead", {}).get("slug"),
            "also_today": home.get("alsoToday", {}).get("slug"),
            "special": home.get("special", {}).get("slug"),
        }
