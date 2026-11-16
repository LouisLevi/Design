"""Fotorealistischeres Licht für eine Homestyler-Luftansicht, ohne Struktur oder Möbel zu verändern.

Nur multiplikative Licht- und Farbkorrekturen auf dem vorhandenen Bild (keine Pixel werden verschoben):
Kontaktschatten (Ambient Occlusion) an Wänden und Möbeln, weiches Tageslicht durch das Fenster der
linken Wand, Helligkeitsverlauf von der Fensterseite in den Raum, beschattete Außenwände,
fotografische Tonkurve und feines Korn. Der weiße Hintergrund bleibt unverändert.

Aufruf: python3 renderings/licht_luftansicht.py <eingabe.png> <ausgabe.png>
Angewendet auf: Luftansicht Wohnung Erdgeschoss (renderings/auswahl/Wohnung 1 Luftansicht.png).
Die Lichtgeometrie (Fenster, Raumgrenzen) ist für dieses Bild (1672 × 941) eingemessen.
"""
import sys

import cv2
import numpy as np


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def masks(im):
    nw = (im.min(axis=2) >= 254).astype(np.uint8)
    _, lab = cv2.connectedComponents(nw, connectivity=4)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    model = (~np.isin(lab, border[border > 0])).astype(np.uint8)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    H, S, V = (hsv[..., i].astype(int) for i in range(3))
    floor = ((H >= 12) & (H <= 21) & (S >= 60) & (S <= 175) & (V >= 115)).astype(np.uint8) & model
    floor = cv2.morphologyEx(floor, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    floor = cv2.morphologyEx(floor, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab2, st, _ = cv2.connectedComponentsWithStats(floor, connectivity=8)
    floor = np.isin(lab2, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 3000]).astype(np.uint8)
    white = ((S < 25) & (V > 200)).astype(np.uint8) & model & (1 - floor)
    return model, floor, white


def soft_poly(shape, pts, sigma):
    m = np.zeros(shape, np.float32)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 1.0, lineType=cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), sigma)


def relight(im):
    h, w = im.shape[:2]
    model, floor, white = masks(im)
    mf = model.astype(np.float32)[..., None]
    lin = srgb_to_lin(im.astype(np.float32) / 255)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    # 1) Kontaktschatten auf dem Boden an Wänden und Möbeln
    d_floor = cv2.distanceTransform(floor, cv2.DIST_L2, 5)
    ao_floor = 1 - 0.34 * np.exp(-d_floor / 10.0) - 0.12 * np.exp(-d_floor / 38.0)
    # 2) Wandfuß: Wände werden zum Boden hin etwas dunkler
    d_wall = cv2.distanceTransform(1 - floor, cv2.DIST_L2, 5)
    ao_wall = 1 - 0.16 * np.exp(-d_wall / 12.0)
    shade = np.where(floor > 0, ao_floor, np.where(white > 0, ao_wall, 1.0))
    # 2b) Schlagschatten der Möbel: Möbel = Löcher in der Bodenfläche; Licht vom Fenster links →
    #     Schatten fallen nach rechts unten, weich auslaufend
    cs, _ = cv2.findContours(floor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filled = np.zeros_like(floor)
    cv2.drawContours(filled, cs, -1, 1, -1)
    furniture = (filled & (1 - floor)).astype(np.float32)
    cast = np.zeros_like(furniture)
    for k, (dx, dy) in enumerate([(4, 2), (8, 4), (13, 6), (19, 9)]):
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        cast = np.maximum(cast, cv2.warpAffine(furniture, M, (w, h)) * (1 - 0.18 * k))
    cast = cv2.GaussianBlur(cast, (0, 0), 3.5) * floor
    shade = shade * (1 - 0.36 * cast)
    # Weicher Übergang an allen Maskenkanten: Bodenschatten stetig fortsetzen und mit der weichen
    # Bodenmaske gewichten, Wandfuß ebenso → keine hellen oder dunklen Säume an Möbeln und Wänden
    ff = floor.astype(np.float32)
    f_soft = cv2.GaussianBlur(ff, (0, 0), 1.3)
    floor_shade = np.where(floor > 0, shade, 0).astype(np.float32)
    ext = cv2.GaussianBlur(floor_shade, (0, 0), 2.0) / np.maximum(cv2.GaussianBlur(ff, (0, 0), 2.0), 1e-3)
    ext = np.where(cv2.GaussianBlur(ff, (0, 0), 2.0) > 1e-3, ext, 1.0)
    wall_w = cv2.GaussianBlur(white.astype(np.float32), (0, 0), 1.3)
    shade = 1 + (ext - 1) * f_soft + (ao_wall - 1) * wall_w * (1 - f_soft)

    # 3) Tageslicht durch das Fenster der linken Wand: weiche, warme Lichtfläche auf Boden und Möbeln
    sun = soft_poly((h, w), [(590, 318), (590, 478), (838, 548), (838, 388)], 22)
    sun = np.maximum(sun, 0.55 * soft_poly((h, w), [(742, 236), (818, 236), (846, 330), (768, 330)], 18))  # Fenster hinten
    sun *= (1 - white.astype(np.float32) * 0.85)          # Licht fällt auf Boden/Möbel, kaum auf Wandflächen
    sun *= np.clip(shade, 0, 1) ** 2                       # in Kontakt- und Schlagschatten kein Sonnenlicht
    # 4) Raumhelligkeit: zur Fensterseite heller, nach rechts/hinten etwas dunkler (nur Innenflächen)
    room = np.clip(1.07 - 0.16 * (xx - 590) / 900.0, 0.88, 1.07)
    # Innenwände: Lichtabfall mit dem Abstand zum Fenster (Außenkanten/Fassade ausgenommen)
    bg0 = (1 - model).astype(np.uint8)
    d_out = cv2.distanceTransform(1 - bg0, cv2.DIST_L2, 5)
    dist_win = np.hypot(xx - 600, (yy - 400) * 1.2)
    wall_light = 0.90 + 0.16 * np.exp(-dist_win / 420.0)
    inner = cv2.GaussianBlur(((white > 0) & (d_out > 45)).astype(np.float32), (0, 0), 6)
    room = np.where(white > 0, 1.0 + (wall_light - 1.0) * inner, room)
    # 5) Gesamtlicht von links oben
    glob = 1.03 - 0.07 * ((xx - 480) / 1100.0 + (yy - 60) / 760.0) / 2

    lit = lin * (shade * room * glob)[..., None]
    warm = np.array([0.86, 0.97, 1.10], np.float32)       # BGR: warmes Tageslicht
    lit = lit * (1 + sun[..., None] * 0.62 * warm)

    # 6) Außenwände vorn (Südseite): leicht beschattet, kühler, zum Boden hin dunkler
    bg = (1 - model).astype(np.uint8)
    d_bg = cv2.distanceTransform(1 - bg, cv2.DIST_L2, 5)
    facade = (white > 0) & (d_bg < 120) & (yy > 690)
    fac = np.zeros((h, w), np.float32)
    fac[facade] = 1
    fac = cv2.GaussianBlur(fac, (0, 0), 2) * mf[..., 0]
    grad = np.clip((yy - 690) / 120.0, 0, 1)
    lit = lit * (1 - fac[..., None] * (0.06 + 0.08 * grad[..., None]) * np.array([1.0, 1.0, 1.04]))
    lit = lit * (1 + fac[..., None] * np.array([0.025, 0.0, -0.02]))

    out = lin_to_srgb(lit)
    # 7) fotografische Tonkurve (leichtes S) und Farbtrennung: warme Lichter, kühle Schatten
    lum = (out @ np.array([0.114, 0.587, 0.299], np.float32))[..., None]
    s_curve = lum + 0.10 * (lum - 0.5) * (1 - np.abs(2 * lum - 1))
    out = out * np.where(lum > 1e-4, s_curve / np.maximum(lum, 1e-4), 1)
    split = (lum - 0.5) * np.array([-0.025, 0.0, 0.025], np.float32)
    out = np.clip(out + split * 0.6, 0, 1)
    # Holzboden etwas weniger orange (realistischer)
    hsv = cv2.cvtColor((out * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.where(floor > 0, hsv[..., 1] * 0.90, hsv[..., 1])
    out = cv2.cvtColor(hsv.clip(0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255

    # 8) feines Korn
    rng = np.random.default_rng(7)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 0.7)[..., None] * 0.006
    out = out + grain

    # Hintergrund bleibt exakt wie vorher
    res = out * mf + (im.astype(np.float32) / 255) * (1 - mf)
    return (np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == "__main__":
    src = cv2.imread(sys.argv[1])
    cv2.imwrite(sys.argv[2], relight(src))
