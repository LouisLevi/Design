"""Exposé Altenbaunaer Straße 26 als HTML erzeugen und mit Chromium zu PDF rendern.

Aufruf: python3 expose/build.py
Ergebnis: expose/Expose_Altenbaunaer_Strasse_26.pdf (+ expose.html zum Prüfen im Browser)
Vorher einmal: python3 expose/prepare_assets.py <alte-mappe.pdf>
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PLANS = json.loads((ROOT / "assets" / "plans" / "plans.json").read_text())
ADDRESS = "Altenbaunaer Straße 26"
CITY = "34134 Kassel"
MOVE_IN = "Januar 2027"
CONTACT = {"name": "Carsten Günther", "phone": "0179 2199 100", "tel": "+491792199100",
           "mail": "buero@planungsbuero-guenther.de"}
EFFICIENCY = "A+"  # Prognose für den Neubau, kein Wert aus einem Energieausweis
NB = " "  # geschütztes Leerzeichen


def missing(what):
    return f'<span class="missing">[FEHLT: {what}]</span>'


def m2(v):
    return f"{v}{NB}m²"


def eur(v):
    return f"{v}{NB}€"


def deposit(rent, months=3):
    """Kaution als Vielfaches der Kaltmiete, deutsch formatiert."""
    from decimal import Decimal
    v = Decimal(rent.replace(".", "").replace(",", ".")) * months
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + NB + "€"


UNITS = [
    {
        "n": 1, "floor": "Erdgeschoss", "floor_short": "EG", "area": "53,03", "rent": "742,42", "sqm": "14,00", "outdoor": None,
        "lead": "Zwei Zimmer auf 53,03" + NB + "m²",
        "text": [
            "Der Wohn-, Koch- und Essbereich ist mit 29,70" + NB + "m² der größte Raum der Wohnung "
            "und hat Fenster an drei Seiten. Das Schlafzimmer mit 12,67" + NB + "m² liegt davon getrennt am Flur.",
            "Daneben das Bad mit Fenster und bodengleicher Dusche. Ein eigener Abstellraum mit 2,60" + NB + "m² "
            "schafft Stauraum außerhalb der Wohnräume.",
        ],
        "rooms": [("Wohnen, Kochen, Essen", "29,70"), ("Schlafen", "12,67"), ("Bad", "4,71"), ("Flur", "3,35"),
                  ("Abstellraum", "2,60")],
        "split": "Wohnen/Kochen/Essen, Schlafen, Bad, Flur, Abstellraum",
        "room_caption": "Wohnen, Kochen und Essen",
        "plans": ["w1"], "luft_h": 125,
    },
    {
        "n": 2, "floor": "Erdgeschoss", "floor_short": "EG", "area": "71,17", "rent": "996,31", "sqm": "14,00", "outdoor": ("Terrasse", "6,13"),
        "lead": "Zwei Zimmer und Terrasse, 71,17" + NB + "m²",
        "text": [
            "Die größte der Zweizimmerwohnungen im Haus. Wohnen, Kochen und Essen teilen sich 43,19" + NB + "m²; "
            "von hier führt eine Tür direkt auf die Terrasse.",
            "Das Schlafzimmer mit 13,52" + NB + "m² liegt abgetrennt im hinteren Teil der Wohnung. "
            "Bad mit Fenster und bodengleicher Dusche, dazu ein separater Abstellraum.",
        ],
        "rooms": [("Wohnen, Kochen, Essen", "43,19"), ("Schlafen", "13,52"), ("Bad", "4,15"), ("Flur", "2,69"),
                  ("Abstellraum", "1,49"), ("Terrasse", "6,13")],
        "split": "Wohnen/Kochen/Essen, Schlafen, Bad, Flur, Abstellraum",
        "room_caption": "Wohnbereich mit Essplatz und Küche",
        "plans": ["w2"], "luft_h": 118,
    },
    {
        "n": 3, "floor": "1. Obergeschoss (Eingangsebene)", "floor_short": "1. OG", "area": "190,95", "rent": "2.577,76", "sqm": "13,50", "outdoor": ("Balkon und Terrasse", "14,51"),
        "lead": "Maisonette über zwei Ebenen, 190,95" + NB + "m²",
        "text": [
            "Die größte Wohnung des Hauses. Auf der Eingangsebene liegt ein offener Wohn-, Koch- und Essbereich "
            "mit 97,57" + NB + "m², Kochinsel und Zugang zum Balkon, dazu ein Gäste-Bad mit Dusche und ein Abstellraum.",
            "Über die Treppe erreichen Sie die obere Ebene: Schlafzimmer, begehbare Ankleide mit 21,88" + NB + "m², "
            "Büro, Bad und eine eigene Terrasse.",
        ],
        "rooms": [("Wohnen, Kochen, Essen", "97,57"), ("Diele", "3,99"), ("Gäste-Bad", "3,58"), ("Abstellraum", "2,05"),
                  ("Balkon", "7,22"), ("Schlafen", "15,50"), ("Ankleide", "21,88"), ("Bad", "7,07"), ("Flur", "13,18"),
                  ("Büro", "11,62"), ("Terrasse", "7,29")],
        "split": "Zwei Ebenen: Wohnen/Kochen/Essen, Schlafen, Ankleide, Büro, Bad, Gäste-Bad, Diele, Flur, Abstellraum",
        "room_caption": "Wohn- und Essbereich mit Treppe zur oberen Ebene",
        "plans": ["w3-eg", "w3-og"], "luft_h": 98,
    },
    {
        "n": 4, "floor": "1. Obergeschoss", "floor_short": "1. OG", "area": "49,00", "rent": "735,00", "sqm": "15,00", "outdoor": None,
        "lead": "Zwei Zimmer auf 49,00" + NB + "m²",
        "text": [
            "Der Eingang führt direkt in den Wohn-, Koch- und Essbereich mit 33,33" + NB + "m² und Fenstern "
            "an zwei Seiten.",
            "Vom Wohnraum aus erreichen Sie das Schlafzimmer mit 12,20" + NB + "m² und das Bad mit Fenster "
            "und bodengleicher Dusche.",
        ],
        "rooms": [("Wohnen, Kochen, Essen", "33,33"), ("Schlafen", "12,20"), ("Bad", "3,47")],
        "split": "Wohnen/Kochen/Essen, Schlafen, Bad",
        "room_caption": "Küche, Essplatz und Wohnbereich",
        "plans": ["w4"], "luft_h": 125,
    },
    {
        "n": 5, "floor": "2. Obergeschoss", "floor_short": "2. OG", "area": "44,70", "rent": "670,43", "sqm": "15,00", "outdoor": ("Terrasse", "4,17"),
        "lead": "Zwei Zimmer und Terrasse, 44,70" + NB + "m²",
        "text": [
            "Der Wohn-, Koch- und Essbereich mit 26,48" + NB + "m² öffnet sich zur vorgelagerten Terrasse.",
            "Schlafzimmer und Bad liegen hinter der Küchenzeile, beide mit Fenster. Ein Flur mit Abstellfläche "
            "von 3,80" + NB + "m² schafft zusätzlichen Stauraum.",
        ],
        "rooms": [("Wohnen, Kochen, Essen", "26,48"), ("Schlafen", "6,35"), ("Bad", "3,90"),
                  ("Flur mit Abstellfläche", "3,80"), ("Terrasse", "4,17")],
        "split": "Wohnen/Kochen/Essen, Schlafen, Bad, Flur mit Abstellfläche",
        "room_caption": "Wohnbereich",
        "plans": ["w5"], "luft_h": 125,
    },
    {
        "n": 6, "floor": "Erdgeschoss", "floor_short": "EG", "area": "33,24", "rent": "498,60", "sqm": "15,00", "outdoor": None,
        "lead": "Einzimmerwohnung, 33,24" + NB + "m²",
        "text": [
            "Wohnen, Essen und Schlafen teilen sich einen Raum mit 20,76" + NB + "m² und zwei Fenstern "
            "an der Längsseite.",
            "Die Küche liegt im Eingangsbereich, getrennt vom Wohnraum, daneben eine kleine Ankleide. "
            "Bad mit Fenster und bodengleicher Dusche.",
        ],
        "rooms": [("Wohnen, Essen, Schlafen", "20,76"), ("Küche und Flur", "6,11"), ("Bad", "3,78"),
                  ("Ankleide", "2,59")],
        "split": "Wohnen/Essen/Schlafen, Küche mit Flur, Bad, Ankleide",
        "room_caption": "Wohn- und Essbereich",
        "plans": ["w6"], "luft_h": 118,
    },
]

PLAN_TITLES = {"w3-eg": "Grundriss Eingangsebene", "w3-og": "Grundriss obere Ebene"}


class Doc:
    def __init__(self):
        self.pages = []

    @property
    def next_no(self):
        return len(self.pages) + 1

    def add(self, inner, content="", content_style="", bottom="", bottom_style="", folio=True):
        no = self.next_no
        side = "recto" if no % 2 else "verso"
        fol = f'<div class="folio"><span>{ADDRESS}</span><b>{no:02d}</b></div>' if folio else ""
        cont = f'<div class="content" style="{content_style}">{content}</div>' if content else ""
        bot = f'<div class="content content-bottom" style="{bottom_style}">{bottom}</div>' if bottom else ""
        self.pages.append(f'<section class="page {side}">{inner}{cont}{bot}{fol}</section>')
        return no


def facts(rows):
    out = []
    for r in rows:
        label, value, *opt = r
        cls = ' class="strong"' if opt and opt[0] else ""
        out.append(f"<tr{cls}><td>{label}</td><td>{value}</td></tr>")
    return f'<table class="facts">{"".join(out)}</table>'


def plan_block(key, scale_mm_per_m=10):
    p = PLANS[key]
    w, h = p["width_m"] * scale_mm_per_m, p["height_m"] * scale_mm_per_m
    labs = "".join(
        f'<div class="lab" style="left:{l["pos"][0]}%;top:{l["pos"][1]}%"><b>{l["name"]}</b>'
        f'<span>{l["area"]}{NB}m²</span></div>' for l in p["labels"])
    return (f'<div class="plan" style="width:{w:.1f}mm;height:{h:.1f}mm">'
            f'<img src="assets/plans/{key}.png" alt="">{labs}</div>'), w, h


def scale_bar():
    return ('<div class="scale-wrap"><div class="scale"><i></i><i></i><i></i><i></i></div>'
            '<div class="scale-nums"><span>0</span><span>1</span><span>2</span><span>3</span><span>4' + NB + 'm</span></div></div>')


def plan_section(key, title):
    block, _, _ = plan_block(key)
    return (
        f'<div style="grid-column:1/13;display:flex;justify-content:space-between;align-items:baseline">'
        f'<div class="kicker">{title}</div><div class="small">Maßstab 1:100 bei A4</div></div>'
        f'<div class="rule" style="grid-column:1/13;margin-top:2mm"></div>'
        f'<div style="grid-column:1/13;margin-top:8mm;display:flex;justify-content:center">{block}</div>'
        f'<div style="grid-column:1/13;margin-top:8mm;display:flex;justify-content:space-between;align-items:flex-end">'
        f'<p class="small" style="max-width:95mm">Möblierung beispielhaft. Grundriss nicht zur Maßentnahme. '
        f'Das schwarze Dreieck markiert den Wohnungseingang.</p>{scale_bar()}</div>')


def build():
    d = Doc()
    first_unit_page = 5
    unit_pages, p = {}, first_unit_page
    for u in UNITS:
        unit_pages[u["n"]] = p
        p += 1 + len(u["plans"])

    # 1 — Titel
    d.add(
        '<img class="bleed-top" src="assets/img/haus.jpg" alt="" '
        'style="top:auto;bottom:0;height:130mm;object-position:72% 50%">'
        '<div style="position:absolute;left:22mm;right:18mm;top:18mm" class="kicker">Exposé zur Vermietung</div>'
        '<div style="position:absolute;left:22mm;top:58mm;width:150mm">'
        '<h1 class="display" style="font-size:54pt;line-height:56pt;letter-spacing:-0.02em">Altenbaunaer<br>Straße 26</h1>'
        f'<p class="lead" style="margin-top:9mm">{CITY}</p>'
        f'<p class="lead" style="color:var(--graphite)">Sechs Mietwohnungen von 33 bis 191{NB}m², '
        f'Erstbezug ab {MOVE_IN}</p></div>'
        '<div class="rule-accent" style="position:absolute;left:22mm;width:14.5mm;top:52mm"></div>'
        '<div class="caption" style="position:absolute;right:18mm;bottom:133mm;text-align:right">'
        'Außenansicht. Visualisierung</div>',
        folio=False)

    # 2 — Auf einen Blick
    rows = "".join(
        f'<tr><td class="nr">{u["n"]}</td><td>{u["floor_short"]}</td><td>{u["split"]}</td>'
        f'<td>{(u["outdoor"][0] + " " + m2(u["outdoor"][1])) if u["outdoor"] else "–"}</td>'
        f'<td class="r num">{m2(u["area"])}</td><td class="r num">{eur(u["rent"])}</td>'
        f'<td class="r num" style="color:var(--graphite)">{unit_pages[u["n"]]:02d}</td></tr>' for u in UNITS)
    d.add("", content=(
        '<div class="kicker" style="grid-column:1/13">Das Haus</div>'
        '<h1 class="display" style="grid-column:1/8;margin-top:6mm">Auf einen Blick</h1>'
        '<div style="grid-column:1/6;margin-top:12mm">'
        '<p class="lead">Im Neubau Altenbaunaer Straße 26 entstehen sechs Mietwohnungen zwischen 33 und '
        f'191{NB}m² – vom Einzimmerapartment bis zur Maisonette über zwei Ebenen.</p>'
        '<p class="body" style="margin-top:5mm">Jede Wohnung erhält eine neue Einbauküche, ein Bad mit '
        'bodengleicher Dusche und Fußbodenheizung in allen Räumen. Wärme liefert eine Luft-Wasser-Wärmepumpe, '
        'Strom eine hauseigene Photovoltaikanlage mit Speicher.</p></div>'
        '<div style="grid-column:7/13;margin-top:12mm">' + facts([
            ("Objekt", f"Neubau, {CITY}"),
            ("Baujahr", "2027"),
            ("Erstbezug", f"ab {MOVE_IN}"),
            ("Wohnungen", "6, im Erdgeschoss bis 2. OG"),
            ("Wohnflächen", f"33,24 – 190,95{NB}m²"),
            ("Kaltmieten", f"498,60 – 2.577,76{NB}€"),
            ("Kaltmiete je m²", f"13,50 – 15,00{NB}€"),
            ("Heizung", "Luft-Wasser-Wärmepumpe"),
            ("Wärmeverteilung", "Fußbodenheizung"),
            ("Strom", "Photovoltaik mit Speicher"),
            ("Keller", f"Kellerraum je Wohnung, ca. 5–10{NB}m²"),
            ("Stellplätze", "nach Absprache"),
        ]) + '</div>'),
        bottom=(
        '<div class="kicker" style="grid-column:1/13">Die Wohnungen</div>'
        '<table class="overview" style="grid-column:1/13;margin-top:3mm"><thead><tr>'
        '<th style="width:9mm">Nr.</th><th style="width:15mm">Geschoss</th><th>Aufteilung</th><th style="width:32mm">Freifläche</th>'
        '<th class="r" style="width:22mm">Wohnfläche</th><th class="r" style="width:22mm">Kaltmiete</th>'
        f'<th class="r" style="width:12mm">Seite</th></tr></thead><tbody>{rows}</tbody></table>'
        '<p class="small" style="grid-column:1/9;margin-top:4mm">Flächen laut Planung, Balkon und Terrassen '
        'in der Wohnfläche enthalten. Kaltmieten zuzüglich Nebenkosten.</p>'))

    # 3 — Ausstattung
    feats = [('Küche', 'Neue Einbauküche mit Backofen, Cerankochfeld, großem Kühlschrank, Geschirrspülmaschine und Abzugshaube'), ('Bad', 'Bodengleiche Dusche'), ('Heizung', 'Fußbodenheizung in allen Räumen, Wohnungsstation'), ('Fenster', 'Dreifachverglasung, elektrische Rollläden, außenliegende Jalousien'), ('Netz', 'Glasfaser-Internet, WLAN in jedem Raum'), ('Elektro', 'Zeitgemäße Unterverteilung, überdurchschnittlich viele Steckdosen')]
    feat_html = "".join(
        f'<div class="feat-item"><span class="no">{i:02d}</span><div><div class="kicker">{k}</div>'
        f'<p>{t}</p></div></div>' for i, (k, t) in enumerate(feats, 1))
    house = [("Zugang", "Video-Klingelanlage, Treppenhaus mit Tageslicht"),
             ("Keller", f"Eigener Kellerraum je Wohnung, ca. 5–10{NB}m²"),
             ("Waschen", "Gemeinschaftliche Waschküche, Möglichkeit zur Wäschetrocknung"),
             ("Garten", "Garten mit Grillplatz zur Mitbenutzung"),
             ("Stellplätze", "Nach Absprache")]
    house_html = "".join(f"<dt>{k}</dt><dd>{t}</dd>" for k, t in house)
    d.add(
        '<img src="assets/img/detail-kueche.jpg" alt="" class="p3-image">'
        '<p class="caption p3-caption"><b>Wohnung 1, Küche.</b> Visualisierung – Einrichtung beispielhaft</p>',
        content=(
        '<div style="grid-column:1/6">'
        '<div class="kicker">Ausstattung</div>'
        '<h1 class="display" style="font-size:44pt;line-height:46pt;margin-top:14mm">In jeder<br>Wohnung</h1>'
        '<p class="lead" style="margin-top:9mm">Neue Einbauküche, Bad mit bodengleicher Dusche und '
        'Fußbodenheizung in allen Räumen.</p>'
        '<p class="body" style="margin-top:6mm">Die Haustechnik ist auf den Alltag ausgelegt: '
        'dreifach verglaste Fenster mit elektrischen Rollläden und außenliegenden Jalousien, '
        'Glasfaser-Internet und WLAN in jedem Raum.</p></div>'),
        bottom=(
        '<div class="kicker" style="grid-column:1/13;margin-bottom:3mm">Wohnung</div>'
        f'<div class="feat" style="grid-column:1/13">{feat_html}</div>'
        '<div class="kicker" style="grid-column:1/13;margin:8mm 0 3mm">Im Haus</div>'
        f'<dl class="spec spec-house" style="grid-column:1/13">{house_html}</dl>'),
        bottom_style="align-items:start")

    # 4 — Energie und Lage
    d.add(
        '<img class="bleed-top" src="assets/img/haus-detail.jpg" alt="" style="height:95mm">',
        content=(
        '<p class="caption" style="grid-column:1/13"><b>Außenansicht, obere Geschosse.</b> Visualisierung</p>'
        '<div class="kicker" style="grid-column:1/13;margin-top:10mm">Energie und Lage</div>'
        '<h1 class="display" style="grid-column:1/11;margin-top:5mm">Eigener Strom, kurze Wege</h1>'),
        content_style="top:98mm",
        bottom=(
        '<div style="grid-column:1/6">'
        '<h2 class="h2">Energie</h2>'
        '<p class="body" style="margin-top:3mm">Eine Photovoltaikanlage mit Speicher erzeugt Strom am Haus; '
        'die Mieterinnen und Mieter beziehen ihn über ein Mieterstrommodell.</p>'
        '<p class="body">Geheizt wird mit einer Luft-Wasser-Wärmepumpe, die Wärme über Fußbodenheizungen '
        'in allen Räumen abgibt. Wände und Dach sind überdurchschnittlich gut gedämmt.</p>'
        '<div style="margin-top:8mm">' + facts([
            ("Wärmeerzeugung", "Luft-Wasser-Wärmepumpe"),
            ("Wärmeverteilung", "Fußbodenheizung"),
            ("Strom", "Photovoltaik mit Speicher"),
            ("Versorgungsmodell", "Mieterstrom"),
        ]) + '</div></div>'
        '<div style="grid-column:7/13">'
        '<h2 class="h2">Lage</h2>'
        '<p class="body" style="margin-top:3mm">Das Haus steht auf einem großzügigen Grundstück in '
        'Innenstadtlage. Der rückwärtige Teil mit Garten liegt ruhig und naturnah.</p>'
        '<div style="margin-top:5mm;display:flex;align-items:flex-end;gap:4mm">'
        '<span class="num" style="font-family:NR Display;font-weight:300;font-size:60pt;line-height:46pt;color:var(--accent)">6</span>'
        '<span class="small" style="max-width:44mm">Minuten zu Fuß zu den Haltestellen des öffentlichen Nahverkehrs (ca.)</span></div>'
        '<div style="margin-top:8mm">' + facts([
            ("Haltestellen ÖPNV", "ca. 6 Min. zu Fuß"),
            ("Universität", "in unmittelbarer Nähe"),
            ("Autobahn", "in wenigen Minuten"),
        ]) + '</div></div>'),
        bottom_style="align-items:start")

    # Wohnungen
    for u in UNITS:
        n = u["n"]
        outdoor = (f'{u["outdoor"][0]}, {m2(u["outdoor"][1])}') if u["outdoor"] else "–"
        room_rows = "".join(f'<tr><td>{r}</td><td class="num">{m2(a)}</td></tr>' for r, a in u["rooms"])
        room_rows += f'<tr class="sum"><td>Wohnfläche</td><td class="num">{m2(u["area"])}</td></tr>'
        d.add(
            f'<img class="bleed-top" src="assets/img/w{n}-innen.jpg" alt="" style="height:140mm">',
            content=(
                f'<p class="caption" style="grid-column:1/13"><b>Wohnung {n}, {u["room_caption"]}.</b> '
                'Visualisierung – Einrichtung beispielhaft</p>'
                f'<div class="col-split" style="grid-column:1/6">'
                f'<div><div class="kicker">Wohnungen <span class="n">{n:02d} / 06</span></div>'
                f'<h1 class="display" style="margin-top:4mm">Wohnung {n}</h1>'
                f'<p class="lead" style="margin-top:2mm;color:var(--graphite)">{u["lead"]}</p></div>'
                f'<div class="body">{"".join(f"<p>{t}</p>" for t in u["text"])}</div></div>'
                f'<div class="col-split" style="grid-column:7/13">'
                f'<div style="padding-top:5mm">' + facts([
                    ("Wohnfläche", m2(u["area"]), True),
                    ("Kaltmiete", eur(u["rent"]), True),
                    ("Kaltmiete je m²", eur(u["sqm"])),
                    ("Freifläche", outdoor),
                    ("Geschoss", u["floor"]),
                    ("Bezugsfrei ab", MOVE_IN),
                ]) + '</div>'
                f'<div><div class="kicker" style="margin-bottom:2mm">Räume</div>'
                f'<table class="rooms">{room_rows}</table></div></div>'),
            content_style="top:143mm;grid-template-rows:auto 1fr;row-gap:9mm")

        for i, key in enumerate(u["plans"]):
            if i == 0:
                top = (f'<div style="grid-column:1/13;height:{u["luft_h"]}mm;display:flex;justify-content:center">'
                       f'<img src="assets/img/w{n}-luft.jpg" alt="" style="height:100%;width:auto;max-width:170mm;object-fit:contain"></div>'
                       f'<p class="caption" style="grid-column:1/13;margin-top:2mm"><b>Wohnung {n}, Luftansicht.</b> '
                       'Visualisierung – Einrichtung beispielhaft</p>')
                title = PLAN_TITLES.get(key, "Grundriss") + f" · Wohnung {n}"
            else:
                top = (f'<div style="grid-column:1/6"><div class="kicker">Wohnungen <span class="n">{n:02d} / 06</span></div>'
                       f'<h1 class="display" style="margin-top:4mm">Obere Ebene</h1></div>'
                       f'<p class="body" style="grid-column:7/13;margin-top:16mm">Auf der oberen Ebene liegen Schlafzimmer, '
                       f'begehbare Ankleide, Büro und Bad, dazu die Terrasse mit 7,29{NB}m². Die Treppe verbindet '
                       f'beide Ebenen innerhalb der Wohnung.</p>')
                title = PLAN_TITLES.get(key, "Grundriss") + f" · Wohnung {n}"
            d.add("", content=top, bottom=plan_section(key, title))

    # Konditionen und Kontakt
    cond_rows = "".join(
        f'<tr><td class="nr">{u["n"]}</td><td>{u["floor"].split(" (")[0]}</td>'
        f'<td class="r num">{m2(u["area"])}</td><td class="r num">{eur(u["rent"])}</td>'
        f'<td class="r num">{deposit(u["rent"])}</td></tr>' for u in UNITS)
    scale = "".join(f'<i class="{"on" if c == EFFICIENCY else ""}">{c}</i>'
                    for c in ["A+", "A", "B", "C", "D", "E", "F", "G", "H"])
    d.add("", content=(
        '<div class="kicker" style="grid-column:1/13">Konditionen und Kontakt</div>'
        '<h1 class="display" style="grid-column:1/8;margin-top:6mm">Konditionen</h1>'
        '<table class="overview" style="grid-column:1/13;margin-top:10mm"><thead><tr>'
        '<th style="width:12mm">Nr.</th><th>Geschoss</th><th class="r">Wohnfläche</th><th class="r">Kaltmiete</th>'
        '<th class="r">Kaution (3 Kaltmieten)</th></tr></thead>'
        f'<tbody>{cond_rows}</tbody></table>'
        '<div style="grid-column:1/6;margin-top:14mm">'
        '<h2 class="h2" style="margin-bottom:4mm">Mietbedingungen</h2>' + facts([
            ("Objekt", f"{ADDRESS},<br>{CITY}"),
            ("Bezugsfrei ab", f"{MOVE_IN}, Erstbezug"),
            ("Kaution", "drei Kaltmieten"),
            ("Nebenkosten", "auf Anfrage"),
            ("Stellplätze", "nach Absprache"),
        ]) + '</div>'
        '<div style="grid-column:7/13;margin-top:14mm">'
        '<h2 class="h2" style="margin-bottom:4mm">Energie</h2>' + facts([
            ("Energieausweis", "liegt noch nicht vor"),
            ("Art", "Bedarfsausweis, nach Fertigstellung"),
            ("Energieträger", "Strom, Luft-Wasser-Wärmepumpe"),
            ("Baujahr", "2027"),
        ]) +
        '<div class="kicker" style="margin-top:6mm">Effizienzklasse · Prognose</div>'
        f'<div class="eff">{scale}</div>'
        '<p class="small" style="margin-top:2.5mm">Erwartete Klasse auf Basis der Planung (Neubau, Wärmepumpe, '
        'Photovoltaik, hoher Dämmstandard). Verbindlich sind die Werte des Energieausweises, der nach '
        'Fertigstellung vorliegt.</p></div>'),
        bottom=(
        '<div style="grid-column:1/6">'
        '<div class="kicker">Ihr Ansprechpartner</div>'
        f'<p class="display" style="font-size:24pt;line-height:28pt;margin-top:3mm">{CONTACT["name"]}</p></div>'
        '<div class="contact" style="grid-column:7/13">'
        f'<a href="tel:{CONTACT["tel"]}">Telefon {CONTACT["phone"].replace(" ", NB)}</a>'
        f'<a href="mailto:{CONTACT["mail"]}">{CONTACT["mail"]}</a></div>'
        '<div class="rule" style="grid-column:1/13;margin:10mm 0 4mm"></div>'
        '<p class="small" style="grid-column:1/10">Alle Visualisierungen und Grundrisse zeigen '
        'Einrichtungsbeispiele. Flächen laut Planung, Balkon und Terrassen in der Wohnfläche enthalten; '
        'Abweichungen in der Ausführung möglich. Dieses Exposé ist kein Vertragsangebot.</p>'))

    head = ('<!doctype html><html lang="de"><head><meta charset="utf-8">'
            f'<title>Exposé {ADDRESS}</title><link rel="stylesheet" href="expose.css"></head><body>')
    (ROOT / "expose.html").write_text(head + "\n".join(d.pages) + "</body></html>")
    print(f"{len(d.pages)} Seiten, Wohnungen ab Seite {unit_pages}")


def detail_crop():
    from PIL import Image
    im = Image.open(ROOT.parent / "renderings" / "fotorealistisch" / "auswahl" / "Wohnung 1 Innenansicht.jpg")
    w, h = im.size
    cw = round(h * 4 / 5)
    x = w - cw - 40
    im.crop((x, 0, x + cw, h)).save(ROOT / "assets" / "img" / "detail-kueche.jpg", quality=93, subsampling=0)


def render():
    js = ROOT / "render.js"
    subprocess.run(["node", str(js)], check=True)


if __name__ == "__main__":
    detail_crop()
    build()
    render()
