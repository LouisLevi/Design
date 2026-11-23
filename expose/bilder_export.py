"""Alle Bilder des Exposés geordnet und beschriftet als Download-Paket zusammenstellen.

Aufruf: python3 expose/bilder_export.py
Ergebnis: expose/Bilder_Altenbaunaer_Strasse_26.zip
Die Bilder sind die fertig aufbereiteten Dateien (Wohnungen 1920 × 1080, Außenansichten
hochskaliert auf rund 2200 bis 2900 Pixel), unbeschnitten und ohne erneute Kompression.
"""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
RENDER = ROOT.parent / "renderings" / "fotorealistisch"
AUSSEN = ROOT.parent / "renderings" / "aussenansichten" / "hochskaliert"
NAME = "Bilder_Altenbaunaer_Strasse_26"

# Reihenfolge wie im Exposé. Außenansichten: Titel (Seite 1), dann Seite 2 oben, links, rechts
EXTERIOR = [
    ("Aussenansicht_Abend_Strasse_frontal.jpg", "Aussenansicht_Strassenseite_mit_Eingang"),
    ("Aussenansicht_Abend_Hof_schraeg.jpg", "Aussenansicht_Hof_und_Gartenseite"),
    ("Aussenansicht_Abend_Strasse_schraeg.jpg", "Aussenansicht_Strassenseite"),
    ("Aussenansicht_Abend_Gartenseite.jpg", "Aussenansicht_Gartenseite"),
]
# Wohnungen: (Nummer der Quelle in renderings/fotorealistisch/auswahl, Name im Paket)
UNITS = [
    (1, "Wohnung_Erdgeschoss"),
    (2, "Wohnung_Erdgeschoss_Richtung_Garten"),
    (4, "Wohnung_1_Obergeschoss"),
    (5, "Wohnung_2_Obergeschoss"),
    (6, "Wohnung_Untergeschoss"),
]

HINWEIS = """Altenbaunaer Straße 26, 34134 Kassel-Niederzwehren
Bilder aus dem Exposé zur Vermietung

01 bis 04   Außenansichten am Abend (Titelbild, dann die Ansichten auf Seite 2)
05 bis 14   je Wohnung Innenansicht und Luftansicht, in der Reihenfolge des Exposés

Alle Bilder sind Visualisierungen. Die Einrichtung ist beispielhaft.
Format: JPEG. Außenansichten in voller Auflösung (rund 2200 bis 2900 Pixel),
Wohnungen 1920 × 1080 Pixel.
"""


def main():
    files = [(AUSSEN / src, f"{k:02d}_{label}.jpg") for k, (src, label) in enumerate(EXTERIOR, 1)]
    k = len(files) + 1
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
