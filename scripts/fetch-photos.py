"""Download chosen free-licence photos listed in photo-queue.json.

Each item: {"slug" or "page", "url", "path", "alt", "credit", "creditUrl"}.
Saves a 1280x720 JPEG under public/ and sets the story's image field (with credit).
"""
import io, json, pathlib, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "DevlensBangladeshBot/1.0 (https://devlensbd.pages.dev; photo fetch)"}
W, H = 1280, 720
items = json.loads((ROOT / "photo-queue.json").read_text())
for it in items:
    out = ROOT / "public" / it["path"].lstrip("/")
    if out.exists():
        continue
    with urllib.request.urlopen(urllib.request.Request(it["url"], headers=UA), timeout=120) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    fy = it.get("focusY", 0.5)
    x = (im.width - W) // 2; y = int((im.height - H) * fy)
    im = im.crop((x, y, x + W, y + H))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    img = {"src": it["path"], "alt": it["alt"], "width": W, "height": H, "credit": it["credit"], "creditUrl": it.get("creditUrl")}
    if it.get("slug"):
        f = ROOT / "src/data/posts" / f"{it['slug']}.json"
        p = json.loads(f.read_text()); p["image"] = img
        f.write_text(json.dumps(p, ensure_ascii=False, indent=1))
    print("saved", it["path"])
