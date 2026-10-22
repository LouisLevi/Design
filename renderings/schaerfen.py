"""Ein Bild nur schärfen und vergrößern, ohne Licht, Farben oder Inhalt zu verändern.

Aufruf: python3 renderings/schaerfen.py <eingabe> <ausgabe> [breite]
Real-ESRGAN ×4 (esrgan.py), auf die Zielbreite verkleinert und zu 85 % mit einer
Lanczos-Vergrößerung gemischt, damit Laub und Flächen natürlich bleiben.
"""
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).parent))
import esrgan  # noqa: E402


def main(src_path, out_path, width=2480):
    src = cv2.imread(str(src_path))
    h = round(src.shape[0] * width / src.shape[1])
    strong = cv2.resize(esrgan.upscale_x4(src), (width, h), interpolation=cv2.INTER_AREA)
    soft = cv2.resize(src, (width, h), interpolation=cv2.INTER_LANCZOS4)
    out = cv2.addWeighted(strong, 0.85, soft, 0.15, 0)
    cv2.imwrite(str(out_path), out, [cv2.IMWRITE_JPEG_QUALITY, 94])
    print(f"{out_path}  {width}×{h}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2480)
