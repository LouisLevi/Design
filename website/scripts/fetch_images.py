#!/usr/bin/env python3
"""
Lädt alle Bilder von der bestehenden Website des Planungsbüros Günther herunter
und schreibt images/manifest.js, damit die neue Website sie automatisch verwendet.

    python3 scripts/fetch_images.py                 # Standard-URL
    python3 scripts/fetch_images.py https://...     # andere Start-URL

Nur Python-Standardbibliothek. Crawlt alle Unterseiten derselben Domain
(max. 60 Seiten), sammelt <img src/srcset/data-src>, <source srcset>,
og:image und CSS background-image und lädt jeweils die größte Variante.
"""
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

START = sys.argv[1] if len(sys.argv) > 1 else "https://www.planungsbuero-guenther.de/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
MAX_PAGES = 60
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), r.headers.get("Content-Type", ""), r.geturl()


def largest_from_srcset(srcset):
    best, best_w = None, -1
    for part in srcset.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = 0
        if len(bits) > 1:
            m = re.match(r"(\d+(?:\.\d+)?)([wx])", bits[1])
            if m:
                w = float(m.group(1)) * (1000 if m.group(2) == "x" else 1)
        if w >= best_w:
            best, best_w = bits[0], w
    return best


def upscale(url):
    """Strip common CMS resize parameters to get the original file."""
    # Wix: .../media/abc.jpg/v1/fill/w_300,h_200,.../abc.jpg -> .../media/abc.jpg
    m = re.match(r"(https?://static\.wixstatic\.com/media/[^/]+)", url)
    if m:
        return m.group(1)
    # Squarespace / generic ?format=300w, ?w=300
    p = urllib.parse.urlparse(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k.lower() not in ("w", "h", "width", "height", "format", "fit", "resize", "quality", "q")]
    url = urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(q)))
    return url


class Collector(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.links, self.images = base, set(), []

    def add_img(self, src, alt=""):
        if src and not src.startswith("data:"):
            self.images.append((urllib.parse.urljoin(self.base, src.strip()), alt or ""))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.add(urllib.parse.urljoin(self.base, a["href"]).split("#")[0])
        if tag == "img":
            src = largest_from_srcset(a["srcset"]) if a.get("srcset") else None
            src = src or a.get("data-src") or a.get("data-lazy-src") or a.get("data-original") or a.get("src")
            self.add_img(src, a.get("alt", ""))
        if tag == "source" and a.get("srcset"):
            self.add_img(largest_from_srcset(a["srcset"]))
        if tag == "meta" and a.get("property") in ("og:image", "og:image:url"):
            self.add_img(a.get("content"))
        style = a.get("style") or ""
        for m in re.finditer(r"url\((['\"]?)(.*?)\1\)", style):
            self.add_img(m.group(2))


def main():
    os.makedirs(OUT, exist_ok=True)
    host = urllib.parse.urlparse(START).netloc.replace("www.", "")
    queue, seen_pages, images = [START], set(), {}

    while queue and len(seen_pages) < MAX_PAGES:
        url = queue.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        try:
            body, ctype, final = get(url)
        except Exception as e:
            print(f"  ! {url}: {e}")
            continue
        if "html" not in ctype:
            continue
        print(f"Seite: {final}")
        c = Collector(final)
        html = body.decode("utf-8", "replace")
        c.feed(html)
        for m in re.finditer(r"background(?:-image)?\s*:\s*url\((['\"]?)(.*?)\1\)", html):
            c.add_img(m.group(2))
        page = urllib.parse.urlparse(final).path.strip("/") or "start"
        for src, alt in c.images:
            images.setdefault(src, {"alt": alt, "page": page})
            if alt and not images[src]["alt"]:
                images[src]["alt"] = alt
        for link in c.links:
            p = urllib.parse.urlparse(link)
            if p.netloc.replace("www.", "") == host and not p.path.lower().endswith(IMG_EXT + (".pdf", ".zip")):
                queue.append(link)

    manifest = []
    for src, meta in images.items():
        candidates = [upscale(src), src] if upscale(src) != src else [src]
        for cand in candidates:
            try:
                data, ctype, _ = get(cand)
            except Exception:
                continue
            if not ctype.startswith("image/") or "svg" in ctype or len(data) < 4000:
                break  # icons, tracking pixels, svg logos
            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/avif": ".avif", "image/gif": ".gif"}.get(ctype.split(";")[0], ".jpg")
            name = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(urllib.parse.urlparse(cand).path))[0].lower()).strip("-")[:40] or "bild"
            fname = f"{meta['page'].replace('/', '-')}-{name}-{hashlib.md5(cand.encode()).hexdigest()[:6]}{ext}"
            with open(os.path.join(OUT, fname), "wb") as f:
                f.write(data)
            w, h = image_size(data)
            manifest.append({"src": f"images/{fname}", "alt": meta["alt"], "page": meta["page"], "width": w, "height": h})
            print(f"  ✓ {fname} ({w}×{h})")
            break

    with open(os.path.join(OUT, "manifest.js"), "w", encoding="utf-8") as f:
        f.write("// Automatisch erzeugt von scripts/fetch_images.py\n")
        f.write("window.SITE_IMAGES = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n")
    print(f"\n{len(manifest)} Bilder gespeichert in {OUT}")


def image_size(b):
    """Read width/height from JPEG/PNG/WebP headers without Pillow."""
    try:
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
        if b[:2] == b"\xff\xd8":
            i = 2
            while i < len(b):
                if b[i] != 0xFF:
                    i += 1
                    continue
                marker = b[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
                i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
            if b[12:16] == b"VP8 ":
                return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
            if b[12:16] == b"VP8X":
                return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    except Exception:
        pass
    return 0, 0


if __name__ == "__main__":
    main()
