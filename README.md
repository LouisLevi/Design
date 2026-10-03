# Design

Dieses Repo enthält die Design-Skills von [Emil Kowalski](https://emilkowal.ski)
(Sonner, Vaul, animations.dev) für Claude Code – installiert unter `.claude/skills/`.
Claude Code lädt sie automatisch, sobald in diesem Repo gearbeitet wird.

Quelle: https://github.com/emilkowalski/skill (MIT, Stand: e8a175d)

## Enthaltene Skills

| Skill | Wofür |
| --- | --- |
| `emil-design-eng` | Hauptskill: UI-Politur, Animations-Entscheidungen, Design-Details |
| `animate` | Animationen von Grund auf bauen (Kurve, Dauer, Properties) |
| `review-animations` | Strenges Review bestehender Animationen (nur per `/review-animations`) |
| `improve-animations` | Ganze Codebase auf Animationen auditieren, mit Umsetzungsplänen |
| `find-animation-opportunities` | Stellen finden, an denen Motion wirklich hilft |
| `animation-vocabulary` | Die richtigen Begriffe für Animationseffekte |
| `apple-design` | Apples Design- und Motion-Prinzipien fürs Web |
| `mobile-native` | Web-Apps auf dem Handy nativ wirken lassen |
| `break-ui` | UI mit Worst-Case-Daten testen |
| `pick-ui-library` | Passende UI-Library wählen (nur per `/pick-ui-library`) |
| `prototype` | Mehrere UI-Varianten mit Umschalter bauen (nur per `/prototype`) |
| `ask-sonner` | Hilfe zur Toast-Library Sonner |

### Weitere Design-Skills

| Skill | Wofür | Quelle |
| --- | --- | --- |
| `frontend-design` | Eigenständige, nicht-generische Ästhetik (Typo, Farbe, Richtung) | [anthropics/skills](https://github.com/anthropics/skills) @ 8a1541c |
| `ui-ux-pro-max` | Durchsuchbare Design-Datenbank: Styles, Paletten, Fonts, UX-Regeln, Stacks | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) @ 477bcb2 (MIT) |
| `design-taste-frontend` | „Taste Skill“ v2 – Anti-Slop für Landingpages, Portfolios, Redesigns | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) @ ce26fc2 (MIT) |

`ui-ux-pro-max` nutzt ein Python-Skript (`python3`, keine Abhängigkeiten), z. B.:
`python3 .claude/skills/ui-ux-pro-max/scripts/search.py "fintech" --design-system`

Nicht übernommen (nicht Web): `write-swift`, `animate-expo`.

## MCP-Verbindungen

In `.mcp.json` sind drei Server konfiguriert. Schlüssel stehen **nicht** im Repo,
sondern kommen aus Umgebungsvariablen:

| Server | Wofür | Auth |
| --- | --- | --- |
| `stitch` | Google Stitch – UI-Designs generieren | `STITCH_API_KEY` (stitch.withgoogle.com → Profil → Stitch settings → API key) |
| `nano-banana` | Bilder mit Gemini (Nano Banana) erzeugen/bearbeiten | `GEMINI_API_KEY` (aistudio.google.com/apikey) |
| `vercel` | Website deployen, Projekte & Logs | OAuth – in Claude Code `/mcp` → `vercel` → Login |

Einrichtung lokal:

```bash
export STITCH_API_KEY=...
export GEMINI_API_KEY=...
claude          # Projekt-MCP-Server beim ersten Start bestätigen
/mcp            # Status prüfen, Vercel-Login durchführen
```

Hinweis: Falls Claude Code bei Stitch trotz Header einen OAuth-Login versucht
(bekanntes Problem), Stitch stattdessen global hinzufügen:
`claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: $STITCH_API_KEY" -s user`

## Nutzung

Einfach normal mit Claude Code arbeiten – die Skills greifen automatisch bei
passenden Aufgaben. Gezielt aufrufen z. B. mit `/emil-design-eng` oder `/prototype`.

Lokal für alle Projekte installieren (statt nur für dieses Repo):

```bash
npx skills@latest add emilkowalski/skills
```

## Aktualisieren

```bash
git clone --depth 1 https://github.com/emilkowalski/skill /tmp/emil-skill
cp -r /tmp/emil-skill/skills/<name> .claude/skills/
```
