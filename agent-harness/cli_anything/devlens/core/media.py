"""Images under public/media/YYYY/MM/: add, inspect, list.

Image sizes are read from the file headers (JPEG, PNG, WebP, GIF) so no image
library is needed.
"""

from __future__ import annotations

import re
import struct
from pathlib import Path

from cli_anything.devlens.core.site import MEDIA_DIR, Site, SiteError, now_dhaka

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def image_size(data: bytes) -> tuple[str, int, int]:
    """Return (format, width, height) from image bytes, or raise SiteError."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return "png", w, h
    if data[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", data[6:10])
        return "gif", w, h
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8 ":
            w, h = struct.unpack("<HH", data[26:30])
            return "webp", w & 0x3FFF, h & 0x3FFF
        if chunk == b"VP8L":
            b = data[21:25]
            w = 1 + (((b[1] & 0x3F) << 8) | b[0])
            h = 1 + (((b[3] & 0x0F) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
            return "webp", w, h
        if chunk == b"VP8X":
            w = 1 + int.from_bytes(data[24:27], "little")
            h = 1 + int.from_bytes(data[27:30], "little")
            return "webp", w, h
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return "jpeg", w, h
            i += 2 + seg_len
        raise SiteError("JPEG has no size marker")
    if data.lstrip()[:5] in (b"<?xml", b"<svg ") or b"<svg" in data[:500]:
        m = re.search(rb'<svg[^>]*\bwidth="(\d+)[^"]*"[^>]*\bheight="(\d+)', data[:2000])
        return ("svg", int(m.group(1)), int(m.group(2))) if m else ("svg", 0, 0)
    raise SiteError("Not a supported image (JPEG, PNG, WebP, GIF or SVG)")


def safe_name(name: str) -> str:
    stem, ext = Path(name).stem, Path(name).suffix.lower()
    stem = re.sub(r"[^a-zA-Z0-9]+", "-", stem).strip("-").lower() or "image"
    return stem + (".jpg" if ext == ".jpeg" else ext)


def add(site: Site, file: str, month: str | None = None, name: str | None = None,
        overwrite: bool = False) -> dict:
    src = Path(file).expanduser()
    if not src.is_file():
        raise SiteError(f"No such file: {file}")
    data = src.read_bytes()
    fmt, w, h = image_size(data)
    month = month or now_dhaka().strftime("%Y-%m")
    if not re.match(r"^\d{4}-\d{2}$", month):
        raise SiteError(f"--month must be YYYY-MM, got {month!r}")
    fname = safe_name(name or src.name)
    if Path(fname).suffix not in EXTS:
        raise SiteError(f"Unsupported extension: {fname}")
    y, m = month.split("-")
    rel = f"{MEDIA_DIR}/{y}/{m}/{fname}"
    if site.session.exists(rel) and not overwrite:
        raise SiteError(f"{rel} already exists; pass --overwrite or --name")
    site.session.write_bytes(rel, data)
    return {"src": f"/media/{y}/{m}/{fname}", "path": rel, "format": fmt,
            "width": w, "height": h, "bytes": len(data)}


def info(site: Site, src: str) -> dict:
    rel = site.public_file(src)
    data = site.session.read_bytes(rel)
    if data is None:
        raise SiteError(f"No such image: {rel}")
    fmt, w, h = image_size(data)
    return {"src": "/" + rel[len("public/"):], "path": rel, "format": fmt,
            "width": w, "height": h, "bytes": len(data)}


def list_media(site: Site, month: str | None = None) -> list[dict]:
    base = site.root / MEDIA_DIR
    if month:
        y, m = month.split("-")
        base = base / y / m
    out = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.suffix.lower() in EXTS:
            rel = p.relative_to(site.root).as_posix()
            out.append({"src": "/" + rel[len("public/"):], "bytes": p.stat().st_size})
    return out
