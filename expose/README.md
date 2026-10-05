# Exposé Altenbaunaer Straße 26

`Expose_Altenbaunaer_Strasse_26.pdf`: 18 Seiten A4 für alle sechs Wohnungen.

Neu erzeugen:

```bash
pip install pymupdf pillow fonttools
python3 expose/build.py            # schreibt expose.html und rendert das PDF (Playwright/Chromium)
```

- Texte und Daten stehen in `build.py` (Liste `UNITS`), Gestaltung in `expose.css`.
- `prepare_assets.py <alte-mappe.pdf>` hat Titelbild und Grundrisse aus der alten Mappe gezogen
  (Grundrisse ohne Text, Raumnamen werden neu gesetzt). Nur nötig, wenn sich die Pläne ändern.
- Bilder: `renderings/fotorealistisch/auswahl/` (Innenansicht 3:2 beschnitten, Luftansicht freigestellt).
- Schriften: Newsreader und IBM Plex Sans (SIL Open Font License), als statische Schnitte eingebettet.
- Offene Angaben werden mit `missing()` rot als `[FEHLT: …]` markiert (aktuell keine). Nebenkosten stehen bewusst auf „auf Anfrage“; die Effizienzklasse A+ ist als Prognose gekennzeichnet, bis der Energieausweis vorliegt.
