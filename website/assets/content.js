/*
 * Inhalte der Website.
 *
 * PROJEKTE SIND PLATZHALTER: Titel, Orte und Kennzahlen unten sind Beispiele,
 * damit das Layout gefüllt ist. Bitte durch die echten Projekte ersetzen.
 *
 * Bilder: `image` kann ein Pfad wie "images/projekt-labor.jpg" sein.
 * Bleibt es leer, wird automatisch das nächste Bild aus images/manifest.js
 * (vom Download-Skript erzeugt) verwendet – und sonst eine gezeichnete Fassade.
 */
window.SITE_CONTENT = {
  categories: [
    { id: "all", label: "Alle" },
    { id: "labor", label: "Büro & Labor" },
    { id: "denkmal", label: "Denkmalschutz" },
    { id: "wissenschaft", label: "Wissenschaft" },
    { id: "betrieb", label: "Laufender Betrieb" },
  ],

  projects: [
    {
      title: "Laborgebäude, Neubau",
      category: "labor",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 1–8",
      text: "Platzhaltertext: Neubau eines Labor- und Bürogebäudes mit hohem Technisierungsgrad. Hier stehen später Aufgabe, Konzept und Besonderheiten des Projekts.",
      image: "",
      size: "wide",
    },
    {
      title: "Sanierung eines Baudenkmals",
      category: "denkmal",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 2–9",
      text: "Platzhaltertext: Instandsetzung und Umnutzung eines denkmalgeschützten Gebäudes in enger Abstimmung mit der Denkmalpflege.",
      image: "",
    },
    {
      title: "Institutsgebäude",
      category: "wissenschaft",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 1–9",
      text: "Platzhaltertext: Gebäude für Forschung und Lehre mit Büro-, Seminar- und Laborflächen.",
      image: "",
    },
    {
      title: "Umbau im laufenden Betrieb",
      category: "betrieb",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 5–8",
      text: "Platzhaltertext: Abschnittsweiser Umbau, während Nutzerinnen und Nutzer im Gebäude weiterarbeiten.",
      image: "",
    },
    {
      title: "Bürogebäude, Modernisierung",
      category: "labor",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 3–8",
      text: "Platzhaltertext: Modernisierung eines Verwaltungsgebäudes mit neuer Haustechnik und Brandschutzkonzept.",
      image: "",
    },
    {
      title: "Forschungslabor, Erweiterung",
      category: "wissenschaft",
      place: "Ort folgt",
      year: "Jahr folgt",
      phases: "LPH 1–8",
      text: "Platzhaltertext: Erweiterung bestehender Laborflächen mit Koordination von Laborplanung, HLS und Elektro.",
      image: "",
      size: "wide",
    },
  ],

  phases: [
    { n: 1, title: "Grundlagenermittlung", text: "Aufgabe klären, Bedarf erfassen, Bestand und Rahmenbedingungen aufnehmen." },
    { n: 2, title: "Vorplanung", text: "Erste Konzepte und Varianten, Kostenschätzung, Abstimmung mit Bauherr und Nutzern." },
    { n: 3, title: "Entwurfsplanung", text: "Durchgearbeiteter Entwurf mit Fachplanung, Kostenberechnung." },
    { n: 4, title: "Genehmigungsplanung", text: "Bauantrag und Abstimmung mit Behörden – auch mit der Denkmalpflege." },
    { n: 5, title: "Ausführungsplanung", text: "Werk- und Detailplanung als Grundlage für die Ausführung." },
    { n: 6, title: "Vorbereitung der Vergabe", text: "Leistungsverzeichnisse und Mengenermittlung." },
    { n: 7, title: "Mitwirkung bei der Vergabe", text: "Angebote prüfen, werten und Vergabe vorbereiten." },
    { n: 8, title: "Objektüberwachung", text: "Bauleitung, Termin- und Kostenkontrolle, Qualitätssicherung auf der Baustelle." },
    { n: 9, title: "Objektbetreuung", text: "Begehungen zur Mängelfeststellung und Dokumentation nach der Übergabe." },
  ],
};
