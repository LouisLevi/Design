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

Nicht übernommen (nicht Web): `write-swift`, `animate-expo`.

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
