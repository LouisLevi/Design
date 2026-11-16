"""Alle Bilder des Exposés geordnet und beschriftet als Download-Paket zusammenstellen.

Aufruf: python3 expose/bilder_export.py
Ergebnis: expose/Bilder_Altenbaunaer_Strasse_26.zip
Die Bilder sind die fertig aufbereiteten Dateien (1920 × 1080, Außenansicht 2480 × 1860),
unbeschnitten und ohne erneute Kompression.
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
RENDER = ROOT.parent / "renderings" / "fotorealistisch"
NAME = "Bilder_Altenbaunaer_Strasse_26"

# Reihenfolge wie im Exposé: (Quelle in renderings/fotorealistisch/auswahl, Name im Paket)
UNITS = [
    (1, "Wohnung_Erdgeschoss"),
    (2, "Wohnung_Erdgeschoss_Richtung_Garten"),
    (4, "Wohnung_1_Obergeschoss"),
    (5, "Wohnung_2_Obergeschoss"),
    (6, "Wohnung_Untergeschoss"),
]

HINWEIS = """Altenbaunaer Straße 26, 34134 Kassel-Niederzwehren
Bilder aus dem Exposé zur Vermietung

00          Außenansicht
01 bis 10   je Wohnung Innenansicht und Luftansicht, in der Reihenfolge des Exposés

Alle Bilder sind Visualisierungen. Die Einrichtung ist beispielhaft.
Format: JPEG, 1920 × 1080 Pixel (Außenansicht 2480 × 1860 Pixel).
"""


def main():
    files = [(RENDER / "Aussenansicht Umgebung.jpg", "00_Aussenansicht.jpg")]
    k = 1
    for n, label in UNITS:
        for view in ("Innenansicht", "Luftansicht"):
            files.append((RENDER / "auswahl" / f"Wohnung {n} {view}.jpg", f"{k:02d}_{label}_{view}.jpg"))
            k += 1

    zip_path = ROOT / f"{NAME}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr(f"{NAME}/Hinweis.txt", HINWEIS)
        for src, name in files:
            z.write(src, f"{NAME}/{name}")
            print(f"{name:55s} ← {src.relative_to(ROOT.parent)}")
    print(zip_path, f"{zip_path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
