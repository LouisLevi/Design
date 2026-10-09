# Planungsbüro Günther – neue Website

Statische Website (HTML, CSS, JavaScript ohne Frameworks und ohne Build-Schritt).
Inhalte, Fotos und Filme stammen von der bisherigen Website planungsbuero-guenther.de.

## Seiten

| Datei | Inhalt |
| --- | --- |
| `index.html` | Start: Hero mit Film, Kennzahlen, Leistungen, ausgewählte Projekte, digitaler Workflow mit Filmen, Büro |
| `projekte.html` | Projektdatenbank: 59 Referenzen, Filter nach Kategorie, Suche, Sortierung, Raster-/Listenansicht, Detailansicht mit Galerie und Film |
| `leistungen.html` | Sechs Leistungsfelder und interaktiver Explorer der HOAI-Leistungsphasen 1–9 |
| `buero.html` | Vita Carsten Günther und Team mit Durchwahlen |
| `karriere.html` | Stellenangebote (Bauzeichner:in, Praktikum) |
| `kontakt.html` | Kontaktdaten, Bürozeiten mit Live-Status, Projektanfrage-Formular |
| `impressum.html`, `datenschutz.html` | Rechtstexte (Platzhalter siehe unten) |

Ein Projekt lässt sich direkt verlinken: `projekte.html#<slug>` öffnet die Detailansicht,
`projekte.html#efh` filtert auf eine Kategorie (`aktuell`, `efh`, `mfh`, `gewerbe`, `entwicklung`).

## Projekte pflegen

Alle Projekte stehen in `assets/js/projects.js` (ein Eintrag pro Projekt):

```js
{"id": "PG-001", "slug": "…", "cat": "aktuell", "title": "…", "ort": "Söhrewald",
 "jahr": 2027, "status": "geplant", "lph": "LPH 1–9", "volumen": 12000000,
 "img": [["dateiname", 1600, 900]], "film": "film-soehrewald", "featured": 0}
```

- Bilder liegen in `assets/img/p/` als `<name>.webp` (max. 1600 px) und `<name>-s.webp` (Vorschau, 760 px).
- Filme liegen in `assets/video/` als `.mp4` (H.264, „faststart“) mit gleichnamigem `.webp`-Poster.
- `featured` (0–4) legt Reihenfolge der fünf Projekte auf der Startseite fest.
- Kennzahlen auf der Startseite (Anzahl Referenzen, Bauvolumen) sind fest im HTML eingetragen und bei neuen Projekten anzupassen.

## Hosting (Hetzner Webhosting S)

- `.htaccess`: erzwingt HTTPS und www, leitet die alten Wix-Adressen (`/kontakt`, `/team`, `/einfamilienhäuser` …) per 301 auf die neuen Seiten um, setzt Cache- und Sicherheits-Header.
- `404.html`, `sitemap.xml`, `robots.txt` liegen im Hauptverzeichnis.
- Hochladen: alles in diesem Ordner außer `README.md` in das Web-Verzeichnis (`public_html`).

## Technik & Datenschutz

- Schriften (Archivo, IBM Plex Sans/Mono, SIL Open Font License) sind lokal eingebunden – kein Abruf bei Google Fonts.
- Keine Cookies, kein Tracking, keine eingebetteten Fremddienste (Karten und Instagram nur als Links).
- Hell-/Dunkelmodus folgt der Systemeinstellung; `prefers-reduced-motion` wird respektiert (Hero-Film startet dann nicht automatisch).
- Das Formular öffnet das E-Mail-Programm mit vorbereiteter Anfrage (`mailto:`), da die Seite ohne Server-Backend auskommt. Für einen direkten Versand kann später ein Formular-Endpunkt des Hosters angebunden werden (`assets/js/main.js`, Abschnitt „Kontakt“).
- Lokale Vorschau: `python3 -m http.server` in diesem Ordner, dann http://localhost:8000.

## Vor dem Livegang zu klären

1. Impressum (Daten der alten Seite) und Datenschutz (Hetzner, Stand Oktober 2026) sind vollständig.
2. **Bildrechte** für Fotos, Visualisierungen und Filme bestätigen (inkl. Drohnenaufnahme Hochhaus).
3. **Bildzuordnung prüfen** bei: Neubau 3-Familienhaus Vellmar, Neubau 4-Familienhaus mit Büroeinheit Butzbach, Erweiterung Bürogebäude Kassel, Fitnesscenter Kassel, Doppelhaushälften Kassel, Wohnanlage mit Shopping-Mall Österreich (auf der alten Seite nicht eindeutig zugeordnet).
4. Auf der alten Seite war das Projekt Habichtswald/Ehlen doppelt gelistet; es ist jetzt ein Eintrag („Habichtswald-Ehlen“).
5. Neu formulierte Texte freigeben lassen: Hero-Claim, Abschnitt „Digitaler Workflow“, Stichpunkte in den Leistungen, Beschreibungen der HOAI-Phasen.

## Nach dem Livegang: IONOS-Kosten senken

Bei IONOS werden monatlich 65,40 € für „Webhosting Pro“ abgebucht (Stand Oktober 2026). Die Website lief nie dort (vorher Wix, jetzt Hetzner), der Vertrag trägt aber die **Domain** planungsbuero-guenther.de und die **E-Mail-Postfächer** (MX: mx00/mx01.ionos.de). Deshalb **nicht einfach kündigen**.

Vorgehen, sobald die neue Seite stabil mit HTTPS läuft:
1. IONOS „Verträge & Abos“ prüfen: Inhalt von Webhosting Pro (Domains, Postfächer, Speicher), weitere Verträge, Laufzeit und Kündigungsfrist.
2. Entscheiden:
   - A) Bei IONOS auf einen reinen Domain- und E-Mail-Tarif wechseln (meist unter 10 €/Monat).
   - B) Domain und Postfächer zu Hetzner umziehen (Webhosting S enthält E-Mail, .de-Domain wenige €/Jahr). Postfach-Umzug sorgfältig planen, damit keine Mail verloren geht.
3. Danach das Wix-Abo kündigen.
