# Exposé Altenbaunaer Straße 26

`Expose_Altenbaunaer_Strasse_26.pdf` (hell) und `Expose_Altenbaunaer_Strasse_26_dunkel.pdf`: je 15 Seiten A4
für die fünf Mietwohnungen (Erdgeschoss, Erdgeschoss in Richtung Garten, 1. OG, 2. OG, Untergeschoss).
Die frühere Wohnung 3 wird nicht vermietet und ist nicht mehr enthalten.

Neu erzeugen:

```bash
pip install pymupdf pillow fonttools
python3 expose/build.py            # schreibt expose.html / expose-dunkel.html und rendert beide PDFs
```

- Texte und Daten stehen in `build.py` (Liste `UNITS`), Gestaltung in `expose.css`.
- `prepare_assets.py <alte-mappe.pdf>` hat Titelbild und Grundrisse aus der alten Mappe gezogen
  (Grundrisse ohne Text, Raumnamen werden neu gesetzt). Nur nötig, wenn sich die Pläne ändern.
- Bilder: `renderings/fotorealistisch/auswahl/` (Innenansicht 3:2 beschnitten, Luftansicht freigestellt).
- Schriften: Newsreader und IBM Plex Sans (SIL Open Font License), als statische Schnitte eingebettet.
- Offene Angaben werden mit `missing()` rot als `[FEHLT: …]` markiert (aktuell keine). Nebenkosten stehen bewusst auf „auf Anfrage“; die Effizienzklasse A+ ist als Prognose gekennzeichnet, bis der Energieausweis vorliegt.
- Dunkle Variante: gleiche Seiten mit `body.dark` (Farben in `expose.css`). Luftansichten werden dafür
  freigestellt und auf die Papierfarbe gerechnet, Grundrisse hell auf dunkel (`prepare_dark()`).
