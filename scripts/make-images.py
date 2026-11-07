"""Make AI illustrations for stories listed in media-queue.json.

Runs on GitHub Actions (the image service is reachable there). For each queued
item whose file does not exist yet, it fetches an AI-generated image, saves it
as a 1280x720 JPEG under public/media/, and sets the story's "image" field.
"""
import io, json, pathlib, sys, time, urllib.parse, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "media-queue.json"
W, H = 1280, 720
STYLE = ("Editorial illustration, soft natural light, muted realistic colours, Bangladesh setting. "
         "No visible faces, people only from behind or far away. No text, no letters, no signs, no logos, no watermark.")

def fetch(prompt, seed):
    q = urllib.parse.quote(f"{prompt}. {STYLE}")
    url = f"https://image.pollinations.ai/prompt/{q}?width={W}&height={H}&nologo=true&seed={seed}&model=flux"
    req = urllib.request.Request(url, headers={"User-Agent": "devlens-site-images"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()

def main():
    items = json.loads(QUEUE.read_text()) if QUEUE.exists() else []
    made, failed = 0, 0
    for it in items:
        out = ROOT / "public" / it["path"].lstrip("/")
        post = ROOT / "src/data/posts" / f"{it['slug']}.json"
        if out.exists():
            continue
        data = None
        for attempt in range(3):
            try:
                data = fetch(it["prompt"], it.get("seed", 7) + attempt)
                img = Image.open(io.BytesIO(data)).convert("RGB")
                if img.width < 600:
                    raise ValueError(f"image too small: {img.size}")
                break
            except Exception as e:
                print(f"{it['slug']}: attempt {attempt + 1} failed: {e}")
                data = None
                time.sleep(10)
        if data is None:
            failed += 1
            continue
        img = img.resize((W, H)) if img.size != (W, H) else img
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, "JPEG", quality=82, optimize=True, progressive=True)
        if post.exists():
            p = json.loads(post.read_text())
            p["image"] = {"src": it["path"], "alt": it["alt"], "width": W, "height": H}
            post.write_text(json.dumps(p, ensure_ascii=False, indent=1))
        made += 1
        print(f"made {it['path']}")
    print(f"done: {made} made, {failed} failed")

if __name__ == "__main__":
    main()
