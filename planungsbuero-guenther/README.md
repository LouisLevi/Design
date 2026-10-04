# Planungsbüro Günther – Website

Neu aufgebaute Website im Design „Kontaktabzug“ (Entwurf B2 in `entwurf/`).
Statisches HTML, CSS und JavaScript, ohne Frameworks. Die Seiten werden mit
einem kleinen Python-Skript aus den Quellen in `_src/` erzeugt.

```bash
python3 _src/build.py            # Seiten neu erzeugen
python3 -m http.server 8000      # Vorschau: http://localhost:8000
```

## Seiten und Adressen

Die Adressen entsprechen der bisherigen Website, damit Links und Google-Treffer weiter funktionieren.

| Adresse | Inhalt |
| --- | --- |
| `/` | Start: Logo-Schriftzug, Bauaufgaben als Bildleiste, 5 Schritte zum Haus, Filme |
| `/portfolio/` | Werkverzeichnis aller 59 Projekte mit Filter |
| `/aktuelle-projekte/`, `/einfamilienhäuser/`, `/mehrfamilienhäuser/`, `/gewerbe-sonstige-bauwerke/`, `/projektentwicklungen/` | Projekte je Bauaufgabe; Klick öffnet Bilder, Film und Eckdaten |
| `/videos/` | alle 7 Filme |
| `/leistungen/` | sechs Leistungsfelder, Leistungsphasen der HOAI |
| `/team/`, `/vita/` | Team (unverändert übernommen), Lebenslauf Carsten Günther |
| `/karriere/` | Bauzeichner:in, Praktikant:in |
| `/kontakt/` | Kontaktdaten, Bürozeiten, Anfrageformular |
| `/impressum/`, `/datenschutzerklaerung/` | Rechtstexte |

Ein Projekt lässt sich direkt verlinken: `/einfamilienhäuser/#<slug>` öffnet die Projektansicht.

## Ordner

```
_src/build.py          Generator (Kopf, Fuß, Navigation, Bausteine)
_src/projekte.json     alle Projekte – Reihenfolge = Reihenfolge auf der Website
_src/seiten/*.html     Inhalte der einzelnen Seiten (Platzhalter wie {{schritte}})
assets/css/site.css    Designsystem
assets/js/site.js      Menü, 5 Schritte, Filme, Projektansicht, Filter, Formular
assets/js/projekte.js  wird vom Generator erzeugt – nicht von Hand ändern
assets/img, assets/video, assets/fonts
entwurf/               Designentwürfe (gehören nicht zur Website)
```

Nach jeder Änderung in `_src/` einmal `python3 _src/build.py` ausführen.

## Bilder nachliefern

Diese Dateien werden automatisch eingebunden, sobald sie vorhanden sind (dann neu bauen):

| Datei | Wofür |
| --- | --- |
| `assets/img/site/logo.svg` | Original-Logo, helle Fassung für dunklen Hintergrund (ersetzt den Nachbau) |
| `assets/img/site/schritt-1.webp` | Schritt 1 „Kennenlernen & Beratung“, Querformat, ca. 1600 × 1000 px |
| `assets/img/site/schritt-3.webp` | Schritt 3 „Bauantrag & Genehmigung“, Querformat, ca. 1600 × 1000 px |

Fotos umwandeln (ImageMagick):

```bash
convert foto.jpg -resize 1600x -quality 82 assets/img/site/schritt-1.webp
# Projektbild: volle Größe + Vorschau
convert foto.jpg -resize 1600x -quality 82 assets/img/p/<name>.webp
convert foto.jpg -resize 760x  -quality 80 assets/img/p/<name>-s.webp
```

Neue Projektbilder in `_src/projekte.json` beim Projekt unter `img` eintragen: `["<name>", Breite, Höhe]`.

## Projekte pflegen

Ein Eintrag in `_src/projekte.json`:

```json
{"id": "PG-060", "slug": "neubau-xyz-kassel", "cat": "efh", "title": "Neubau …", "ort": "Kassel",
 "jahr": 2026, "status": "geplant", "lph": "LPH 1–9", "volumen": 500000,
 "img": [["neubau-xyz-kassel-1", 1600, 1200]], "film": "film-…"}
```

`cat`: `aktuell`, `efh`, `mfh`, `gewerbe`, `entwicklung`. Projektentwicklungen nutzen statt `volumen` das Feld `grundstueck`.
Zahlen auf Startseite und in der Navigation zählen sich automatisch.

## Kontaktformular

Ohne Formulardienst öffnet „Absenden“ das E-Mail-Programm mit vorbereiteter Nachricht.
Für den direkten Versand in `_src/seiten/kontakt.html` beim Formular `data-endpoint="…"` mit der
Adresse des Formulardienstes eintragen (Versand als JSON per POST) und die Datenschutzerklärung ergänzen.

## Technik und Datenschutz

- Keine Cookies, kein Tracking, keine eingebetteten Fremddienste. Schriften (Inter, Archivo; SIL Open Font License) liegen lokal.
- `prefers-reduced-motion` wird beachtet; Filme starten erst auf Klick.
- `sitemap.xml`, `robots.txt` und `404.html` werden mitgebaut.

## Vor dem Livegang

1. Hosting festlegen und in der Datenschutzerklärung eintragen (markierte Stellen: Anbieter, Löschfrist der Logfiles).
2. Impressum prüfen: Inhalte stammen von der bisherigen Seite; Rechtsgrundlage auf DDG aktualisiert, Hinweis auf die
   abgeschaltete EU-Streitschlichtungsplattform entfernt, Anschrift der Architektenkammer ergänzt.
3. Bilder für Schritt 1 und 3 sowie Original-Logo einsetzen (siehe oben).
4. Formulardienst anbinden (optional, siehe oben).
