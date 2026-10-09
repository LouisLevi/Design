#!/usr/bin/env python3
"""Baut die statische Website des Planungsbüro Günther.

Aufruf (im Ordner planungsbuero-guenther):  python3 _src/build.py

Quellen:
  _src/projekte.json   alle Projekte (Reihenfolge = Reihenfolge auf der Website)
  _src/seiten/*.html   Inhalte der einzelnen Seiten mit Platzhaltern wie {{schritte}}
Ergebnis: index.html und je ein Ordner pro Seite (gleiche Adressen wie die bisherige Website).

Bilder, die noch nachgeliefert werden, erscheinen automatisch, sobald die Datei
unter dem erwarteten Namen liegt (siehe BILDER unten) – danach einfach neu bauen.
"""
import datetime
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
DOMAIN = "https://www.planungsbuero-guenther.de"
YEAR = datetime.date.today().year

PROJECTS = json.load(open(os.path.join(SRC, "projekte.json"), encoding="utf-8"))
BY_ID = {p["id"]: p for p in PROJECTS}


def projekt(title, ort):
    """Projekt eindeutig über Titel und Bauort finden (bricht ab, wenn es nicht genau eines gibt)."""
    hits = [p for p in PROJECTS if p["title"] == title and p["ort"] == ort]
    if len(hits) != 1:
        raise SystemExit(f"Projekt nicht eindeutig: {title} / {ort} ({len(hits)} Treffer)")
    return hits[0]


def projektbild(title, ort, n=1, vorschau=False):
    name = projekt(title, ort)["img"][n - 1][0]
    return f"assets/img/p/{name}{'-s' if vorschau else ''}.webp"

# Bauaufgaben – Pfad entspricht der bisherigen Adresse
CATS = [
    dict(key="aktuell", path="aktuelle-projekte", name="Aktuelle Projekte", disp="aktuelle projekte", v="aktuelle projekte",
         intro="In Planung, im Bau und gerade fertiggestellt.", img="assets/video/film-soehrewald.webp", note="Wohnanlage Söhrewald · in Planung"),
    dict(key="efh", path="einfamilienhäuser", name="Einfamilienhäuser", disp="einfamilien&shy;häuser", v="einfamilien&shy;häuser",
         intro="Neubau, Umbau, Erweiterung und Sanierung.", img=projektbild("Neubau eines modernen Einfamilienhauses", "Kassel", 1, True), note="Modernes Einfamilienhaus, Kassel"),
    dict(key="mfh", path="mehrfamilienhäuser", name="Mehrfamilienhäuser", disp="mehrfamilien&shy;häuser", v="mehrfamilien&shy;häuser",
         intro="Neubau, Umbau, Erweiterung und Sanierung.", img=projektbild("Neubau von zwei Mehrfamilienhäusern (30 WE)", "Kaufungen", 1, True), note="Zwei Mehrfamilienhäuser (30 WE), Kaufungen"),
    dict(key="gewerbe", path="gewerbe-sonstige-bauwerke", name="Gewerbe & Sonstige Bauwerke", disp="gewerbe &amp; sonstige bauwerke", v="gewerbe &amp; sonstige",
         intro="Gewerbe, Verwaltung, Umnutzung und Bauen im Bestand.", img=projektbild("Neubau Polizeirevier Süd-West (Baunatal)", "Baunatal", 1, True), note="Polizeirevier Süd-West, Baunatal"),
    dict(key="entwicklung", path="projektentwicklungen", name="Projektentwicklungen", disp="projekt&shy;entwicklungen", v="projekt&shy;entwicklungen",
         intro="Aus Grundstücken werden realisierbare Projekte.", img="assets/video/film-kita-kassel.webp", note="Wohn- und Geschäftshaus mit Kita, Kassel"),
]
CAT = {c["key"]: c for c in CATS}
for c in CATS:
    c["count"] = sum(1 for p in PROJECTS if p["cat"] == c["key"])

# Filme (Reihenfolge wie auf der Seite „Videos“)
# Titel wie auf der Seite „Videos“ der bisherigen Website; Ort aus den Projektdaten
FILMS = [
    ("film-soehrewald", "Wohnanlage Söhrewald", "3D-Visualisierung"),
    ("film-salamander-areal", "Entwicklung eines Areals mit Kindergarten, Parkhaus, Boardinghaus, Neubau von Mehrfamilienhäusern und Sanierung eines Fabrikgebäudes zu Loftwohnungen", "3D-Visualisierung"),
    ("film-kita-kassel", "Neubau eines Wohn- u. Geschäftshauses mit Kindertagesstätte", "3D-Visualisierung"),
    ("film-kassel-25we", "Neubau eines 25-Familienhauses", "3D-Visualisierung"),
    ("film-hochhaus-kassel", "Teilsanierung eines Hochhauses", "Drohnenflug"),
    ("film-pultdachhaus", "Bau eines Pultdachhauses in Holzständerbauweise", "Holzständerbau"),
    ("film-satteldachhaus", "Bau eines Satteldachhauses in Holzständerbauweise", "Holzständerbau"),
]
FILM_PROJEKT = {p["film"]: p for p in PROJECTS if p.get("film")}
FILMS = [(k, t, f"{FILM_PROJEKT[k]['ort']} · {art}", FILM_PROJEKT[k]["id"]) for k, t, art in FILMS]
FILM = {f[0]: f for f in FILMS}

# Bilder, die nachgeliefert werden (Datei ablegen, neu bauen – fertig)
BILDER = {
    "logo": "assets/img/site/logo.svg",               # Original-Logo (weiße Fassung für dunklen Hintergrund)
    "schritt-1": "assets/img/site/schritt-1.webp",    # Erstgespräch / Beratung im Büro (Querformat)
    "schritt-3": "assets/img/site/schritt-3.webp",    # Pläne / Bauantrag (Querformat)
}

PAGES = [
    # Ausgabe, Navigation, Unterleiste, Titel, Beschreibung, Inhalt
    ("index.html", "home", "portfolio", "Architekt | Planungsbüro Günther | Kassel",
     "Planungsbüro Günther – Architekten & Ingenieure in Kassel. Alle Leistungsphasen der HOAI für Einfamilienhäuser, Mehrfamilienhäuser, Gewerbebauten und Projektentwicklungen.", "start.html"),
    ("portfolio/index.html", "portfolio", "portfolio", "Portfolio | Planungsbüro Günther",
     f"Alle {len(PROJECTS)} Projekte des Planungsbüro Günther: Einfamilienhäuser, Mehrfamilienhäuser, Gewerbe und Projektentwicklungen.", "portfolio.html"),
    *[(f"{c['path']}/index.html", "portfolio", c["key"], f"{c['name']} | Planungsbüro Günther",
       f"{c['name']} – {c['count']} Projekte des Planungsbüro Günther, Kassel. {c['intro']}", "kategorie.html") for c in CATS],
    ("videos/index.html", "portfolio", "videos", "Videos | Planungsbüro Günther",
     "Filme zu Projekten des Planungsbüro Günther: 3D-Visualisierungen, Drohnenflüge und Holzbau.", "videos.html"),
    ("leistungen/index.html", "leistungen", "portfolio", "Leistungen | Planungsbüro Günther",
     "Architektenleistungen in allen Phasen der HOAI, Aufmaß, Projektentwicklung, Projektsteuerung, Beratung und Immobilienmarketing.", "leistungen.html"),
    ("team/index.html", "team", "team", "Das Team | Planungsbüro Günther",
     "Das Team des Planungsbüro Günther: Architekten, Ingenieure und Werkstudenten unter der Leitung von Dipl.-Ing. Architekt Carsten Günther.", "team.html"),
    ("vita/index.html", "team", "vita", "Vita | Planungsbüro Günther",
     "Lebenslauf von Dipl.-Ing. Architekt Carsten Günther, Inhaber und Gründer des Planungsbüro Günther.", "vita.html"),
    ("karriere/index.html", "karriere", "karriere", "Karriere | Planungsbüro Günther",
     "Stellenangebote beim Planungsbüro Günther in Kassel: Bauzeichner:in und Praktikum.", "karriere.html"),
    ("kontakt/index.html", "kontakt", "portfolio", "Kontakt | Planungsbüro Günther",
     "Kontakt zum Planungsbüro Günther: Friedrich-Ebert-Straße 1, 34117 Kassel · +49 (0) 561 920 01877 · buero@planungsbuero-guenther.de", "kontakt.html"),
    ("impressum/index.html", "", "portfolio", "Impressum | Planungsbüro Günther", "Impressum des Planungsbüro Günther, Kassel.", "impressum.html"),
    ("datenschutzerklaerung/index.html", "", "portfolio", "Datenschutzerklärung | Planungsbüro Günther", "Datenschutzerklärung des Planungsbüro Günther, Kassel.", "datenschutz.html"),
    ("404.html", "", "portfolio", "Seite nicht gefunden | Planungsbüro Günther", "Diese Seite gibt es nicht (mehr).", "404.html"),
]

E = html.escape
AC = ' aria-current="page"'


# ---------------------------------------------------------------- Hilfen
def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def fmt_eur(v, ca=False):
    return ("ca. " if ca else "") + f"{v:,.0f} €".replace(",", ".") if v else "keine Angabe"


def img_p(name, w, h, alt, root, sizes="(max-width: 640px) 50vw, 25vw", eager=False):
    """Projektbild mit Vorschau (-s, 760 px) und voller Größe (1600 px)."""
    sw = 760 if w >= 760 else w
    sh = round(h * sw / w)
    load = "eager" if eager else "lazy"
    return (f'<img src="{root}assets/img/p/{name}-s.webp" srcset="{root}assets/img/p/{name}-s.webp {sw}w, {root}assets/img/p/{name}.webp {w}w" '
            f'sizes="{sizes}" width="{sw}" height="{sh}" alt="{E(alt)}" loading="{load}" decoding="async">')


def cover(p, root, sizes="(max-width: 640px) 50vw, 25vw"):
    alt = f"{p['title']}, {p['ort']}"
    if p["img"]:
        n, w, h = p["img"][0]
        return img_p(n, w, h, alt, root, sizes)
    return f'<img src="{root}assets/video/{p["film"]}.webp" width="1280" height="720" alt="{E(alt)}" loading="lazy" decoding="async">'


def bild(key, root, alt, label, cls=""):
    rel = BILDER[key]
    if exists(rel):
        return f'<img src="{root}{rel}" alt="{E(alt)}" class="{cls}" loading="lazy" decoding="async">'
    return f'<div class="ph">Foto folgt · {E(label)}</div>'


def logo(root, full=True):
    if exists(BILDER["logo"]):
        return f'<a class="logo" href="{root}" aria-label="planungsbüro günther – Startseite"><img src="{root}{BILDER["logo"]}" alt="planungsbüro günther – Architekten &amp; Ingenieure"></a>'
    if not full:
        return f'<a class="mini" href="{root}" aria-label="planungsbüro günther – Startseite"><span class="pg">pg</span><span>Architekten &amp; Ingenieure · Kassel</span></a>'
    return (f'<a class="logo" href="{root}" aria-label="planungsbüro günther – Architekten &amp; Ingenieure – Startseite">'
            '<span class="pg" aria-hidden="true">pg</span><span class="wm" aria-hidden="true"><span class="l1"><span>planungsbüro</span>günther</span>'
            '<span class="l2">Architekten &amp; Ingenieure</span></span></a>')


def link(root, path):
    return root + (path + "/" if path else "")


# ---------------------------------------------------------------- Bausteine
def header(root, nav, sub, home):
    items = [("home", "", "Home"), ("portfolio", "portfolio", "Portfolio"), ("leistungen", "leistungen", "Leistungen"),
             ("team", "team", "Team"), ("karriere", "karriere", "Karriere")]
    navhtml = "".join(f'<a href="{link(root, p)}"{AC if k == nav else ""}>{t}</a>' for k, p, t in items)
    navhtml += f'<a class="kontakt" href="{link(root, "kontakt")}"{AC if nav == "kontakt" else ""}>Kontakt</a>'

    if sub in ("team", "vita", "karriere"):
        bar = [("", "team", "Über uns", ""), ("team", "team", "Das Team", ""), ("vita", "vita", "Vita", ""), ("karriere", "karriere", "Karriere", "2 offen")]
    else:
        bar = [("", "portfolio", "Portfolio", "")] + [(c["key"], c["path"], c["name"], str(c["count"])) for c in CATS] + [("videos", "videos", "Videos", str(len(FILMS)))]
    barhtml = "".join(f'<a href="{link(root, p)}"{AC if k and k == sub else ""}>{t}{f" <span>{n}</span>" if n else ""}</a>' for k, p, t, n in bar)

    mob = f'''<div class="mnav" id="mnav" role="dialog" aria-modal="true" aria-label="Menü">
  <div class="mnav-top">{logo(root)}<button class="menu-btn" type="button" data-close-menu>Schließen</button></div>
  <ul>
    <li><a href="{root}">Home</a></li>
    <li><a href="{link(root, 'portfolio')}">Portfolio</a><ul>{''.join(f'<li><a href="{link(root, c["path"])}">{c["name"]}</a></li>' for c in CATS)}<li><a href="{link(root, 'videos')}">Videos</a></li></ul></li>
    <li><a href="{link(root, 'leistungen')}">Leistungen</a></li>
    <li><a href="{link(root, 'team')}">Team</a><ul><li><a href="{link(root, 'team')}">Das Team</a></li><li><a href="{link(root, 'vita')}">Vita</a></li></ul></li>
    <li><a href="{link(root, 'karriere')}">Karriere</a></li>
    <li><a href="{link(root, 'kontakt')}">Kontakt</a></li>
  </ul>
  <div class="mnav-foot">Friedrich-Ebert-Straße 1, 34117 Kassel<br><a href="tel:+4956192001877">+49 (0) 561 920 01877</a><br><a href="mailto:buero@planungsbuero-guenther.de">buero@planungsbuero-guenther.de</a></div>
</div>'''
    return f'''<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="bar1"><div class="wrap">
  {logo(root, full=not home)}
  <nav class="nav" aria-label="Hauptnavigation">{navhtml}<button class="menu-btn" type="button" aria-controls="mnav" aria-expanded="false" data-open-menu><i aria-hidden="true"></i>Menü</button></nav>
</div></header>
<nav class="bar2" aria-label="{'Über uns' if sub in ('team', 'vita', 'karriere') else 'Portfolio'}"><div class="wrap">{barhtml}</div></nav>
{mob}'''


def footer(root):
    return f'''<footer>
  <div class="wrap">
    <div class="f-cta">
      <h2 class="disp"><span>sie planen</span><br><b>ein bauvorhaben?</b></h2>
      <div class="tel"><a href="tel:+4956192001877"><span class="cond">0561 920 01877</span></a><a href="mailto:buero@planungsbuero-guenther.de"><span class="link">buero@planungsbuero-guenther.de</span></a></div>
    </div>
    <div class="f-grid">
      <div class="f-col"><h4>Büro</h4>Planungsbüro Günther<br>Friedrich-Ebert-Straße 1<br>34117 Kassel<br>Mo–Fr 09:00–17:00</div>
      <div class="f-col"><h4>Portfolio</h4><ul>{''.join(f'<li><a href="{link(root, c["path"])}">{c["name"]}</a></li>' for c in CATS[:3])}</ul></div>
      <div class="f-col"><h4 aria-hidden="true">&nbsp;</h4><ul>{''.join(f'<li><a href="{link(root, c["path"])}">{c["name"]}</a></li>' for c in CATS[3:])}<li><a href="{link(root, 'videos')}">Videos</a></li></ul></div>
      <div class="f-col"><h4>Über uns</h4><ul><li><a href="{link(root, 'leistungen')}">Leistungen</a></li><li><a href="{link(root, 'team')}">Team</a></li><li><a href="{link(root, 'vita')}">Vita</a></li><li><a href="{link(root, 'karriere')}">Karriere</a></li><li><a href="https://www.instagram.com/planungsbuero_guenther/" rel="noopener" target="_blank">Instagram ↗</a></li></ul></div>
    </div>
  </div>
  <div class="f-end"><div class="wrap"><a class="mini" href="{root}" aria-label="Startseite"><span class="pg" aria-hidden="true">pg</span><span>© {YEAR} Planungsbüro Günther</span></a>
    <nav aria-label="Rechtliches"><a href="{link(root, 'impressum')}">Impressum</a><a href="{link(root, 'datenschutzerklaerung')}">Datenschutzerklärung</a></nav></div></div>
</footer>'''


def strip(root):
    out = []
    for i, c in enumerate(CATS):
        out.append(f'''<a href="{link(root, c['path'])}"{' class="on"' if i == 0 else ''}>
        <img src="{root}{c['img']}" alt="" loading="{'eager' if i == 0 else 'lazy'}" decoding="async">
        <span class="cnt cond" aria-hidden="true">{c['count']}</span>
        <span class="v" aria-hidden="true">{c['v']}</span>
        <span class="cap"><span class="disp"><b>{c['disp']}</b></span><small>{E(c['note'])} · {c['count']} Projekte</small></span>
        <span class="sr">{c['name']}, {c['count']} Projekte</span></a>''')
    return f'<div class="strip">{"".join(out)}</div>'


STEPS = [
    ("kennenlernen &amp; beratung", "Wünsche, Grundstück, Budget: Wir klären, was möglich ist.", "LPH 1", "Grundlagenermittlung",
     ("bild", "schritt-1", "Dipl.-Ing. Architekt Carsten Günther", "Erstgespräch"), "Ihr Ansprechpartner · Carsten Günther"),
    ("entwurf &amp; visualisierung", "Ihr Haus in Skizze und 3D – bevor gebaut wird.", "LPH 2–3", "Vor- und Entwurfsplanung",
     ("img", "assets/video/film-kassel-25we.webp", "3D-Visualisierung des Wohnhauses mit 25 WE in Kassel"), "3D-Visualisierung · Wohnhaus Kassel"),
    ("bauantrag &amp; genehmigung", "Alle Unterlagen, alle Abstimmungen mit dem Bauamt.", "LPH 4", "Genehmigungsplanung",
     ("bild", "schritt-3", "Grundriss 1. Obergeschoss der Wohnanlage Söhrewald", "Pläne / Bauantrag"), "Grundriss 1. OG · Wohnanlage Söhrewald"),
    ("ausführung &amp; vergabe", "Werkpläne, Ausschreibung, geprüfte Angebote.", "LPH 5–7", "Ausführung, Vergabe",
     ("img", projektbild("Neubau eines modernen Einfamilienhauses", "Kassel"), "Modernes Einfamilienhaus in Kassel"), "Modernes Einfamilienhaus · Kassel"),
    ("bau &amp; übergabe", "Bauüberwachung bis zur Schlüsselübergabe.", "LPH 8–9", "Objektüberwachung",
     ("img", projektbild("Umbau und Sanierung einer ehemaligen Kaserne zu einer Wohnanlage (51 WE)", "Kassel"), "Umbau einer ehemaligen Kaserne zur Wohnanlage mit 51 WE in Kassel"), "Ehemalige Kaserne, 51 WE · Kassel"),
]


def steps(root):
    out = []
    for i, (t, p, lph, lphname, media, cap) in enumerate(STEPS, 1):
        if media[0] == "bild":
            fig = bild(media[1], root, media[2], media[3])
        else:
            fig = f'<img src="{root}{media[1]}" alt="{E(media[2])}" loading="lazy" decoding="async">'
        capt = f'<span class="label">{cap}</span>' if cap else ""
        out.append(f'''<li class="st{' on' if i == 1 else ''}"><div class="num cond" aria-hidden="true">{i}</div>
      <div class="txt"><h3><span class="sr">Schritt {i}: </span>{t}</h3><p>{p}</p><div class="lph"><span class="label">{lph}</span>{lphname}</div></div>
      <figure>{fig}{capt}</figure></li>''')
    return f'<ol class="steps" role="list" style="list-style:none;margin:0;padding:0">{"".join(out)}</ol>'


def film_button(root, key, cls="film"):
    f = FILM[key]
    title, sub = f[1], f[2]
    short = {"film-salamander-areal": "areal stuttgart", "film-kita-kassel": "wohn- und geschäftshaus mit kita", "film-kassel-25we": "wohnhaus, 25 we",
             "film-hochhaus-kassel": "hochhaus kassel", "film-pultdachhaus": "pultdachhaus", "film-satteldachhaus": "satteldachhaus",
             "film-soehrewald": "wohnanlage söhrewald"}[key]
    return (f'<button class="{cls}" type="button" data-film="{root}assets/video/{key}.mp4" aria-label="Film abspielen: {E(title)}">'
            f'<img src="{root}assets/video/{key}.webp" alt="" loading="lazy" decoding="async"><span class="play" aria-hidden="true"><i></i></span>'
            f'<span class="cap" aria-hidden="true"><b>{short}</b><span>{E(sub)}</span></span></button>')


def films_home(root):
    return '<div class="films films--home">' + "".join(film_button(root, k) for k in ("film-hochhaus-kassel", "film-satteldachhaus", "film-kassel-25we")) + "</div>"


def films_all(root):
    out = []
    for key, title, sub, pid in FILMS:
        p = BY_ID[pid]
        c = CAT[p["cat"]]
        out.append(f'''<div>{film_button(root, key)}
      <div class="film-meta"><b>{E(title)}</b><span>{E(sub)} · <a class="link" href="{link(root, c['path'])}#{p['slug']}">Zum Projekt</a></span></div></div>''')
    return f'<div class="vgrid">{"".join(out)}</div>'


def pcard(p, root, n):
    film = '<span class="label film-badge">Film</span>' if p.get("film") else ""
    year = p.get("jahr")
    meta = " · ".join(x for x in [p["ort"], (("geplant " if p.get("status") == "geplant" else "") + str(year)) if year else "", p.get("lph", "")] if x)
    return (f'<button class="pcard" type="button" data-slug="{p["slug"]}" aria-haspopup="dialog">'
            f'<figure>{cover(p, root)}<span class="n"><b>{n:02d}</b></span>{film}</figure>'
            f'<span class="t">{E(p["title"])}</span><span class="m">{E(meta)}</span></button>')


def grid(cat, root):
    items = [p for p in PROJECTS if p["cat"] == cat]
    return '<div class="pgrid">' + "".join(pcard(p, root, i) for i, p in enumerate(items, 1)) + "</div>"


def werkverzeichnis(root):
    tabs = [f'<button type="button" data-filter="alle" aria-pressed="true">Alle <span>{len(PROJECTS)}</span></button>']
    tabs += [f'<button type="button" data-filter="{c["key"]}" aria-pressed="false">{c["name"]} <span>{c["count"]}</span></button>' for c in CATS]
    rows = []
    for p in PROJECTS:
        year = p.get("jahr", "")
        if year and p.get("status") == "geplant":
            year = f"geplant {year}"
        thumb = cover(p, root, "64px")
        rows.append(f'<tr data-slug="{p["slug"]}" data-cat="{p["cat"]}" tabindex="0"><td>{p["id"][3:]}</td><td>{E(p["title"])}</td><td>{E(p["ort"])}</td>'
                    f'<td>{year}</td><td>{E(p.get("lph", "–"))}</td><td>{CAT[p["cat"]]["name"]}</td><td class="thumb">{thumb}</td></tr>')
    return (f'<div class="tabs" role="group" aria-label="Nach Bauaufgabe filtern">{"".join(tabs)}</div>'
            '<table class="ptable"><thead><tr><th>Nr.</th><th>Projekt</th><th>Ort</th><th>Jahr</th><th>Leistungen</th><th>Bauaufgabe</th><th class="thumb"><span class="sr">Bild</span></th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def phead_cat(c):
    return (f'<header class="phead wrap"><span class="label">Portfolio · {CATS.index(c) + 1:02d}</span>'
            f'<h1 class="disp"><span>portfolio</span><br><b>{c["disp"]}</b></h1>'
            f'<aside><span class="cond">{c["count"]}</span><small>Projekte · {E(c["intro"])}</small></aside></header>')


def projects_js():
    data = []
    for p in PROJECTS:
        d = {k: p[k] for k in ("slug", "title", "ort") if k in p}
        d["cat"] = CAT[p["cat"]]["name"]
        d["img"] = [[n, w, h] for n, w, h in p["img"]]
        if p.get("film"):
            d["film"] = p["film"]
        rows = [["Bauort", p["ort"]]]
        if p["cat"] == "entwicklung":
            y = p.get("jahr")
            rows.append(["Erstellungsjahr", (f"geplant {y}" if p.get("status") == "geplant" else str(y)) if y else "keine Angabe"])
            rows.append(["Grundstücksgröße", p.get("grundstueck", "keine Angabe")])
            rows.append(["Leistungen", p.get("lph", "keine Angabe")])
        else:
            rows.append(["Geplante Fertigstellung" if p.get("status") == "geplant" else "Fertigstellung", str(p.get("jahr", "keine Angabe"))])
            rows.append(["Leistungen", p.get("lph", "keine Angabe")])
            rows.append(["Bauvolumen", fmt_eur(p.get("volumen"), p.get("volumen_ca"))])
        d["rows"] = rows
        d["path"] = CAT[p["cat"]]["path"]
        data.append(d)
    js = "/* Automatisch erzeugt von _src/build.py – bitte nicht von Hand ändern. */\nwindow.PG_PROJEKTE = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open(os.path.join(ROOT, "assets/js/projekte.js"), "w", encoding="utf-8") as f:
        f.write(js)


# ---------------------------------------------------------------- Seiten
def render(out, nav, sub, title, desc, body_file, cat=None):
    depth = out.count("/")
    root = "../" * depth
    if out == "404.html":
        root = "/"  # 404 wird unter beliebiger Adresse ausgeliefert
    body = open(os.path.join(SRC, "seiten", body_file), encoding="utf-8").read()

    def tok(m):
        name, arg = m.group(1), m.group(2)
        if name == "root":
            return root
        if name == "link":
            return link(root, arg)
        if name == "strip":
            return strip(root)
        if name == "schritte":
            return steps(root)
        if name == "filme_start":
            return films_home(root)
        if name == "filme_alle":
            return films_all(root)
        if name == "anzahl":
            return str(len(PROJECTS)) if arg == "alle" else str(CAT[arg]["count"])
        if name == "kopf_kategorie":
            return phead_cat(cat)
        if name == "raster":
            return grid(cat["key"], root)
        if name == "werkverzeichnis":
            return werkverzeichnis(root)
        if name == "jahr":
            return str(YEAR)
        raise KeyError(f"Unbekannter Platzhalter {{{{{name}}}}} in {body_file}")

    body = re.sub(r"\{\{(\w+)(?::([^}]*))?\}\}", tok, body)
    canonical = DOMAIN + "/" + (out[:-len("index.html")] if out.endswith("index.html") else out)
    page = f'''<!doctype html>
<html lang="de" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#00020a">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Planungsbüro Günther">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{DOMAIN}/assets/video/film-soehrewald.webp">
<link rel="icon" href="{root}assets/img/site/icon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{root}assets/img/site/icon-180.png">
<link rel="preload" href="{root}assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/css/site.css">
</head>
<body>
{header(root, nav, sub, home=(out == "index.html"))}
<main id="inhalt">
{body}
</main>
{footer(root)}
<script src="{root}assets/js/projekte.js" defer></script>
<script src="{root}assets/js/site.js" defer></script>
</body>
</html>
'''
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    return canonical


def main():
    os.makedirs(os.path.join(ROOT, "assets/js"), exist_ok=True)
    projects_js()
    urls = []
    for out, nav, sub, title, desc, body in PAGES:
        cat = CAT.get(sub) if body == "kategorie.html" else None
        url = render(out, nav, sub, title, desc, body, cat)
        if out != "404.html":
            urls.append(url)
    today = datetime.date.today().isoformat()
    sm = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nDisallow: /_src/\nDisallow: /entwurf/\nSitemap: {DOMAIN}/sitemap.xml\n")
    missing = [k for k, v in BILDER.items() if not exists(v)]
    print(f"{len(PAGES)} Seiten gebaut.", f"Noch fehlende Bilder: {', '.join(missing)}" if missing else "Alle Bilder vorhanden.")


if __name__ == "__main__":
    main()
