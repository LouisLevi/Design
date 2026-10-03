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

## Technik & Datenschutz

- Schriften (Archivo, IBM Plex Sans/Mono, SIL Open Font License) sind lokal eingebunden – kein Abruf bei Google Fonts.
- Keine Cookies, kein Tracking, keine eingebetteten Fremddienste (Karten und Instagram nur als Links).
- Hell-/Dunkelmodus folgt der Systemeinstellung; `prefers-reduced-motion` wird respektiert (Hero-Film startet dann nicht automatisch).
- Das Formular öffnet das E-Mail-Programm mit vorbereiteter Anfrage (`mailto:`), da die Seite ohne Server-Backend auskommt. Für einen direkten Versand kann später ein Formular-Endpunkt des Hosters angebunden werden (`assets/js/main.js`, Abschnitt „Kontakt“).
- Lokale Vorschau: `python3 -m http.server` in diesem Ordner, dann http://localhost:8000.

## Vor dem Livegang zu klären

1. **Impressum:** Mitgliedsnummer der Architektenkammer, USt-IdNr., Berufshaftpflichtversicherung (Platzhalter sind markiert).
2. **Datenschutz:** Hosting-Anbieter, Löschfrist der Server-Logfiles, Datum „Stand“.
3. **Bildrechte** für Fotos, Visualisierungen und Filme bestätigen (inkl. Drohnenaufnahme Hochhaus).
4. **Bildzuordnung prüfen** bei: Neubau 3-Familienhaus Vellmar, Neubau 4-Familienhaus mit Büroeinheit Butzbach, Erweiterung Bürogebäude Kassel, Fitnesscenter Kassel, Doppelhaushälften Kassel, Wohnanlage mit Shopping-Mall Österreich (auf der alten Seite nicht eindeutig zugeordnet).
5. Auf der alten Seite war das Projekt Habichtswald/Ehlen doppelt gelistet; es ist jetzt ein Eintrag („Habichtswald-Ehlen“).
6. Neu formulierte Texte freigeben lassen: Hero-Claim, Abschnitt „Digitaler Workflow“, Stichpunkte in den Leistungen, Beschreibungen der HOAI-Phasen.
