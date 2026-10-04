#!/usr/bin/env python3
"""Bilder mit FLUX über Cloudflare Workers AI erzeugen (kostenloses Tageskontingent).

Ersatz für Nano Banana, solange für die Gemini-API keine Zahlungsart hinterlegt ist.
Braucht nur Python 3 (keine Pakete) und zwei Umgebungsvariablen:

    CLOUDFLARE_ACCOUNT_ID   Account-ID (Cloudflare-Dashboard → Workers AI → „REST API“)
    CLOUDFLARE_API_TOKEN    API-Token mit der Berechtigung „Workers AI“

Beispiele:

    python3 tools/bild.py "Einfamilienhaus, weißer Putz, Flachdach, Abendlicht" -o haus.jpg
    python3 tools/bild.py "…" -o hero.webp --breite 1600 --hoehe 900 --modell klein-9b --seed 7
"""

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

MODELLE = {
    # Name: (Modell-ID, Eingabe als multipart?)
    "klein-4b": ("@cf/black-forest-labs/flux-2-klein-4b", True),
    "klein-9b": ("@cf/black-forest-labs/flux-2-klein-9b", True),
    "dev": ("@cf/black-forest-labs/flux-2-dev", True),
    "schnell": ("@cf/black-forest-labs/flux-1-schnell", False),  # nur 1024 × 1024
}


def multipart(felder):
    grenze = uuid.uuid4().hex
    teile = []
    for name, wert in felder.items():
        teile.append(
            f'--{grenze}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{wert}\r\n'
        )
    teile.append(f"--{grenze}--\r\n")
    return "".join(teile).encode(), f"multipart/form-data; boundary={grenze}"


def anfrage(args, konto, token):
    modell_id, ist_multipart = MODELLE[args.modell]
    if ist_multipart:
        felder = {
            "prompt": args.prompt,
            # Breite und Höhe: 256–1920 px, auf ein Vielfaches von 16 gerundet
            "width": max(256, min(1920, round(args.breite / 16) * 16)),
            "height": max(256, min(1920, round(args.hoehe / 16) * 16)),
        }
        if args.seed is not None:
            felder["seed"] = args.seed
        daten, typ = multipart(felder)
    else:
        felder = {"prompt": args.prompt, "steps": 8}
        if args.seed is not None:
            felder["seed"] = args.seed
        daten, typ = json.dumps(felder).encode(), "application/json"

    url = f"https://api.cloudflare.com/client/v4/accounts/{konto}/ai/run/{modell_id}"
    req = urllib.request.Request(
        url,
        data=daten,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": typ},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as antwort:
            inhalt = json.load(antwort)
    except urllib.error.HTTPError as fehler:
        text = fehler.read().decode(errors="replace")
        sys.exit(f"Cloudflare antwortet mit HTTP {fehler.code}: {text[:600]}")

    bild = (inhalt.get("result") or {}).get("image")
    if not inhalt.get("success", True) or not bild:
        sys.exit(f"Kein Bild erhalten: {json.dumps(inhalt)[:600]}")
    return base64.b64decode(bild)


def endung(daten):
    if daten.startswith(b"\x89PNG"):
        return ".png"
    if daten[:4] == b"RIFF" and daten[8:12] == b"WEBP":
        return ".webp"
    return ".jpg"


def speichern(daten, ziel):
    ziel.parent.mkdir(parents=True, exist_ok=True)
    quelle_endung = endung(daten)
    ziel_endung = ziel.suffix.lower().replace(".jpeg", ".jpg")
    if ziel_endung == quelle_endung:
        ziel.write_bytes(daten)
        return ziel

    # Anderes Format gewünscht (z. B. .webp für die Website): mit Pillow oder ImageMagick umwandeln
    roh = ziel.with_name(ziel.stem + ".roh" + quelle_endung)
    roh.write_bytes(daten)
    try:
        from PIL import Image

        Image.open(roh).save(ziel, quality=86)
    except ImportError:
        werkzeug = shutil.which("magick") or shutil.which("convert")
        if not werkzeug:
            ziel = ziel.with_suffix(quelle_endung)
            roh.rename(ziel)
            print(f"Hinweis: kein Pillow/ImageMagick gefunden, gespeichert als {quelle_endung}")
            return ziel
        subprocess.run([werkzeug, str(roh), "-quality", "86", str(ziel)], check=True)
    roh.unlink()
    return ziel


def main():
    p = argparse.ArgumentParser(description="Bild mit FLUX (Cloudflare Workers AI) erzeugen")
    p.add_argument("prompt", help="Bildbeschreibung (Englisch liefert meist bessere Ergebnisse)")
    p.add_argument("-o", "--ausgabe", required=True, help="Zieldatei (.jpg, .png oder .webp)")
    p.add_argument("--modell", choices=MODELLE, default="klein-4b")
    p.add_argument("--breite", type=int, default=1600)
    p.add_argument("--hoehe", type=int, default=900)
    p.add_argument("--seed", type=int, help="gleicher Seed + gleicher Prompt = gleiches Bild")
    args = p.parse_args()

    konto = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not konto or not token:
        sys.exit("CLOUDFLARE_ACCOUNT_ID und CLOUDFLARE_API_TOKEN sind nicht gesetzt (siehe README).")

    ziel = speichern(anfrage(args, konto, token), Path(args.ausgabe))
    print(ziel)


if __name__ == "__main__":
    main()
