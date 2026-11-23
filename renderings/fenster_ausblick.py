"""Ausblick in den Fenstern der Innenansichten ersetzen (Hochhäuser → ruhige Baumkronen vor hellem Himmel).

Aufruf: python3 renderings/fenster_ausblick.py [Wohnung …]   (ohne Angabe: Wohnungen 1, 4 und 5)
Liest renderings/fenster/vorher/Wohnung N Innenansicht.jpg (Stand vor dieser Bearbeitung) und schreibt nach
renderings/fotorealistisch/auswahl/Wohnung N Innenansicht.jpg.

Nur die Glasflächen werden neu belegt; Rahmen, Vorhänge, Möbel, Pflanzen und Leuchten vor den Fenstern
bleiben pixelgleich (an ihren Kanten wird der alte Hintergrund herausgerechnet: Freistellung mit
geschätzter Vorder- und Hintergrundfarbe).

Der neue Ausblick: Baumkronen aus der Tagesansicht der Umgebung (renderings/fotorealistisch/
Aussenansicht Umgebung.jpg), auf neutrales Tageslicht umgerechnet, entsättigt und mit Dunst aufgehellt,
wie bei einer Innenaufnahme, die auf den Raum belichtet ist. Helligkeit des Himmels wie bisher im Fenster.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).parent
SRC = ROOT / "fenster" / "vorher"
OUT = ROOT / "fotorealistisch" / "auswahl"
ENV = ROOT / "fotorealistisch" / "Aussenansicht Umgebung.jpg"
LUM = np.array([0.114, 0.587, 0.299], np.float32)  # BGR


# ---------- Baumreihe ----------
def tree_tile():
    """Baumkronen vor Himmel als relative Helligkeit (Himmel = 1)."""
    env = cv2.imread(str(ENV)).astype(np.float32) / 255
    top = env[605:660, 330:560].reshape(-1, 3)
    lt = top @ LUM
    sky = top[lt >= np.percentile(lt, 40)].mean(0)
    a = np.clip(env[600:786, 310:572] / sky, 0, 1)
    # leichte Helligkeitsschwankungen im Himmel entfernen (weiches Knie unter 1)
    d = 1 - a
    d = np.maximum(d - 0.035, 0) / 0.965
    a = 1 - d
    h, w = a.shape[:2]
    # weiche Ränder links/rechts/oben, damit Kacheln nahtlos ineinander übergehen
    fx = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / 28.0, 0, 1)
    fy = np.clip(np.arange(h) / 14.0, 0, 1)
    f = (fx[None, :] * fy[:, None]) ** 1.5
    return 1 - (1 - a) * f[..., None]


TILE = None


def place(canvas, tile, x, y, s, flip, fade):
    t = cv2.resize(tile, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
    if flip:
        t = t[:, ::-1]
    t = 1 - (1 - np.clip(t, 0, 1)) * fade
    H, W = canvas.shape[:2]
    h, w = t.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 > x0 and y1 > y0:
        canvas[y0:y1, x0:x1] = np.minimum(canvas[y0:y1, x0:x1], t[y0 - y:y1 - y, x0 - x:x1 - x])


def treeline(W, H, top, s, seed, rows=1, back=0.45, hedge=None):
    """Relative Helligkeit (H×W×3): Himmel 1, darunter Baumkronen ab Zeile top (Maßstab s)."""
    global TILE
    if TILE is None:
        TILE = tree_tile()
    rng = np.random.default_rng(seed)
    c = np.ones((H, W, 3), np.float32)
    th, tw = TILE.shape[0] * s, TILE.shape[1] * s
    x = -rng.uniform(0.1, 0.5) * tw                      # hintere, blassere Reihe
    while x < W:
        place(c, TILE, int(x), int(top - rng.uniform(2, 16) * s), s * rng.uniform(0.72, 0.88), rng.random() < .5, back)
        x += tw * rng.uniform(0.5, 0.7)
    for r in range(rows):                                # vordere Reihen, nach unten dichter
        x = -rng.uniform(0.1, 0.6) * tw
        while x < W:
            place(c, TILE, int(x), int(top + r * 0.5 * th + rng.uniform(0, 12) * s), s * rng.uniform(0.92, 1.1),
                  rng.random() < .5, 1.0)
            x += tw * rng.uniform(0.6, 0.8)
    if hedge is not None:                                # Erdgeschoss: dichtes Grün (Hecke, Sträucher) bis unten
        dense = TILE[95:]
        y = hedge
        while y < H:
            x = -rng.uniform(0.1, 0.5) * tw
            while x < W:
                place(c, dense, int(x), int(y + rng.uniform(-8, 8) * s), s * rng.uniform(0.9, 1.1), rng.random() < .5, 1.0)
                x += tw * rng.uniform(0.35, 0.5)
            y += dense.shape[0] * s * 0.45
    return c


def grade(rel, haze=0.36, sat=0.6, blur=0.8):
    lum = (rel * LUM).sum(2, keepdims=True)
    rel = lum + (rel - lum) * sat
    rel = 1 - (1 - rel) * (1 - haze)
    return cv2.GaussianBlur(rel, (0, 0), blur) if blur else rel


# ---------- Masken und Freistellung ----------
def poly_mask(shape, pts, ss=8):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts, np.float64) * ss).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=3)
    return m.astype(np.float32) / 255


def normconv(img, w, sigma):
    num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(w, (0, 0), sigma)[..., None]
    return num / np.maximum(den, 1e-4), den[..., 0]


def matte(I, fg_core, bg_core, band, sigma=2.5):
    """Alpha des Vordergrunds im Band; liefert alpha und geschätzten alten Hintergrund B."""
    F, fden = normconv(I, fg_core, sigma)
    B, _ = normconv(I, bg_core, sigma)
    d = F - B
    a = ((I - B) * d).sum(2) / np.maximum((d * d).sum(2), 1e-4)
    a = np.clip(a, 0, 1) * np.clip((fden - 0.04) / 0.08, 0, 1)    # ohne Vordergrund in der Nähe: Hintergrund
    a = np.where(fg_core > 0, 1.0, np.where(bg_core > 0, 0.0, a)) * band + fg_core * (1 - band)
    # alter Hintergrund so, dass I = a·F + (1 − a)·B exakt gilt (bei a = 0 ist B = I)
    al = a[..., None]
    B = np.where(al < 0.97, (I - al * F) / np.maximum(1 - al, 0.03), B)
    return a.astype(np.float32), np.clip(B, 0, 1)


def composite(I, glass, view, occ_alpha=None, B_old=None):
    """glass: weiche Maske der Glasfläche; view: neues Bild (BGR 0..1) für das ganze Bild."""
    if occ_alpha is None:
        out = view
    else:
        Bo = I if B_old is None else B_old
        out = I + (1 - occ_alpha)[..., None] * (view - Bo)
    g = glass[..., None]
    return I * (1 - g) + out * g


def grain(shape, seed, amount=0.006):
    rng = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rng.normal(0, 1, shape[:2]).astype(np.float32), (0, 0), 0.6)
    return n[..., None] * amount


def view_in(shape, box, sky, rel):
    """Neues Fensterbild: Himmelsfarbe × relative Helligkeit der Baumreihe, eingesetzt im Rechteck box."""
    x0, y0, x1, y1 = box
    v = np.ones(shape, np.float32) * sky
    yy = np.arange(y0, y1, dtype=np.float32)[:, None, None]
    t = (yy - y0) / max(y1 - y0, 1)
    grad = 0.955 + 0.045 * t                                   # Himmel oben etwas dunkler und kühler
    grad = grad * (1 + (1 - t) * np.array([0.012, 0.0, -0.012], np.float32))
    v[y0:y1, x0:x1] = sky * grad * rel
    return v


# ---------- Wohnung 1. Obergeschoss (Quelle: Wohnung 4) ----------
def w4(I):
    H, W = I.shape[:2]
    V = I.max(2)
    out = I.copy()
    # großes Fenster rechts: Glaskanten aus den Rahmenkanten gemessen
    top = lambda x: 294 - 0.2 * (x - 1235)
    right = lambda y: 1644 - 0.184 * (y - 240)
    left = lambda y: 1221 - 0.0615 * (y - 300)
    bottom = lambda x: 597 + 0.0 * x
    # Eckpunkte als Schnitt der Geraden (wenige Iterationen genügen)
    def corner(fx, fy, x):
        for _ in range(20):
            y = fy(x); x = fx(y)
        return x, fy(x)
    tl = corner(left, top, 1220); tr = corner(right, top, 1640)
    br = corner(right, bottom, 1590); bl = corner(left, bottom, 1205)
    # unten reicht das Glas bis hinter das Sofa (Unterkante wird vom Sofa verdeckt)
    glass = poly_mask(I.shape, [tl, tr, (1583, 580), (1440, 600), (1432, 616), (1235, 606), bl])
    # Sofa vor dem Fenster: Oberkante je Spalte (scharfer Sprung auf hell), geführt von einem groben
    # Verlauf der Sofakante, damit helle Altbau-Reste im alten Ausblick nicht als Sofa gelten
    xs, ys = zip(*[(1203, 597), (1215, 599), (1235, 604), (1248, 606), (1255, 600), (1300, 593), (1318, 590),
                   (1335, 593), (1350, 596), (1425, 611), (1432, 612), (1436, 578), (1440, 569), (1450, 566),
                   (1460, 565), (1515, 573), (1585, 583), (1600, 585)])
    sofa = np.zeros((H, W), np.float32)
    edge = {}
    for x in range(1203, 1600):
        prior = np.interp(x, xs, ys)
        col = V[530:640, x]
        cand = [530 + j + 1 for j in np.where((col[1:-7] > 0.80) & (col[:-8] < 0.70))[0] if col[j + 1:j + 7].mean() > 0.82]
        near = [c for c in cand if abs(c - prior) <= 3]
        edge[x] = min(near, key=lambda c: abs(c - prior)) if near else int(round(prior))
    xs_e = np.array(sorted(edge)); ys_e = np.array([edge[x] for x in xs_e])
    ys_m = np.array([int(np.median(ys_e[max(i - 2, 0):i + 3])) for i in range(len(ys_e))])   # Ausreißer glätten
    for x, y in zip(xs_e, ys_m):
        sofa[y:, x] = 1
        p, q = V[y - 3, x], V[y + 1, x]                 # Kantenpixel anteilig (Kantenglättung)
        sofa[y - 1, x] = np.clip((V[y - 1, x] - p) / max(q - p, 1e-3), 0, 1)
    for y in range(564, 614):                       # linke, runde Kante des hohen Sofateils
        row = V[y, 1420:1452]
        e = [i for i in range(1, len(row)) if row[i] > 0.8 and row[i - 1] < 0.75]
        if e:
            sofa[y, 1420 + e[0]:1452] = 1
            sofa[y, 1420 + e[0] - 1] = max(sofa[y, 1420 + e[0] - 1], 0.5)
    glass = glass * (1 - sofa)
    # Bogenleuchte vor dem Glas: Band um Bogen und Schirm, Kern = dunkel
    band = np.zeros((H, W), np.uint8)
    arc = np.array([(1211, 466), (1214, 450), (1218, 440), (1224, 428), (1231, 418), (1240, 409), (1249, 403),
                    (1258, 399)], np.int32)
    cv2.polylines(band, [arc], False, 1, thickness=11)
    cv2.fillPoly(band, [np.array([(1246, 401), (1256, 390), (1269, 387), (1279, 390), (1288, 399), (1286, 407),
                                  (1248, 408)], np.int32)], 1)
    bandf = cv2.GaussianBlur(band.astype(np.float32), (0, 0), 1.0)
    bandm = (band > 0)
    fg = ((V < 0.43) & bandm).astype(np.float32)
    bg = (((V > 0.62) & bandm) | (~bandm)).astype(np.float32) * (glass > 0.5)
    a, B = matte(I, fg, bg, bandm.astype(np.float32))
    x0, y0 = int(bl[0]) - 4, int(tr[1]) - 4
    x1, y1 = int(tr[0]) + 4, int(bl[1]) + 6
    sky = np.array([0.975, 0.975, 0.965], np.float32)
    rel = grade(treeline(x1 - x0, y1 - y0, 455 - y0, 1.25, 11, rows=2), haze=0.32)
    view = view_in(I.shape, (x0, y0, x1, y1), sky, rel) + grain(I.shape, 4)
    out = composite(out, glass, view, occ_alpha=a * bandm, B_old=B)

    # zwei schmale Fenster links zwischen Vorhängen, teils hinter Stores
    # (Falten der Stores leicht schräg: 0,07 px je Zeile; Helligkeit je Spalte aus den hellsten Pixeln)
    out = curtain_window(I, out, [(412, 266), (522, 266), (524, 472), (440, 472)], rows=(272, 335), shear=0.07,
                         tree=(400, 250, 140, 240, 405, 0.8, 5), seed=5, haze=0.34, q=75, protect=0.64)
    out = curtain_window(I, out, [(718, 307), (788, 307), (791, 472), (732, 472)], rows=(312, 420), shear=0.05,
                         tree=(700, 290, 110, 200, 418, 0.75, 6), seed=6, haze=0.34, q=75, protect=0.64)
    return out


def w1(I):
    H, W = I.shape[:2]
    V = I.max(2)
    B_, G_, R_ = I[..., 0], I[..., 1], I[..., 2]
    green = G_ - np.maximum(R_, B_)
    out = I.copy()
    sky = np.array([0.965, 0.96, 0.94], np.float32)

    # großes Fenster links (Kanten aus den Rahmen gemessen), davor die Pflanze
    # Unterkante = Oberkante des weißen Rahmenprofils über der dunklen Dichtung
    glass = poly_mask(I.shape, [(-2, 144), (339, 288), (369.3, 713.5), (0, 935.5), (-2, 935.5)])
    # Pflanze: grüne oder dunkle Pixel mit grünlicher Umgebung; dunkelgraue Teile des alten Ausblicks
    # (Fenster, Kanten der Hochhäuser) sind nicht grün und gehören zum Hintergrund
    gb = cv2.GaussianBlur(green, (0, 0), 2.0)
    fg = (((V < 0.30) & (gb > -0.004)) | ((green > 0.022) & (V < 0.55))).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    area = st[:, cv2.CC_STAT_AREA]
    gmean = np.bincount(lab.ravel(), weights=green.ravel(), minlength=n) / np.maximum(area, 1)
    keep = np.zeros(n, bool)
    keep[1:] = (area[1:] > 400) | ((area[1:] > 30) & (gmean[1:] > 0.008))   # dünne graue Linien: alter Ausblick
    fg = keep[lab].astype(np.float32)
    trunk = poly_mask(I.shape, [(113, 700), (160, 700), (166, 740), (171, 780), (172, 860), (174, 900), (184, 960),
                                (130, 985), (133, 900), (125, 860), (124, 780), (118, 740)])
    w_ = R_ - B_                                        # Stamm: bräunlich
    stem = (trunk > 0.5) & (((w_ > 0.03) & (V < 0.5)) | (V < 0.16))
    stem = cv2.morphologyEx(stem.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    fg = np.maximum(fg * (1 - (trunk > 0.5) * (1 - stem) * (green < 0.01)), stem)
    bg = (((V > 0.48) & (green < 0.004)) | ((V <= 0.48) & (gb < -0.012))).astype(np.float32)
    bg = np.maximum(bg, ((trunk > 0.5) & ~stem.astype(bool) & (green < 0.01)).astype(np.float32))
    bg = bg * (1 - cv2.dilate(fg, np.ones((3, 3), np.uint8)))
    band = 1 - np.clip(fg + bg, 0, 1)
    a, Bold = matte(I, fg, bg, band, sigma=2.0)
    rel = grade(treeline(380, 1000, 330, 2.1, 21, rows=2, hedge=640), haze=0.30, blur=1.0)
    view = view_in(I.shape, (0, 0, 380, 1000), sky, rel) + grain(I.shape, 7)
    out = composite(out, glass, view, occ_alpha=a, B_old=Bold)

    # hinteres Fenster an der Küche
    glass2 = poly_mask(I.shape, [(856.3, 331.2), (951.0, 333.2), (951.0, 510.6), (857.8, 510.6)])
    rel2 = grade(treeline(110, 190, 75, 0.85, 22, rows=2), haze=0.34)
    view2 = view_in(I.shape, (850, 325, 960, 515), sky, rel2) + grain(I.shape, 8)
    out = composite(out, glass2, view2)
    return out


def column_light(I, mask, shear, rows, q=50):
    """Helligkeit je Spalte (entlang der Faltenrichtung, shear = dx je dy) aus den Zeilen rows, wo nur Himmel
    durch Glas und Stores zu sehen ist: Mittel der helleren Hälfte. Liefert ein Bild in Größe von I."""
    H, W = I.shape[:2]
    ya, yb = rows
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    xs = xx - shear * (yy - ya)                                   # gescherte Spalte
    sel = (mask > 0.5) & (yy >= ya) & (yy < yb)
    keys = np.round(xs[sel]).astype(int)
    vals = I[sel]
    lum = vals @ LUM
    k0, k1 = keys.min(), keys.max()
    prof = np.zeros((k1 - k0 + 1, 3), np.float32)
    have = np.zeros(k1 - k0 + 1, bool)
    for k in range(k0, k1 + 1):
        m = keys == k
        if m.sum() >= 3:
            l = lum[m]
            prof[k - k0] = vals[m][l >= np.percentile(l, q)].mean(0)
            have[k - k0] = True
    idx = np.arange(len(prof))
    for c in range(3):
        prof[:, c] = np.interp(idx, idx[have], prof[have, c])
    prof = cv2.GaussianBlur(prof[:, None, :], (0, 0), sigmaX=0.1, sigmaY=0.8)[:, 0, :]
    kf = np.clip(xs - k0, 0, len(prof) - 1.001)                 # linear zwischen den Spalten (keine Treppen)
    k = kf.astype(int)
    f = (kf - k)[..., None]
    return prof[k] * (1 - f) + prof[k + 1] * f, (xs, k0)


def curtain_window(I, out, P, rows, shear, tree, fg_limit=None, seed=9, haze=0.30, q=50, protect=None):
    """Fenster zwischen blickdichten (warmen) Vorhängen, teils hinter weißen Stores.

    P: Glasfläche (darf in die Vorhänge hineinreichen), rows: Zeilen, in denen nur Himmel durch Glas und
    Stores zu sehen ist (daraus die Helligkeit je Spalte), shear: Neigung der Falten (dx je dy),
    tree: (x0, y0, Breite, Höhe, Oberkante der Bäume, Maßstab, Zufallswert) der Baumreihe.
    """
    H, W = I.shape[:2]
    V = I.max(2)
    warm = I[..., 2] - I[..., 0]
    glass = poly_mask(I.shape, P)
    inner = cv2.erode((glass > 0.5).astype(np.uint8), np.ones((25, 25), np.uint8))
    # Vorhangstoff: warme, wenig bunte Flächen, die über die Fensterfläche hinausreichen (ein warmer Fleck
    # im alten Ausblick, ganz innerhalb der Fläche, gehört nicht dazu)
    sat = (V - I.min(2)) / np.maximum(V, 1e-3)
    wm = ((warm > 0.035) & (V < 0.8) & (sat < 0.25)).astype(np.uint8)
    n, lab = cv2.connectedComponents(wm, connectivity=8)
    outside = np.unique(lab[(glass < 0.5) & (wm > 0)])
    fg = np.isin(lab, outside[outside > 0]).astype(np.float32)
    obj = cv2.dilate(((sat > 0.28) & (glass > 0.5)).astype(np.uint8), np.ones((9, 9), np.uint8))  # bunter Rest
    fg = fg * (1 - obj * (glass > 0.5))                                                          # im alten Ausblick
    if fg_limit is not None:
        fg = fg * fg_limit
    bg = ((warm < -0.012) | ((glass > 0.5) & (fg == 0) & (warm > 0.035))).astype(np.float32)  # warme Reste im
    bg = np.maximum(bg, inner.astype(np.float32)) * (1 - cv2.dilate(fg, np.ones((3, 3), np.uint8)))  # alten Ausblick
    band = 1 - np.clip(fg + bg, 0, 1)
    a, Bold = matte(I, fg, bg, band, sigma=2.0)
    core = cv2.erode(fg, np.ones((3, 3), np.uint8))
    a = np.maximum(cv2.GaussianBlur(a, (0, 0), 0.9), core)              # Stoffkante weich (keine Treppen)
    L, _ = column_light(I, glass, shear, rows, q=q)
    if protect is not None:                       # dunkle Falten (Schatten im Stoff) bleiben unverändert
        a = np.maximum(a, 1 - np.clip((V - protect) / 0.08, 0, 1))
    lum = (L * LUM).sum(2)
    t = 0.5 + 0.5 * np.clip((lum - 0.80) / 0.08, 0, 1)                       # klares Glas 1, Stores 0,5
    x0, y0, w, h, top, sc, sd = tree
    rel = np.ones((H, W, 3), np.float32)
    rel[y0:y0 + h, x0:x0 + w] = grade(treeline(w, h, top - y0, sc, sd, rows=2), haze=haze, blur=1.0)
    view = L * rel ** t[..., None] + grain(I.shape, seed, 0.005)
    return composite(out, glass, view, occ_alpha=a, B_old=Bold)


# ---------- Wohnung 2. Obergeschoss (Quelle: Wohnung 5) ----------
def w5(I):
    H, W = I.shape[:2]
    V = I.max(2)
    warm = I[..., 2] - I[..., 0]
    out = I.copy()
    sky = np.array([0.975, 0.97, 0.96], np.float32)

    # großes Fenster links hinter Stores, zwischen zwei blickdichten Vorhängen (Kanten schräg)
    # Fläche zwischen den Vorhängen; die Kanten werden über die Farbe (Stoff warm, Ausblick kühl) freigestellt
    # linker Vorhang: Kante gemessen (x = 237 + 0,387 · (y − 260)); Stoff nur bis 3 px rechts davon, damit
    # bräunliche Reste im alten Ausblick direkt neben der Kante nicht als Vorhang gelten
    yy, xx = np.mgrid[0:H, 0:W]
    out = curtain_window(I, out, [(232, 262), (408, 262), (498, 652), (380, 685), (354, 685)],   # unten bis
                         rows=(266, 318), shear=0.27, tree=(220, 250, 300, 450, 452, 1.35, 31),       # zum Rahmen
                         fg_limit=(xx < 237 + 0.387 * (yy - 260) + 3) | (xx > 400), seed=9)

    # kleines Fenster rechts (Kanten aus den Rahmen gemessen)
    top = lambda x: 272 - 0.12 * (x - 1320)
    left = lambda y: 1306 - 0.167 * (y - 280)
    right = lambda y: 1422 - 0.218 * (y - 270)
    bottom = lambda x: 453 + 0.025 * (x - 1295)
    def corner(fx, fy, x):
        for _ in range(20):
            y = fy(x); x = fx(y)
        return x, fy(x)
    g2 = poly_mask(I.shape, [corner(left, top, 1305), corner(right, top, 1420), corner(right, bottom, 1385),
                             corner(left, bottom, 1282)])
    rel2 = np.ones((H, W, 3), np.float32)
    rel2[240:470, 1270:1440] = grade(treeline(170, 230, 160, 0.85, 32, rows=2), haze=0.34)
    view2 = view_in(I.shape, (1270, 240, 1440, 470), sky, rel2[240:470, 1270:1440]) + grain(I.shape, 10, 0.005)
    out = composite(out, g2, view2)

    # Spiegelung des Fensters im Fernseher: weich, nach rechts dunkler
    tv = poly_mask(I.shape, [(1508, 264), (1530, 247), (1562, 241), (1552, 300), (1536, 380), (1522, 454),
                             (1463, 454), (1486, 357)])
    tv = cv2.GaussianBlur(tv, (0, 0), 1.2) * poly_mask(I.shape, [(1505, 262), (1600, 230), (1600, 456),
                                                                  (1460, 456)])
    L3, _ = column_light(I, tv, -0.233, (266, 315), q=60)
    rel3 = np.ones((H, W, 3), np.float32)
    rel3[230:470, 1440:1600] = grade(treeline(160, 240, 120, 0.9, 33, rows=2), haze=0.45, blur=3.0)
    view3 = L3 * rel3 ** 0.7 + grain(I.shape, 11, 0.004)
    out = composite(out, tv, view3)
    return out


JOBS = {1: w1, 4: w4, 5: w5}


def main():
    wanted = [int(a) for a in sys.argv[1:]] or sorted(JOBS)
    for n in wanted:
        I = cv2.imread(str(SRC / f"Wohnung {n} Innenansicht.jpg")).astype(np.float32) / 255
        res = JOBS[n](I)
        dest = OUT / f"Wohnung {n} Innenansicht.jpg"
        res8 = (np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)
        from PIL import Image
        Image.fromarray(cv2.cvtColor(res8, cv2.COLOR_BGR2RGB)).save(
            dest, "JPEG", quality=95, subsampling=0, optimize=True, progressive=True)
        print(dest.relative_to(ROOT.parent))


if __name__ == "__main__":
    main()
