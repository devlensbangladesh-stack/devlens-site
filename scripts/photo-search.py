"""Search Wikimedia Commons and Openverse for freely licensed photos.

Input: PHOTO_QUERIES env var, JSON {"key": "search words", ...}.
Output: candidates/<key>.json (metadata) and candidates/<key>.jpg (numbered contact sheet).
Only public domain, CC0, CC BY and CC BY-SA files are kept.
"""
import io, json, os, pathlib, re, urllib.parse, urllib.request
from PIL import Image, ImageDraw

UA = {"User-Agent": "DevlensBangladeshBot/1.0 (https://devlensbd.pages.dev; photo search)"}
OK = re.compile(r"^(public domain|pd|cc0|cc[ -]by( |-)?(sa)?( |-)?[0-9.]*)", re.I)
out = pathlib.Path("candidates"); out.mkdir(exist_ok=True)

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()

def strip(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()

def commons(q):
    u = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6"
         f"&gsrlimit=20&gsrsearch={urllib.parse.quote(q + ' filetype:bitmap')}"
         "&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1600")
    pages = json.loads(get(u)).get("query", {}).get("pages", {})
    res = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lic = strip(m.get("LicenseShortName", {}).get("value"))
        if not OK.match(lic) or ii.get("width", 0) < 1000:
            continue
        res.append({"source": "Wikimedia Commons", "title": p["title"], "page": ii.get("descriptionurl"),
                    "url": ii.get("thumburl") or ii.get("url"), "license": lic,
                    "author": strip(m.get("Artist", {}).get("value"))[:80] or "Unknown",
                    "desc": strip(m.get("ImageDescription", {}).get("value"))[:200]})
    return res

def openverse(q):
    u = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&license=by,by-sa,cc0,pdm&page_size=20&size=large"
    res = []
    for r in json.loads(get(u)).get("results", []):
        lic = ("CC " + r["license"].upper() + " " + (r.get("license_version") or "")).strip()
        if r["license"] in ("cc0", "pdm"): lic = "Public domain" if r["license"] == "pdm" else "CC0"
        res.append({"source": r.get("source", "Openverse").title(), "title": r.get("title"), "page": r.get("foreign_landing_url"),
                    "url": r.get("url"), "license": lic, "author": (r.get("creator") or "Unknown")[:80], "desc": (r.get("title") or "")[:200]})
    return res

for key, q in json.loads(os.environ["PHOTO_QUERIES"]).items():
    found = []
    for fn in (commons, openverse):
        try: found += fn(q)
        except Exception as e: print(key, fn.__name__, "failed:", e)
    found = found[:16]
    thumbs = []
    for c in found:
        try:
            im = Image.open(io.BytesIO(get(c["url"]))).convert("RGB"); im.thumbnail((400, 260)); thumbs.append(im)
        except Exception as e:
            thumbs.append(Image.new("RGB", (400, 260), "grey")); c["error"] = str(e)
    sheet = Image.new("RGB", (4 * 410, max(1, (len(thumbs) + 3) // 4) * 290), "white")
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(thumbs):
        x, y = (i % 4) * 410, (i // 4) * 290
        sheet.paste(im, (x + 5, y + 5)); d.rectangle([x + 5, y + 5, x + 45, y + 35], fill="black"); d.text((x + 12, y + 12), str(i), fill="white")
    sheet.save(out / f"{key}.jpg", quality=80)
    (out / f"{key}.json").write_text(json.dumps(found, indent=1, ensure_ascii=False))
    print(key, len(found), "candidates")
