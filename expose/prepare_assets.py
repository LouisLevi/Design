"""Bilder und Grundrisse für das Exposé vorbereiten.

Aufruf: python3 expose/prepare_assets.py <alte-mappe.pdf>

- Titelbild (Außenansicht) aus der alten Mappe extrahieren
- Grundrisse ohne Text als hochaufgelöstes PNG (600 dpi bei 1:100) exportieren,
  Positionen der Raumnamen als JSON. Raster statt SVG, weil Chromium die Clip-Pfade der
  SVG so ins PDF schreibt, dass manche Viewer Hilfslinien als Rahmen zeigen.
- Innenansichten auf 3:2 beschneiden, Luftansichten auf Inhalt zuschneiden
"""
import json
import sys
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
RENDER = ROOT.parent / "renderings" / "fotorealistisch" / "auswahl"

PT_PER_M = 40.5  # aus dem Maßstabsbalken der Pläne (0–4 m = 162 pt)
TARGET_DPI = 600  # bei Druck im Maßstab 1:100 (10 mm je Meter)
LABEL_SHIFT = {("w3-eg", "Gäste-Bad"): (2.2, 3.0)}  # Label aus der Dusche schieben (in %)
BAR_Y = 520      # darunter liegt nur der Maßstabsbalken

# Seite der alten Mappe → (Datei, {Beschriftung im Plan: (Raumname, Fläche)}, Zusatzlabels)
PLANS = {
    6: ("w1", {"Wohnen-Kochen-Essen": ("Wohnen · Kochen · Essen", "29,70"), "Schlafen": ("Schlafen", "12,67"),
               "Bad": ("Bad", "4,71"), "Abstl.": ("Abstl.", "2,60")}, []),
    8: ("w2", {"Wohnen-Kochen-Essen": ("Wohnen · Kochen · Essen", "43,19"), "Schlafen": ("Schlafen", "13,52"),
               "Bad": ("Bad", "4,15"), "Abstl.": ("Abstl.", "1,49"), "Terrasse": ("Terrasse", "6,13")}, []),
    11: ("w3-eg", {"Wohnen-Kochen-Essen": ("Wohnen · Kochen · Essen", "97,57"), "Bad": ("Gäste-Bad", "3,58"),
                   "Abstl.": ("Abstl.", "2,05"), "Balkon": ("Balkon", "7,22")}, []),
    12: ("w3-og", {"Schlafen": ("Schlafen", "15,50"), "Ankleide": ("Ankleide", "21,88"), "Büro": ("Büro", "11,62"),
                   "Bad": ("Bad", "7,07"), "Terrasse": ("Terrasse", "7,29")}, []),
    14: ("w4", {"Wohnen-Kochen-Essen": ("Wohnen · Kochen · Essen", "33,33"), "Schlafen": ("Schlafen", "12,20"),
                "Bad": ("Bad", "3,47")}, []),
    16: ("w5", {"Wohnen-Kochen-Essen": ("Wohnen · Kochen · Essen", "26,48"), "Schlafen": ("Schlafen", "6,35"),
                "Bad": ("Bad", "3,90"), "Abstl.": ("Flur / Abstl.", "3,80")},
         [("Terrasse", "4,17", (536, 436))]),
    18: ("w6", {"Wohnen-Essen": ("Wohnen · Essen · Schlafen", "20,76"), "Küche": ("Küche / Flur", "6,11"),
                "Bad": ("Bad", "3,78"), "Ankleide": ("Ankleide", "2,59")}, []),
}


def plan_bounds(page):
    xs, ys = [], []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "re":
                pts = [it[1].tl, it[1].br]
            elif it[0] == "qu":
                pts = list(it[1])
            else:
                pts = [q for q in it[1:] if isinstance(q, pymupdf.Point)]
            for q in pts:
                if q.y < BAR_Y:
                    xs.append(q.x)
                    ys.append(q.y)
    return pymupdf.Rect(min(xs), min(ys), max(xs), max(ys))


def export_plans(pdf_path):
    out = {}
    (ASSETS / "plans").mkdir(parents=True, exist_ok=True)
    for pno, (name, labels, extra) in PLANS.items():
        doc = pymupdf.open(pdf_path)
        page = doc[pno - 1]
        spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
        found, entry = [], None
        for s in spans:
            t = s["text"].strip()
            c = pymupdf.Rect(s["bbox"])
            if s["size"] > 9 and t in labels:
                found.append((labels[t], ((c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2)))
            if t.startswith("WE ") and s["size"] > 6:
                entry = ((c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2)
        missing = set(labels) - {t for t in labels if any(lab == labels[t] for lab, _ in found)}
        assert not missing, (pno, missing)
        for lab_name, area, pos in extra:
            found.append(((lab_name, area), pos))

        # sämtlichen Text entfernen, Linien und Flächen behalten
        for s in spans:
            page.add_redact_annot(pymupdf.Rect(s["bbox"]))
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=pymupdf.PDF_REDACT_TEXT_REMOVE)
        box = plan_bounds(page) + (-4, -4, 4, 4)
        zoom = TARGET_DPI * (10 / 25.4 * 72 / PT_PER_M) / 72  # Seitenpunkte → Pixel bei 1:100
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=box, colorspace=pymupdf.csGRAY, alpha=False)
        pix.save(ASSETS / "plans" / f"{name}.png")

        def rel(p):
            return [round((p[0] - box.x0) / box.width * 100, 2), round((p[1] - box.y0) / box.height * 100, 2)]

        out[name] = {
            "width_m": round(box.width / PT_PER_M, 3),
            "height_m": round(box.height / PT_PER_M, 3),
            "labels": [{"name": n, "area": a,
                        "pos": [v + d for v, d in zip(rel(p), LABEL_SHIFT.get((name, n), (0, 0)))]}
                       for (n, a), p in found],
            "entry": rel(entry) if entry else None,
        }
        print(f"Plan {name}: {box.width / PT_PER_M:.2f} × {box.height / PT_PER_M:.2f} m, {len(found)} Labels")
    (ASSETS / "plans" / "plans.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


def export_cover(pdf_path):
    doc = pymupdf.open(pdf_path)
    xref = doc[0].get_images(full=True)[0][0]
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.save(ASSETS / "img" / "haus.jpg", quality=92)
    # Ausschnitt für Seite 4: obere Geschosse mit Dachterrasse
    w, h = im.size
    im.crop((round(w * 0.30), round(h * 0.06), round(w * 0.93), round(h * 0.06) + round(w * 0.63 * 95 / 210))).save(
        ASSETS / "img" / "haus-detail.jpg", quality=92)
    print(f"Titelbild {pix.width}×{pix.height}")


def prepare_renderings():
    for n in range(1, 7):
        im = Image.open(RENDER / f"Wohnung {n} Innenansicht.jpg")
        w, h = im.size
        cw = round(h * 3 / 2)
        x = (w - cw) // 2
        im.crop((x, 0, x + cw, h)).save(ASSETS / "img" / f"w{n}-innen.jpg", quality=93, subsampling=0)

        lu = Image.open(RENDER / f"Wohnung {n} Luftansicht.jpg").convert("RGB")
        gray = lu.convert("L").point(lambda v: 255 if v < 246 else 0)
        l, t, r, b = gray.getbbox()
        pad = 12
        lu.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, lu.width), min(b + pad, lu.height))).save(
            ASSETS / "img" / f"w{n}-luft.jpg", quality=93, subsampling=0)
    print("Renderings vorbereitet")


if __name__ == "__main__":
    pdf = sys.argv[1]
    (ASSETS / "img").mkdir(parents=True, exist_ok=True)
    export_cover(pdf)
    export_plans(pdf)
    prepare_renderings()
