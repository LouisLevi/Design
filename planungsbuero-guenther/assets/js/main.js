/* Planungsbüro Günther – Interaktionen (ohne Abhängigkeiten) */
(function () {
  "use strict";

  var P = window.PG_PROJECTS || [];
  var IMG = "assets/img/p/";
  var VID = "assets/video/";
  var CATS = {
    aktuell: "Aktuelle Projekte",
    efh: "Einfamilienhäuser",
    mfh: "Mehrfamilienhäuser",
    gewerbe: "Gewerbe & Sonstige",
    entwicklung: "Projektentwicklungen"
  };
  var CAT_SHORT = { aktuell: "Aktuell", efh: "EFH", mfh: "MFH", gewerbe: "Gewerbe", entwicklung: "Entwicklung" };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  function fmtVol(v) {
    if (!v) return "–";
    if (v >= 1e6) return (v / 1e6).toLocaleString("de-DE", { maximumFractionDigits: 1 }) + " Mio. €";
    return (v / 1e3).toLocaleString("de-DE", { maximumFractionDigits: 0 }) + " T€";
  }
  function yearLabel(p) {
    if (!p.jahr) return "–";
    return p.status === "geplant" ? p.jahr + " (gepl.)" : String(p.jahr);
  }
  function cover(p) {
    if (p.img && p.img.length) return IMG + p.img[0][0] + "-s.webp";
    if (p.film) return VID + p.film + ".webp";
    return "";
  }
  function media(p) {
    var list = [];
    if (p.film) list.push({ type: "film", src: VID + p.film + ".mp4", poster: VID + p.film + ".webp", thumb: VID + p.film + ".webp" });
    (p.img || []).forEach(function (i) { list.push({ type: "img", src: IMG + i[0] + ".webp", thumb: IMG + i[0] + "-s.webp", w: i[1], h: i[2] }); });
    return list;
  }

  /* ---------- Navigation ---------- */
  var toggle = $(".menu-toggle"), nav = $("#site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) { nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); } });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("is-open")) { nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); toggle.focus(); } });
  }

  /* ---------- Hero-Viewport ---------- */
  var hv = $("#hero-video");
  if (hv) {
    var tc = $("#hero-tc"), pauseBtn = $("#hero-pause");
    if (reduceMotion) { hv.removeAttribute("autoplay"); hv.pause(); if (pauseBtn) pauseBtn.textContent = "Abspielen"; }
    hv.addEventListener("timeupdate", function () {
      if (!tc) return;
      var t = hv.currentTime, m = Math.floor(t / 60), s = Math.floor(t % 60), f = Math.floor((t % 1) * 25);
      tc.textContent = "TC 00:" + String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0") + ":" + String(f).padStart(2, "0");
    });
    if (pauseBtn) pauseBtn.addEventListener("click", function () {
      if (hv.paused) { hv.play(); pauseBtn.textContent = "Pause"; } else { hv.pause(); pauseBtn.textContent = "Abspielen"; }
    });
  }

  /* ---------- Karten ---------- */
  function cardHTML(p) {
    var badges = '<span class="badge">' + esc(CAT_SHORT[p.cat]) + "</span>";
    if (p.status === "geplant") badges += '<span class="badge badge--accent">In Arbeit</span>';
    if (p.film) badges += '<span class="badge">Film</span>';
    var n = (p.img || []).length + (p.film ? 1 : 0);
    var cells = [["Ort", p.ort], ["Jahr", yearLabel(p)]];
    if (p.cat === "entwicklung") cells.push(["Grundstück", p.grundstueck || "–"]);
    else cells.push(["Leistung", p.lph || "–"], ["Bauvolumen", fmtVol(p.volumen)]);
    return '<button type="button" class="card" data-open="' + esc(p.slug) + '" aria-label="' + esc(p.title) + ', ' + esc(p.ort) + ' – Details öffnen">' +
      '<div class="card-media"><div class="card-badges">' + badges + "</div>" +
      (cover(p) ? '<img src="' + cover(p) + '" alt="" loading="lazy" decoding="async">' : "") +
      '<span class="badge card-count">' + n + (n === 1 ? " Medium" : " Medien") + "</span></div>" +
      '<div class="schriftfeld sf-' + cells.length + '"><div class="sf-title"><span class="sf-id"><span>' + esc(p.id) + "</span><span>" + esc(CATS[p.cat]) + "</span></span><h3>" + esc(p.title) + "</h3></div>" +
      cells.map(function (c) { return '<div class="sf-cell"><span class="sf-k">' + c[0] + '</span><span class="sf-v">' + esc(c[1]) + "</span></div>"; }).join("") +
      "</div></button>";
  }

  /* Startseite: ausgewählte Projekte */
  var feat = $("#featured");
  if (feat && P.length) {
    var f = P.filter(function (p) { return p.featured != null; }).sort(function (a, b) { return a.featured - b.featured; }).slice(0, 5);
    feat.innerHTML = f.map(cardHTML).join("");
  }

  /* ---------- Projektdatenbank ---------- */
  var grid = $("#project-grid");
  if (grid) {
    var state = { cat: "alle", q: "", sort: "jahr-desc", view: "raster", film: false };
    try { var saved = localStorage.getItem("pg-view"); if (saved === "liste" || saved === "raster") state.view = saved; } catch (e) {}
    var hash = (location.hash || "").slice(1);
    if (CATS[hash]) state.cat = hash;

    var chipWrap = $("#cat-chips");
    var counts = { alle: P.length };
    P.forEach(function (p) { counts[p.cat] = (counts[p.cat] || 0) + 1; });
    var filmCount = P.filter(function (p) { return p.film; }).length;
    chipWrap.innerHTML = ["alle"].concat(Object.keys(CATS)).map(function (k) {
      return '<button type="button" class="chip" data-cat="' + k + '" aria-pressed="' + (state.cat === k) + '">' + (k === "alle" ? "Alle" : CATS[k]) + ' <span class="mono">' + counts[k] + "</span></button>";
    }).join("") + '<button type="button" class="chip" data-film aria-pressed="false">Mit Film <span class="mono">' + filmCount + "</span></button>";

    var list = $("#project-list"), tbody = $("#project-tbody"), count = $("#result-count"), empty = $("#empty");

    function filtered() {
      var q = state.q.trim().toLowerCase();
      var out = P.filter(function (p) {
        if (state.cat !== "alle" && p.cat !== state.cat) return false;
        if (state.film && !p.film) return false;
        if (!q) return true;
        return (p.title + " " + p.ort + " " + (p.jahr || "") + " " + (p.lph || "") + " " + CATS[p.cat] + " " + p.id).toLowerCase().indexOf(q) !== -1;
      });
      var s = state.sort;
      out.sort(function (a, b) {
        if (s === "jahr-desc") return (b.jahr || 0) - (a.jahr || 0);
        if (s === "jahr-asc") return (a.jahr || 9999) - (b.jahr || 9999);
        if (s === "vol-desc") return (b.volumen || 0) - (a.volumen || 0);
        if (s === "ort-asc") return a.ort.localeCompare(b.ort, "de");
        if (s === "title-asc") return a.title.localeCompare(b.title, "de");
        return 0;
      });
      return out;
    }

    function render() {
      var rows = filtered();
      count.textContent = rows.length + (rows.length === 1 ? " Projekt" : " Projekte");
      empty.hidden = rows.length > 0;
      grid.hidden = state.view !== "raster" || rows.length === 0;
      list.hidden = state.view !== "liste" || rows.length === 0;
      if (state.view === "raster") grid.innerHTML = rows.map(cardHTML).join("");
      else tbody.innerHTML = rows.map(function (p) {
        return '<tr data-open="' + esc(p.slug) + '" tabindex="0">' +
          "<td>" + (cover(p) ? '<img class="thumb" src="' + cover(p) + '" alt="" loading="lazy">' : "") + "</td>" +
          '<td class="mono">' + esc(p.id) + "</td>" +
          '<td class="t-title">' + esc(p.title) + (p.film ? ' <span class="mono" style="color:var(--accent)">· Film</span>' : "") + "</td>" +
          "<td>" + esc(p.ort) + "</td>" +
          '<td class="mono">' + esc(yearLabel(p)) + "</td>" +
          '<td class="mono">' + esc(p.lph || "–") + "</td>" +
          '<td class="mono right">' + esc(fmtVol(p.volumen)) + "</td></tr>";
      }).join("");
      $$("#cat-chips .chip[data-cat]").forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.cat === state.cat)); });
      $("#cat-chips .chip[data-film]").setAttribute("aria-pressed", String(state.film));
      $$("[data-view]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.view === state.view)); });
      $$(".ptable th button").forEach(function (b) {
        var k = b.dataset.sort; b.removeAttribute("data-dir");
        if (state.sort.indexOf(k) === 0) b.setAttribute("data-dir", state.sort.split("-")[1]);
      });
    }

    chipWrap.addEventListener("click", function (e) {
      var c = e.target.closest(".chip"); if (!c) return;
      if (c.hasAttribute("data-film")) state.film = !state.film;
      else { state.cat = c.dataset.cat; try { history.replaceState(null, "", state.cat === "alle" ? location.pathname : "#" + state.cat); } catch (err) {} }
      render();
    });
    $("#q").addEventListener("input", function (e) { state.q = e.target.value; render(); });
    $("#sort").addEventListener("change", function (e) { state.sort = e.target.value; render(); });
    $$("[data-view]").forEach(function (b) {
      b.addEventListener("click", function () { state.view = b.dataset.view; try { localStorage.setItem("pg-view", state.view); } catch (e) {} render(); });
    });
    $$(".ptable th button").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.sort, cur = state.sort;
        var def = { jahr: "desc", vol: "desc", ort: "asc", title: "asc" }[k];
        if (cur.indexOf(k) === 0) state.sort = k + "-" + (cur.split("-")[1] === "asc" ? "desc" : "asc");
        else state.sort = k + "-" + def;
        var sel = $("#sort"); if ($('#sort option[value="' + state.sort + '"]')) sel.value = state.sort;
        render();
      });
    });
    tbody.addEventListener("keydown", function (e) { if (e.key === "Enter" && e.target.dataset.open) openProject(e.target.dataset.open); });
    render();
  }

  /* ---------- Projektdetail ---------- */
  var dlg = $("#project-dialog");
  var current = null, idx = 0, order = [];
  function bySlug(s) { for (var i = 0; i < P.length; i++) if (P[i].slug === s) return P[i]; return null; }

  function showMedia(i) {
    var m = media(current); if (!m.length) return;
    idx = (i + m.length) % m.length;
    var it = m[idx], main = $(".pd-main", dlg);
    var old = $("video", main); if (old) old.pause();
    if (it.type === "film") {
      main.innerHTML = '<video src="' + it.src + '" poster="' + it.poster + '" controls playsinline preload="metadata"></video>';
    } else {
      main.innerHTML = '<img src="' + it.src + '" width="' + it.w + '" height="' + it.h + '" alt="' + esc(current.title) + ", Ansicht " + (idx + 1) + '">';
    }
    $$(".pd-thumbs button", dlg).forEach(function (b, j) { b.setAttribute("aria-current", String(j === idx)); });
    var cnt = $("#pd-count", dlg); if (cnt) cnt.textContent = String(idx + 1).padStart(2, "0") + " / " + String(m.length).padStart(2, "0");
    $$(".pd-nav", dlg).forEach(function (b) { b.hidden = m.length < 2; });
  }

  function openProject(slug, opts) {
    var p = bySlug(slug); if (!p || !dlg) return;
    current = p;
    order = grid ? $$("[data-open]", grid.hidden ? $("#project-tbody") : grid).map(function (el) { return el.dataset.open; }) : P.map(function (x) { return x.slug; });
    if (order.indexOf(slug) === -1) order = P.map(function (x) { return x.slug; });
    var m = media(p);
    var rows = [
      ["Kategorie", CATS[p.cat]], ["Bauort", p.ort],
      [p.cat === "entwicklung" ? "Erstellungsjahr" : (p.status === "geplant" ? "Fertigstellung (geplant)" : "Fertigstellung"), p.jahr || "Keine Angabe"],
      ["Leistungen", p.lph || "Keine Angabe"]
    ];
    if (p.volumen) rows.push(["Bauvolumen", fmtVol(p.volumen)]);
    if (p.grundstueck) rows.push(["Grundstück", p.grundstueck]);
    if (rows.length % 2) rows.push(["Medien", m.length + (m.length === 1 ? " Datei" : " Dateien")]);
    $(".pd-info", dlg).innerHTML =
      '<div class="pd-top"><span class="mono">' + esc(p.id) + ' · <span id="pd-count"></span></span>' +
      '<button type="button" class="pd-close" data-close aria-label="Schließen"><svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.4"/></svg></button></div>' +
      '<div class="pd-title"><span class="eyebrow">' + esc(CATS[p.cat]) + '</span><h2 id="pd-heading">' + esc(p.title) + "</h2></div>" +
      '<div class="pd-table">' + rows.map(function (r) { return '<div><span class="sf-k">' + esc(r[0]) + '</span><span class="sf-v">' + esc(r[1]) + "</span></div>"; }).join("") + "</div>" +
      '<div class="pd-actions"><p>Sie planen ein vergleichbares Vorhaben? Wir beraten Sie gern zu Machbarkeit, Kosten und Ablauf.</p>' +
      '<a class="btn" href="kontakt.html?projekt=' + encodeURIComponent(p.id) + '">Ähnliches Projekt anfragen <span class="arrow" aria-hidden="true">→</span></a></div>' +
      '<div class="pd-step"><button type="button" data-step="-1">← Vorheriges Projekt</button><button type="button" data-step="1">Nächstes Projekt →</button></div>';
    $(".pd-thumbs", dlg).innerHTML = m.map(function (it, j) {
      return '<button type="button" data-idx="' + j + '" aria-label="' + (it.type === "film" ? "Film" : "Bild " + (j + 1)) + '"><img src="' + it.thumb + '" alt="" loading="lazy">' + (it.type === "film" ? '<span class="film-tag">FILM</span>' : "") + "</button>";
    }).join("");
    $(".pd-thumbs", dlg).hidden = m.length < 2;
    if (!dlg.open) dlg.showModal();
    showMedia(opts && opts.film === false && p.film ? 1 : 0);
    try { history.replaceState(null, "", "#" + p.slug); } catch (e) {}
  }

  function closeProject() {
    if (!dlg) return;
    var v = $("video", dlg); if (v) v.pause();
    dlg.close();
  }

  if (dlg) {
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg || e.target.closest("[data-close]")) return closeProject();
      var t = e.target.closest("[data-idx]"); if (t) return showMedia(+t.dataset.idx);
      if (e.target.closest(".pd-prev")) return showMedia(idx - 1);
      if (e.target.closest(".pd-next")) return showMedia(idx + 1);
      var s = e.target.closest("[data-step]");
      if (s) { var i = order.indexOf(current.slug); openProject(order[(i + +s.dataset.step + order.length) % order.length]); }
    });
    dlg.addEventListener("close", function () {
      var v = $("video", dlg); if (v) v.pause();
      try { history.replaceState(null, "", location.pathname + (grid && $("#cat-chips .chip[aria-pressed=true][data-cat]") && $("#cat-chips .chip[aria-pressed=true][data-cat]").dataset.cat !== "alle" ? "#" + $("#cat-chips .chip[aria-pressed=true][data-cat]").dataset.cat : "")); } catch (e) {}
    });
    dlg.addEventListener("keydown", function (e) {
      if (e.target.matches("video")) return;
      if (e.key === "ArrowRight") { e.preventDefault(); showMedia(idx + 1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); showMedia(idx - 1); }
    });
    /* Wischgeste in der Galerie */
    var sx = null, sy = null;
    $(".pd-main", dlg).addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") { sx = e.clientX; sy = e.clientY; } });
    $(".pd-main", dlg).addEventListener("pointerup", function (e) {
      if (sx == null) return;
      var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) showMedia(idx + (dx < 0 ? 1 : -1));
    });
    document.addEventListener("click", function (e) {
      var o = e.target.closest("[data-open]");
      if (o && !dlg.contains(o)) { e.preventDefault(); openProject(o.dataset.open, { film: o.hasAttribute("data-film-first") ? true : undefined }); }
    });
    var h = (location.hash || "").slice(1);
    if (h && bySlug(h)) openProject(h);
  }

  /* ---------- HOAI-Leistungsphasen ---------- */
  var lph = $("#lph");
  if (lph) {
    var PH = [
      ["Grundlagenermittlung", "Wir klären Aufgabe, Grundstück, Bedarf und Rahmenbedingungen und beraten Sie zum gesamten Leistungsbedarf.", 2, "Bedarf · Ortstermin · Bestandsaufnahme"],
      ["Vorplanung", "Erste Konzepte und Varianten mit Kostenschätzung. Hier entsteht die Idee Ihres Gebäudes, auf Wunsch schon als 3D-Visualisierung.", 7, "Varianten · Kostenschätzung · 3D-Studien"],
      ["Entwurfsplanung", "Das Konzept wird zum durchgearbeiteten Entwurf mit Kostenberechnung und abgestimmten Fachplanungen.", 15, "Entwurf · Kostenberechnung · Fachplaner"],
      ["Genehmigungsplanung", "Wir erstellen die Bauantragsunterlagen, inklusive Entwässerungsantrag, und begleiten das Verfahren bis zur Baugenehmigung.", 3, "Bauantrag · Entwässerung · Behörden"],
      ["Ausführungsplanung", "Werk- und Detailpläne bis in den Maßstab 1:50 und 1:1 als verbindliche Grundlage für die Ausführung.", 25, "Werkpläne · Details · Planfreigaben"],
      ["Vorbereitung der Vergabe", "Mengenermittlung und Leistungsverzeichnisse, damit die Angebote vergleichbar werden.", 10, "Mengen · Leistungsverzeichnisse"],
      ["Mitwirkung bei der Vergabe", "Wir holen Angebote ein, prüfen und werten sie aus und bereiten die Auftragsvergabe vor.", 4, "Preisspiegel · Vergabevorschlag"],
      ["Objektüberwachung", "Bauüberwachung vor Ort: Qualität, Termine und Kosten im Blick, bis zur Abnahme.", 32, "Bauleitung · Termine · Kostenkontrolle"],
      ["Objektbetreuung", "Begehung vor Ablauf der Gewährleistung und Unterstützung bei der Mängelbeseitigung.", 2, "Gewährleistung · Dokumentation"]
    ];
    var bar = $("#lph-bar");
    bar.innerHTML = PH.map(function (ph, i) {
      return '<button type="button" aria-pressed="' + (i === 0) + '" data-lph="' + i + '"><span class="mono">LPH</span><strong>' + (i + 1) + '</strong><span class="visually-hidden">' + ph[0] + "</span></button>";
    }).join("");
    function setLph(i) {
      var ph = PH[i];
      $$("button", bar).forEach(function (b, j) { b.setAttribute("aria-pressed", String(j === i)); });
      $("#lph-num").textContent = String(i + 1);
      $("#lph-name").textContent = ph[0];
      $("#lph-desc").textContent = ph[1];
      $("#lph-share").textContent = ph[2] + " %";
      $("#lph-keys").textContent = ph[3];
      var n = P.filter(function (p) {
        var m = /LPH\s*(\d)(?:–(\d))?/.exec(p.lph || ""); if (!m) return false;
        var a = +m[1], b = m[2] ? +m[2] : a; return i + 1 >= a && i + 1 <= b;
      }).length;
      $("#lph-refs").textContent = n + " von " + P.length;
    }
    bar.addEventListener("click", function (e) { var b = e.target.closest("[data-lph]"); if (b) setLph(+b.dataset.lph); });
    bar.addEventListener("keydown", function (e) {
      var b = e.target.closest("[data-lph]"); if (!b) return;
      var i = +b.dataset.lph;
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault(); i = (i + (e.key === "ArrowRight" ? 1 : -1) + 9) % 9; setLph(i); $$("button", bar)[i].focus();
      }
    });
    setLph(0);
  }

  /* ---------- Kontakt ---------- */
  var openEl = $("#open-state");
  if (openEl) {
    try {
      var parts = new Intl.DateTimeFormat("de-DE", { timeZone: "Europe/Berlin", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
      var get = function (t) { var x = parts.filter(function (p) { return p.type === t; })[0]; return x ? x.value : ""; };
      var wd = get("weekday").replace(".", ""), hh = +get("hour"), mm = +get("minute");
      var isOpen = ["Mo", "Di", "Mi", "Do", "Fr"].indexOf(wd) !== -1 && (hh * 60 + mm) >= 540 && (hh * 60 + mm) < 1020;
      openEl.textContent = isOpen ? "Jetzt im Büro erreichbar" : "Außerhalb der Bürozeiten";
      openEl.classList.toggle("is-open", isOpen);
    } catch (e) { openEl.hidden = true; }
  }

  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var txt = b.getAttribute("data-copy");
      var done = function () { b.textContent = "Kopiert"; b.classList.add("is-done"); setTimeout(function () { b.textContent = "Kopieren"; b.classList.remove("is-done"); }, 1800); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, function () {});
    });
  });

  var form = $("#contact-form");
  if (form) {
    var pre = new URLSearchParams(location.search).get("projekt");
    if (pre) { var ref = bySlugId(pre); if (ref) $("#f-msg").value = "Bezug: Referenz " + ref.id + " – " + ref.title + " (" + ref.ort + ")\n\n"; }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = $("#form-status");
      if (!form.checkValidity()) { status.className = "form-status is-error"; status.textContent = "Bitte füllen Sie Name, E-Mail, Nachricht und die Einwilligung aus."; form.reportValidity(); return; }
      var fd = new FormData(form);
      var art = fd.getAll("art").join(", ");
      var body = [
        "Name: " + fd.get("name"),
        fd.get("firma") ? "Firma: " + fd.get("firma") : "",
        "E-Mail: " + fd.get("email"),
        fd.get("telefon") ? "Telefon: " + fd.get("telefon") : "",
        art ? "Vorhaben: " + art : "",
        fd.get("ort") ? "Bauort: " + fd.get("ort") : "",
        fd.get("zeit") ? "Zeitrahmen: " + fd.get("zeit") : "",
        "", String(fd.get("nachricht") || "")
      ].filter(function (l, i, a) { return l !== "" || (i > 0 && a[i - 1] !== ""); }).join("\n");
      var subject = "Projektanfrage" + (art ? " – " + art : "") + " – " + fd.get("name");
      location.href = "mailto:buero@planungsbuero-guenther.de?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      status.className = "form-status is-ok";
      status.textContent = "Ihr E-Mail-Programm öffnet sich mit der vorbereiteten Anfrage. Falls nicht, schreiben Sie uns direkt an buero@planungsbuero-guenther.de.";
    });
  }
  function bySlugId(id) { for (var i = 0; i < P.length; i++) if (P[i].id === id) return P[i]; return null; }

  var y = $("#year"); if (y) y.textContent = new Date().getFullYear();
})();
