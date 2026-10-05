"""Fertige Renderings auf 1080p bringen und das Licht vereinheitlichen.

Aufruf: python3 renderings/aufbereiten.py
Liest renderings/auswahl/*.jpg und schreibt nach renderings/fotorealistisch/auswahl/
(1920×1080, JPEG, Qualität 95).

Schritte:
- Weißabgleich an den hellen, fast neutralen Flächen (Wände, Decke) auf ein minimal
  warmes Tageslicht-Weiß; bei Luftansichten bleibt der weiße Hintergrund unverändert.
- Innenansichten: Mitteltöne auf eine einheitliche Helligkeit anheben, Lichter (Fenster)
  laufen weich aus statt auszubrennen.
- Alle: dezente Mikrokontraste, etwas Lebendigkeit, Hochskalieren mit FSRCNN (×2,
  OpenCV dnn_superres), auf 1920×1080 verkleinern, leicht nachschärfen.
- Weiche Quellbilder (STRONG_SR): zusätzlich Real-ESRGAN ×4 (esrgan.py), 85 % gemischt.
- Luftansichten: Hintergrund auf sauberes Reinweiß (ohne JPEG-Rauschen).

Braucht: pip install opencv-contrib-python-headless numpy pillow
"""
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
SRC = ROOT / "auswahl"
OUT = ROOT / "fotorealistisch" / "auswahl"
MODEL = Path.home() / ".cache" / "sr" / "FSRCNN_x2.pb"
MODEL_URL = "https://raw.githubusercontent.com/Saafke/FSRCNN_Tensorflow/master/models/FSRCNN_x2.pb"

SIZE = (1920, 1080)
# Quellbilder, die deutlich weicher sind als der Rest der Serie: zusätzlich mit Real-ESRGAN
# hochrechnen (esrgan.py, braucht torch) und mit der FSRCNN-Fassung mischen, damit Stoffe
# und Teppiche ihre natürliche Struktur behalten.
STRONG_SR = {"wohnung 2 innenansicht", "wohnung 4 innenansicht"}
STRONG_SR_MIX = 0.85  # Anteil Real-ESRGAN
WHITE = np.array([0.98, 1.0, 1.015])  # Ziel-Weiß in B, G, R: Tageslicht, minimal warm
WB_STRENGTH = 0.9                     # Anteil der Farbstich-Korrektur
MEDIAN_L = {"innen": 0.57, "luft": None}


def srgb_to_linear(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def soft_clip(x, knee=0.9):
    """Lichter oberhalb von knee weich auslaufen lassen statt hart abzuschneiden."""
    over = np.maximum(x - knee, 0)
    return np.where(x > knee, knee + (1 - knee) * np.tanh(over / (1 - knee)), x)


def white_balance(img, keep_white=False):
    """img: BGR float 0..1. Farbstich der hellen, fast neutralen Flächen korrigieren.

    keep_white: reinweißen Hintergrund (Luftansichten) unverändert lassen.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    mask = (L > 55) & (L < 92) & (np.hypot(a, b) < 16)
    lin = srgb_to_linear(img)
    # Farbverhältnis je Pixel mitteln, damit helle Flächen (Decke, Fenster) nicht dominieren
    px = lin[mask]
    mean = (px / px.mean(axis=1, keepdims=True)).mean(axis=0)
    gain = (WHITE / WHITE.mean() / mean) ** WB_STRENGTH
    out = soft_clip(linear_to_srgb(lin * gain))
    if keep_white:
        w = np.clip((L[..., None] / 100 - 0.95) / 0.04, 0, 1)
        out = w * img + (1 - w) * out
    return out.astype(np.float32)


def tone(img, median_target):
    """Mitteltöne per Gamma auf eine Ziel-Helligkeit; Schwarz und Weiß bleiben fix."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L = lab[..., 0] / 100
    if median_target:
        g = np.log(median_target) / np.log(np.median(L))
        g = float(np.clip(g, 0.72, 1.0))
    else:
        g = 0.94
    L = L ** g
    # dezente Mikrokontraste (Clarity) – großer Radius, kleine Stärke
    blur = cv2.GaussianBlur(L, (0, 0), 18)
    L = L + 0.12 * np.clip((0.97 - L) / 0.15, 0, 1) * (L - blur)  # nicht in den Lichtern
    lab[..., 0] = np.clip(L, 0, 1) * 100
    # Lebendigkeit: schwach gesättigte Farben etwas mehr anheben als kräftige
    chroma = np.hypot(lab[..., 1], lab[..., 2])
    boost = 1 + 0.10 * np.clip(1 - chroma / 40, 0, 1)
    lab[..., 1] *= boost
    lab[..., 2] *= boost
    return np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2BGR), 0, 1)


def upscale(img8):
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(str(MODEL))
    sr.setModel("fsrcnn", 2)
    return fit(sr.upsample(img8))


def fit(big):
    """Auf Breite 1920 verkleinern, dann mittig auf 1080 Höhe zuschneiden."""
    h = round(big.shape[0] * SIZE[0] / big.shape[1])
    small = cv2.resize(big, (SIZE[0], h), interpolation=cv2.INTER_AREA)
    top = (h - SIZE[1]) // 2
    return small[top:top + SIZE[1]]


def sharpen(img8):
    f = img8.astype(np.float32)
    blur = cv2.GaussianBlur(f, (0, 0), 0.9)
    return np.clip(f + 0.35 * (f - blur), 0, 255).astype(np.uint8)


def clean_background(img8, threshold=240):
    """Fast weißen, mit dem Bildrand verbundenen Hintergrund auf Reinweiß setzen.

    Entfernt JPEG-Rauschen und schwache Reste im Hintergrund der Luftansichten;
    Modell und Schattenwurf sind dunkler als threshold und bleiben unverändert.
    """
    near_white = (img8.min(axis=2) > threshold).astype(np.uint8)
    n, labels = cv2.connectedComponents(near_white, connectivity=4)
    border = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    bg = np.isin(labels, border[border > 0]).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 1.2)[..., None]  # weicher Übergang am Modellrand
    return np.clip(img8 * (1 - bg) + 255 * bg, 0, 255).astype(np.uint8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SRC.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    for p in files:
        kind = "luft" if "luft" in p.name.lower() else "innen"
        img = cv2.imread(str(p)).astype(np.float32) / 255
        img = white_balance(img, keep_white=kind == "luft")
        img = tone(img, MEDIAN_L[kind])
        img8 = (img * 255 + 0.5).astype(np.uint8)
        base = sharpen(upscale(img8))
        if p.stem.lower() in STRONG_SR:
            import esrgan  # erst hier laden: torch wird nur für diese Bilder gebraucht
            strong = fit(esrgan.upscale_x4(img8))
            base = cv2.addWeighted(strong, STRONG_SR_MIX, base, 1 - STRONG_SR_MIX, 0)
        img8 = base
        if kind == "luft":
            img8 = clean_background(img8)
        # einheitliche Dateinamen: "Wohnung 6 innenansicht" → "Wohnung 6 Innenansicht"
        name = " ".join(w[:1].upper() + w[1:] for w in p.stem.split()) + ".jpg"
        Image.fromarray(cv2.cvtColor(img8, cv2.COLOR_BGR2RGB)).save(
            OUT / name, "JPEG", quality=95, subsampling=0, optimize=True, progressive=True
        )
        print(f"{OUT.relative_to(ROOT.parent) / name}  {img8.shape[1]}×{img8.shape[0]}")


if __name__ == "__main__":
    main()
