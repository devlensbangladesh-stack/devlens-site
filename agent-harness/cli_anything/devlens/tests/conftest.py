import json
import struct
import zlib
from pathlib import Path

import pytest


def make_png(w: int, h: int) -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _write(path: Path, data, indent=1, newline=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=indent) + ("\n" if newline else "")
    path.write_text(text, encoding="utf-8")


def _post(slug, date, title, cats=("news",), tags=("health",), image="/media/2026/11/a.png"):
    return {"slug": slug, "date": date, "modified": date, "title": title,
            "excerpt": f"Excerpt for {title}.", "categories": list(cats), "tags": list(tags),
            "image": {"src": image, "alt": "Alt", "width": 4, "height": 3},
            "content": f"<p>{title} body · €10k</p>"}


@pytest.fixture
def mini_site(tmp_path):
    """A small synthetic Devlens site."""
    root = tmp_path / "site"
    d = root / "src" / "data"
    _write(d / "categories.json", [
        {"slug": "news", "name": "News", "description": ""},
        {"slug": "analysis", "name": "Analysis", "description": ""},
        {"slug": "devlens-special", "name": "Devlens Special", "description": ""},
    ], newline=False)
    _write(d / "tags.json", [
        {"slug": "health", "name": "Health", "description": ""},
        {"slug": "governance", "name": "Governance", "description": ""},
    ], newline=False)
    _write(d / "posts" / "alpha-story.json", _post("alpha-story", "2026-11-18T09:00:00", "Alpha story"), newline=False)
    _write(d / "posts" / "beta-story.json", _post("beta-story", "2026-11-19T08:00:00", "Beta story"), indent=2, newline=False)
    _write(d / "posts" / "gamma-special.json",
           _post("gamma-special", "2026-11-17T08:00:00", "Gamma special", cats=("devlens-special",)), newline=False)
    _write(d / "pages" / "about.json", {"slug": "about", "title": "About", "excerpt": "", "content": "<p>x</p>"})
    _write(d / "home.json", {
        "lead": {"slug": "beta-story", "label": "News", "headline": "Beta story", "summary": "S"},
        "alsoToday": {"slug": "alpha-story", "label": "News", "headline": "Alpha story", "summary": "S",
                      "plus": ["gamma-special"]},
        "special": {"slug": "gamma-special", "label": "Special report · X", "headline": "Gamma",
                    "summary": "S", "published": "2026-11-17"},
        "pills": {"fundingOpen": 2, "newReports": 1, "keyNumbers": 3},
        "numbers": [{"value": "1%", "label": "One", "source": "A, Nov 2026"}],
        "funding": [
            {"title": "Grant A", "funder": "F", "deadline": "2026-11-20", "url": "https://example.org/a"},
            {"title": "Grant B", "funder": "F", "deadline": "2026-12-05", "url": "https://example.org/b"},
        ],
        "pinnedSpecials": [],
        "spotlight": {"id": "cop31", "label": "Spotlight", "title": "COP31",
                      "today": {"date": "18 Nov", "text": "Old", "sources": []}},
    })
    _write(d / "jobs.json", {
        "sectors": [{"id": "health-nutrition", "name": "Health", "color": "#0b8f68"},
                    {"id": "education", "name": "Education", "color": "#5b3a8c"}],
        "jobs": [
            {"title": "Job one", "org": "BRAC", "badge": "BRAC", "sector": "health-nutrition",
             "url": "https://jobs.example/1", "location": "Dhaka", "nationals": False, "consultancy": False,
             "contract": "Full-time", "ref": "", "deadline": "2026-11-21", "deadlineText": "21 November 2026",
             "button": "View advert", "added": "2026-11-18"},
            {"title": "Job two", "org": "UNICEF", "badge": "UNICEF", "sector": "education",
             "url": "https://jobs.example/2", "location": "Sylhet", "nationals": True, "consultancy": False,
             "contract": "Full-time", "ref": "", "deadline": "2026-12-01", "deadlineText": "1 December 2026",
             "button": "View advert", "added": "2026-11-18"},
            {"title": "Job open", "org": "NGO", "badge": "NGO", "sector": "education",
             "url": "https://jobs.example/3", "location": "Khulna", "nationals": False, "consultancy": True,
             "contract": "Consultancy", "ref": "", "deadline": None, "deadlineText": "Open until filled",
             "button": "View advert", "added": "2026-11-18"},
        ],
    })
    (root / "public" / "media" / "2026" / "11").mkdir(parents=True)
    (root / "public" / "media" / "2026" / "11" / "a.png").write_bytes(make_png(4, 3))
    return root


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)
