# Fotorealistische Renderings – Prompts

Alle 53 Bilder aus `original/` werden mit Nano Banana Pro (`gemini-3-pro-image-preview`,
`image_size: 2K`) bearbeitet und danach mit `finalize.py` auf 1080p gebracht
(16:9 → 1920×1080, 4:3 → 1440×1080). Ergebnis: `fotorealistisch/`, gleiche Ordnerstruktur, PNG→JPG.

Der Lichtblock ist in beiden Prompts wortgleich – das sorgt für das einheitliche Licht über die Serie.

## Innenansichten (`*/Innenansichten/*.jpg`)

```
Turn this 3D interior rendering into a photorealistic architectural interior photograph, as if shot with a full-frame camera and a 24mm tilt-shift lens for a real-estate exposé.

Keep EXACTLY the same camera angle, framing, room geometry, walls, windows, floor, and every piece of furniture and decor in the same position, shape, color and material. Do not add, remove or move any objects. Keep the view outside the windows.

Lighting (must be consistent across a whole series): soft natural daylight on a bright overcast late morning, neutral white balance around 5500 K, light entering through the windows, gentle soft shadows, realistic ambient bounce light, no artificial lamps switched on, no harsh sun beams, no lens flare, balanced exposure with no blown-out highlights and no crushed blacks.

Materials: realistic textures with fine detail — real wood grain, fabric weave on upholstery and textiles, natural leaves on plants, subtle wall surface texture, realistic reflections on glass, tiles and metal.

Remove the "HOMESTYLER" watermark logo in the bottom-right corner completely and fill the area naturally. No text, no watermark, no people.
```

## Luftbilder (`*/Luftbilder/*.jpg`, isometrische Schnittansichten)

```
Turn this 3D cutaway floor-plan rendering into a photorealistic architectural model visualization: the same open-top isometric cutaway of the apartment, rendered like a high-end physical-model photograph for a real-estate exposé.

Keep EXACTLY the same camera angle, framing, wall layout, wall heights, door and window positions, and every piece of furniture in the same position, shape, color and material. Do not add, remove or move any walls or objects. Keep the walls cut open at the top and keep the plain light-grey background.

Lighting (must be consistent across a whole series): soft natural daylight on a bright overcast late morning, neutral white balance around 5500 K, gentle soft shadows, realistic ambient bounce light, no harsh sun beams, no lens flare, balanced exposure with no blown-out highlights and no crushed blacks.

Materials: realistic textures with fine detail — real wood grain on floors and doors, fabric on beds and sofas, natural leaves on plants, matte plaster on the wall cut faces, realistic tiles in bathrooms and kitchens.

Remove the "HOMESTYLER" watermark logo in the bottom-right corner completely and fill the area with the plain background. No text, no watermark, no people.
```

Seitenverhältnis: `16:9` für alle Bilder außer `W3_Wohn-Esszimmer-3.jpg` und `W3_Wohn-Esszimmer-4.jpg` (1024×768 → `4:3`).
