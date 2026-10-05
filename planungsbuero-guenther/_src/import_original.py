#!/usr/bin/env python3
"""Übernimmt Projektdaten und Projektbilder 1:1 von planungsbuero-guenther.de (Wix).

Eingabe: pairs.json – je Bauaufgabe die Projekte in Original-Reihenfolge mit Titel,
Detailtext („Bauort: … Fertigstellung: …“) und den Wix-Medien-IDs der zugehörigen Galerie
(ausgelesen aus der gerenderten Original-Seite: Galerie und Text stehen in derselben Zeile).

Ausgabe: _src/projekte.json und assets/img/p/<slug>-<n>.webp (+ -s.webp Vorschau).
Aufruf: python3 _src/import_original.py pairs.json
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets/img/p")
CACHE = os.environ.get("WIX_CACHE", "/tmp/wix-originale")

CAT_BY_PAGE = {"aktuelle-projekte": "aktuell", "einfamilienhäuser": "efh", "mehrfamilienhäuser": "mfh",
               "gewerbe-sonstige-bauwerke": "gewerbe", "projektentwicklungen": "entwicklung"}

# Eindeutige Tippfehler der Original-Seite (Inhalt unverändert)
TITLE_FIX = {
    "Neubau eines Einfamlienhauses mit Carport": "Neubau eines Einfamilienhauses mit Carport",
    "Neubau eines Wohnhaus mit 25 WE": "Neubau eines Wohnhauses mit 25 WE",
    "Neubau des Deutschen Luft und Raumfahrtzentrums - DLR": "Neubau des Deutschen Luft- und Raumfahrtzentrums (DLR)",
}

# Filme der Seite „Videos“ → Projekt (Titel wie auf der Original-Seite)
FILMS = {
    "Wohnanlage Söhrewald mit 27 WE, Kindertagesstätte und einer Tagespflege": "film-soehrewald",
    "Neubau eines Wohnhauses mit 25 WE": "film-kassel-25we",
    "Teilsanierung eines Hochhauses": "film-hochhaus-kassel",
    "Bau eines Pultdachhauses in Holzständerbauweise": "film-pultdachhaus",
    "Bau eines Satteldachhauses in Holzständerbauweise": "film-satteldachhaus",
    "Ehemaliges Fabrikgelände": "film-salamander-areal",
    "Neubau eines Wohn- u. Geschäftshauses mit Kindertagesstätte": "film-kita-kassel",
}


def clean(s):
    s = s.replace(" ", " ").replace("​", "")
    return re.sub(r"\s+", " ", s).strip()


def slugify(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70].rstrip("-")


def lph(v):
    v = clean(v)
    if not v:
        return None
    v = re.sub(r"\s*-\s*", "–", v) if re.fullmatch(r"(LPH\s*)?[\d\s\-]+", v) else v
    if re.fullmatch(r"[\d–]+", v):
        v = "LPH " + v
    v = re.sub(r"LPH\s*(\d)", r"LPH \1", v)
    v = re.sub(r"(\d)\s*-\s*(\d)", r"\1–\2", v)
    v = v.replace("Design - Planung - Ausführung", "Design · Planung · Ausführung")
    return v


def parse_details(t):
    t = clean(t)
    keys = ["Bauort", "Geplante Fertigstellung", "Fertigstellung", "Erstellungsjahr", "Leistungen", "Bauvolumen", "Grundstücksgröße"]
    pat = re.compile(r"(" + "|".join(re.escape(k) for k in keys) + r"):")
    parts = pat.split(t)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        k, v = parts[i], parts[i + 1].strip()
        if k == "Fertigstellung" and parts[i - 1].endswith("Geplante "):
            continue
        out[k] = v
    return out


def year_status(d):
    for k in ("Geplante Fertigstellung", "Fertigstellung", "Erstellungsjahr"):
        if k in d:
            v = d[k]
            m = re.search(r"(\d{4})", v)
            geplant = k == "Geplante Fertigstellung" or "geplant" in v.lower()
            if not m:
                return None, ("geplant" if geplant else None), k
            return int(m.group(1)), ("geplant" if geplant else "fertig"), k
    return None, None, None


def volume(v):
    if not v:
        return None, False
    ca = "ca." in v
    digits = re.sub(r"[^\d]", "", v)
    return (int(digits) if digits else None), ca


def area(v):
    if not v:
        return None
    m = re.search(r"([\d.]+)\s*qm", v)
    if not m:
        return None
    n = int(m.group(1).replace(".", ""))
    return f"{n:,} m²".replace(",", ".")


def fetch(mid):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, mid)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        subprocess.run(["curl", "-sSfL", "-o", path, f"https://static.wixstatic.com/media/{mid}"], check=True)
    return path


def convert(src, dst, size, q):
    subprocess.run(["convert", src, "-auto-orient", "-strip", "-resize", size, "-quality", str(q), dst], check=True)
    w, h = subprocess.run(["identify", "-format", "%w %h", dst], capture_output=True, text=True, check=True).stdout.split()
    return int(w), int(h)


def main(pairs_file):
    pairs = json.load(open(pairs_file, encoding="utf-8"))
    projects, slugs, n = [], set(), 0
    for page, cat in CAT_BY_PAGE.items():
        for item in pairs[page]:
            n += 1
            title = clean(item["title"])
            title = TITLE_FIX.get(title, title)
            d = parse_details(item["details"])
            ort = clean(d.get("Bauort", ""))
            year, status, ykey = year_status(d)
            slug = base = slugify(f"{title} {ort}")
            k = 2
            while slug in slugs:
                slug = f"{base}-{k}"; k += 1
            slugs.add(slug)
            p = {"id": f"PG-{n:03d}", "slug": slug, "cat": cat, "title": title, "ort": ort}
            if year:
                p["jahr"] = year
            if status:
                p["status"] = status
            if d.get("Leistungen") and lph(d["Leistungen"]):
                p["lph"] = lph(d["Leistungen"])
            vol, ca = volume(d.get("Bauvolumen"))
            if vol:
                p["volumen"] = vol
                if ca:
                    p["volumen_ca"] = True
            if cat == "entwicklung" and area(d.get("Grundstücksgröße")):
                p["grundstueck"] = area(d["Grundstücksgröße"])
            imgs = []
            for i, mid in enumerate(item["imgs"], 1):
                src = fetch(mid)
                name = f"{slug}-{i}"
                w, h = convert(src, os.path.join(IMG, name + ".webp"), "1600x1600>", 82)
                convert(src, os.path.join(IMG, name + "-s.webp"), "760x>", 80)
                imgs.append([name, w, h])
            p["img"] = imgs
            p["quelle"] = item["imgs"]  # Wix-Medien-IDs zur Nachverfolgung
            if title in FILMS:
                p["film"] = FILMS[title]
            projects.append(p)
            print(p["id"], cat, title, "|", ort, "|", len(imgs), "Bilder")
    json.dump(projects, open(os.path.join(ROOT, "_src/projekte.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(projects), "Projekte geschrieben.")


if __name__ == "__main__":
    main(sys.argv[1])
