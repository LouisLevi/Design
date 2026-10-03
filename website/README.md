# Planungsbüro Günther – Website-Entwurf

Statische Seite, kein Build nötig: `index.html` im Browser öffnen.

## Bilder von der bestehenden Website übernehmen

```bash
cd website
python3 scripts/fetch_images.py
```

Das Skript crawlt www.planungsbuero-guenther.de, lädt alle Fotos in der größten
verfügbaren Auflösung nach `images/` und schreibt `images/manifest.js`.
Die Seite verteilt sie danach automatisch: größtes Foto → Titelbild,
Bild mit „Vita/Carsten“ im Namen/Alt-Text → Porträt, Rest → Projekte und Bürostreifen.
Ohne Bilder zeigt die Seite gezeichnete Fassaden als Platzhalter.

`images/` steht in `.gitignore` – die Fotos sind urheberrechtlich geschützt
und nur für den privaten Entwurf gedacht.

## Inhalte anpassen

Alles in `assets/content.js`: Projekte (**derzeit Platzhalter**), Kategorien,
Leistungsphasen. Ein festes Bild pro Projekt über `image: "images/datei.jpg"`.
