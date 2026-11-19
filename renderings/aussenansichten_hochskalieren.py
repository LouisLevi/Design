"""Fertige Außenansichten nur in der Auflösung erhöhen (×2), ohne Licht, Farbe oder Inhalt zu ändern.

Aufruf: python3 renderings/aussenansichten_hochskalieren.py
Liest renderings/aussenansichten/original/*.png und schreibt nach renderings/aussenansichten/hochskaliert/
(JPEG, Qualität 95, volle Farbauflösung). Verfahren: Real-ESRGAN x4plus (esrgan.py), auf ×2 verkleinert
und zu 70 % mit einer Lanczos-Vergrößerung gemischt, damit Putz, Rasen und Laub natürlich bleiben.
"""
import sys
from pathlib import Path

import cv2
from PIL import Image

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import esrgan  # noqa: E402

SRC = ROOT / "aussenansichten" / "original"
OUT = ROOT / "aussenansichten" / "hochskaliert"
MIX = 0.70


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in sorted(SRC.glob("*.png")):
        im = cv2.imread(str(p))
        h, w = im.shape[:2]
        strong = cv2.resize(esrgan.upscale_x4(im), (w * 2, h * 2), interpolation=cv2.INTER_AREA)
        soft = cv2.resize(im, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
        out = cv2.addWeighted(strong, MIX, soft, 1 - MIX, 0)
        dest = OUT / f"{p.stem}.jpg"
        Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).save(dest, "JPEG", quality=95, subsampling=0, optimize=True)
        print(f"{dest.relative_to(ROOT.parent)}  {w * 2}×{h * 2}", flush=True)


if __name__ == "__main__":
    main()
