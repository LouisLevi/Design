"""Zweiten Küchenschenkel (L-Form) in die Luftansicht Wohnung Erdgeschoss einzeichnen, passend zur Innenansicht.

Bereits angewendet: renderings/auswahl/Wohnung 1 Luftansicht.JPG enthält das Ergebnis (Original in der Git-Historie).
Aufruf: python3 renderings/kueche_eck_erdgeschoss.py <original.jpg> <ergebnis.jpg>  (Quelle 1362×768)
"""
import sys, cv2, numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
im = cv2.imread(SRC).astype(np.float32)
H_, W_ = im.shape[:2]
S = 1920 / W_                       # Faktor Quelle → aufbereitetes Bild (dort gemessen)
def P(x, y): return np.array([x / S, (y + 1) / S])
# Achsen pro cm im aufbereiteten Bild: u entlang Fensterwand (nach links), v zur Raummitte, z nach unten
u = np.array([-0.797, 0.180]) / S; v = np.array([0.247, 0.586]) / S; z = np.array([0.0, 0.53]) / S
C0 = P(875.0, 284.0)
L, D, H = 90, 60, 90
b0, b1 = C0, C0 + L * u
f0, f1 = C0 + D * v, C0 + L * u + D * v
def poly(*pts, k=8):
    m = np.zeros((H_ * k, W_ * k), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts) * k * 16).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=4)
    return cv2.resize(m, (W_, H_), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255

def sample(pts):
    m = poly(*pts)[..., 0] > 0.99
    return np.median(im[m], axis=0)
top_col = sample([P(877, 304), P(884, 303), P(885, 316), P(878, 317)])          # Arbeitsplatte lange Zeile (links der Spüle)
side_col = sample([P(878, 300), P(884, 299), P(886, 330), P(880, 331)])        # Seitenfläche (nach links)
wall_col = sample([P(720, 340), P(790, 324), P(792, 340), P(722, 356)])        # Wand (zum Raum gewandt)
front_col = wall_col * 0.95
print("Farben Platte/Seite/Wand:", top_col.round(), side_col.round(), wall_col.round())

out = im.copy()
def paint(mask, col, mult=None):
    global out
    if mult is not None:
        out = out * (1 - mask * (1 - mult))
    else:
        out = out * (1 - mask) + col * mask

# Kontaktschatten auf dem Boden vor dem Sockel und unter der Stirnseite
shadow = poly(f1 + H * z, f0 + H * z, f0 + H * z + 10 * v, f1 + H * z + 10 * v - 6 * u)
shadow = np.maximum(shadow, poly(b1 + H * z, f1 + H * z, f1 + H * z - 8 * u, b1 + H * z - 8 * u))
shadow = cv2.GaussianBlur(shadow, (0, 0), 3.0 / S * 1.4)[..., None] if shadow.ndim == 2 else cv2.GaussianBlur(shadow[..., 0], (0, 0), 2.5)[..., None]
paint(shadow, None, mult=0.80)

# Stirnseite (links, wie die beleuchtete Seitenfläche der langen Zeile)
paint(poly(b1, f1, f1 + H * z, b1 + H * z), side_col)
# Front (zum Raum)
front = poly(f1, f0, f0 + H * z, f1 + H * z)
paint(front, front_col)
# Sockel (10 cm, zurückgesetzt, dunkler)
paint(poly(f1 + 80 * z, f0 + 80 * z, f0 + H * z, f1 + H * z), None, mult=0.72)
# Plattenkante (4 cm) etwas heller als die Front
paint(poly(f1, f0, f0 + 4 * z, f1 + 4 * z), top_col * 0.96)
# Schattenfuge unter der Platte
paint(poly(f1 + 4 * z, f0 + 4 * z, f0 + 5.2 * z, f1 + 5.2 * z), None, mult=0.80)
# Türfuge in der Mitte und Schublade oben
for t in (45,):
    a = f0 + t * u
    paint(poly(a + 5 * z - 0.35 * u, a + 5 * z + 0.35 * u, a + 80 * z + 0.35 * u, a + 80 * z - 0.35 * u), None, mult=0.86)
paint(poly(f1 + 20 * z, f0 + 20 * z, f0 + 20.8 * z, f1 + 20.8 * z), None, mult=0.88)
# Innenecke: leichte Verschattung an der Kante zur langen Zeile
paint(poly(f0 + 4 * z, f0 + 4 * z + 6 * u, f0 + H * z + 6 * u, f0 + H * z), None, mult=0.92)
# Arbeitsplatte
paint(poly(b0, b1, f1, f0), top_col)
# Wand direkt über der Platte (Kontaktschatten)
ao = poly(b0, b1, b1 - 3 * z, b0 - 3 * z)
paint(cv2.GaussianBlur(ao[..., 0], (0, 0), 1.0)[..., None], None, mult=0.90)

# Licht: Platte zum Fenster (hinten) heller, Fronten und Stirnseite zum Boden hin dunkler
yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
def along(p0, p1):
    d = p1 - p0; return np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / (d @ d), 0, 1)[..., None]
top_m = poly(b0, b1, f1, f0)
out = out * (1 - top_m) + out * top_m * (1.04 - 0.08 * along(b0, f0))
fr_m = np.clip(poly(f1, f0, f0 + H * z, f1 + H * z) + poly(b1, f1, f1 + H * z, b1 + H * z), 0, 1)
out = out * (1 - fr_m) + out * fr_m * (1.02 - 0.12 * along(f0, f0 + H * z))

# leichtes Rauschen wie im Rendering, nur in der neuen Fläche
area = np.clip(poly(b0, b1, f1, f0) + poly(b1, f1, f1 + H * z, b1 + H * z) + front, 0, 1)
rng = np.random.default_rng(1)
noise = cv2.GaussianBlur(rng.normal(0, 1.4, im.shape[:2]).astype(np.float32), (0, 0), 0.6)[..., None]
out = out + noise * area
cv2.imwrite(OUT, np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 97])
