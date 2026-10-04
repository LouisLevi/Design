/* Planungsbüro Günther – Interaktion (ohne Abhängigkeiten) */
(function () {
  "use strict";
  var doc = document.documentElement;
  var ROOT = doc.getAttribute("data-root") || "";
  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---------- Menü (Handy) ---------- */
  var mnav = $("#mnav"), opener = $("[data-open-menu]");
  function menu(open) {
    if (!mnav) return;
    mnav.classList.toggle("open", open);
    document.body.classList.toggle("locked", open);
    if (opener) opener.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var f = $("a", mnav); if (f) f.focus(); } else if (opener) opener.focus();
  }
  if (opener) opener.addEventListener("click", function () { menu(true); });
  $$("[data-close-menu]").forEach(function (b) { b.addEventListener("click", function () { menu(false); }); });

  /* ---------- 5 Schritte: der Schritt, der der Bildmitte am nächsten ist, wird aktiv ---------- */
  var steps = $$(".st");
  if (steps.length) {
    var ticking = false;
    var update = function () {
      ticking = false;
      var mid = window.innerHeight / 2, best = steps[0], bestD = Infinity;
      steps.forEach(function (s) {
        var r = s.getBoundingClientRect(), d = Math.abs(r.top + Math.min(r.height, 200) / 2 - mid);
        if (d < bestD) { bestD = d; best = s; }
      });
      steps.forEach(function (s) { s.classList.toggle("on", s === best); });
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  /* ---------- Filme: Klick spielt den Film an Ort und Stelle ab ---------- */
  $$("button[data-film]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var src = btn.getAttribute("data-film");
      var poster = $("img", btn);
      var box = el("div", { class: btn.className + " playing" });
      var v = el("video", { controls: "", playsinline: "", preload: "auto", src: src, "aria-label": btn.getAttribute("aria-label").replace("Film abspielen: ", "Film: ") });
      if (poster) v.setAttribute("poster", poster.getAttribute("src"));
      box.appendChild(v);
      btn.replaceWith(box);
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      v.focus();
    });
  });

  /* ---------- Projekt-Ansicht ---------- */
  var DATA = window.PG_PROJEKTE || [];
  var BY = {}; DATA.forEach(function (p) { BY[p.slug] = p; });
  var ov, stage, thumbs, info, items = [], idx = 0, current = null, lastFocus = null;

  function buildOverlay() {
    ov = el("div", { class: "ov", role: "dialog", "aria-modal": "true", "aria-label": "Projekt" });
    ov.innerHTML =
      '<div class="ov-media"><div class="ov-stage"></div>' +
      '<button class="ov-prev" type="button" aria-label="Vorheriges Bild"><span class="ar"></span></button>' +
      '<button class="ov-next" type="button" aria-label="Nächstes Bild"><span class="ar"></span></button>' +
      '<div class="ov-thumbs"></div></div><div class="ov-info"></div>';
    document.body.appendChild(ov);
    stage = $(".ov-stage", ov); thumbs = $(".ov-thumbs", ov); info = $(".ov-info", ov);
    $(".ov-prev", ov).addEventListener("click", function () { show(idx - 1); });
    $(".ov-next", ov).addEventListener("click", function () { show(idx + 1); });
    var x0 = null;
    stage.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener("touchend", function (e) {
      if (x0 == null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  function show(i) {
    if (!items.length) return;
    idx = (i + items.length) % items.length;
    var it = items[idx];
    stage.innerHTML = "";
    if (it.type === "film") {
      var v = el("video", { controls: "", playsinline: "", preload: "metadata", poster: ROOT + "assets/video/" + it.name + ".webp", src: ROOT + "assets/video/" + it.name + ".mp4" });
      stage.appendChild(v);
    } else {
      stage.appendChild(el("img", { src: ROOT + "assets/img/p/" + it.name + ".webp", width: it.w, height: it.h, alt: current.title + ", Bild " + (idx + 1) }));
    }
    $$("button", thumbs).forEach(function (b, k) { b.setAttribute("aria-current", k === idx ? "true" : "false"); });
    var one = items.length < 2;
    $(".ov-prev", ov).hidden = one; $(".ov-next", ov).hidden = one; thumbs.hidden = one;
  }

  function open(slug, push) {
    var p = BY[slug]; if (!p) return;
    if (!ov) buildOverlay();
    current = p; lastFocus = document.activeElement;
    items = p.img.map(function (i) { return { type: "img", name: i[0], w: i[1], h: i[2] }; });
    if (p.film) items.push({ type: "film", name: p.film });
    thumbs.innerHTML = items.map(function (it, k) {
      return '<button type="button" aria-label="' + (it.type === "film" ? "Film" : "Bild " + (k + 1)) + '">' +
        (it.type === "film" ? '<span class="tfilm">▶ Film</span>' : '<img src="' + ROOT + "assets/img/p/" + it.name + '-s.webp" alt="" loading="lazy">') + "</button>";
    }).join("");
    $$("button", thumbs).forEach(function (b, k) { b.addEventListener("click", function () { show(k); }); });
    var rows = p.rows.map(function (r) { return "<div><dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd></div>"; }).join("");
    info.innerHTML =
      '<button class="ov-close" type="button">Schließen <i aria-hidden="true"></i></button>' +
      '<span class="label">' + esc(p.cat) + "</span><h2>" + esc(p.title) + "</h2><dl>" + rows + "</dl>" +
      '<div class="ov-foot"><span>Interesse an einem ähnlichen Projekt?</span><a class="btn btn--white" href="' + ROOT + 'kontakt/">Kontakt <span class="ar"></span></a></div>';
    $(".ov-close", info).addEventListener("click", close);
    ov.setAttribute("aria-label", p.title);
    show(0);
    ov.classList.add("open");
    document.body.classList.add("locked");
    if (push !== false && location.hash !== "#" + slug) history.replaceState(null, "", "#" + slug);
    setTimeout(function () { var c = $(".ov-close", info); if (c) c.focus(); }, 30);
  }

  function close() {
    if (!ov || !ov.classList.contains("open")) return;
    ov.classList.remove("open");
    document.body.classList.remove("locked");
    var v = $("video", stage); if (v) v.pause();
    history.replaceState(null, "", location.pathname + location.search);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  $$("[data-slug]").forEach(function (n) {
    n.addEventListener("click", function () { open(n.getAttribute("data-slug")); });
    if (n.tagName === "TR") n.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(n.getAttribute("data-slug")); } });
  });
  function fromHash() { var s = decodeURIComponent(location.hash.slice(1)); if (BY[s]) open(s, false); }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { if (ov && ov.classList.contains("open")) close(); else if (mnav && mnav.classList.contains("open")) menu(false); }
    if (ov && ov.classList.contains("open")) {
      if (e.key === "ArrowRight") show(idx + 1);
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "Tab") { // Fokus im Dialog halten
        var f = $$("button, a, video", ov).filter(function (x) { return x.offsetParent !== null; });
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      }
    }
  });

  /* ---------- Werkverzeichnis: Filter ---------- */
  var tabs = $$(".tabs button");
  tabs.forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.getAttribute("data-filter");
      tabs.forEach(function (t) { t.setAttribute("aria-pressed", t === b ? "true" : "false"); });
      $$(".ptable tbody tr").forEach(function (r) { r.hidden = !(f === "alle" || r.getAttribute("data-cat") === f); });
    });
  });

  /* ---------- Kontaktformular ----------
     data-endpoint leer  → öffnet das E-Mail-Programm mit vorbereiteter Nachricht.
     data-endpoint = URL → sendet per POST an den Formulardienst (wird nachgerüstet). */
  var form = $("#anfrage");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var note = $(".form-note", form), bad = null;
      $$("[required]", form).forEach(function (f) {
        var ok = f.value.trim() !== "" && (f.type !== "email" || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value.trim()));
        f.setAttribute("aria-invalid", ok ? "false" : "true");
        f.style.borderColor = ok ? "" : "#ffffff";
        if (!ok && !bad) bad = f;
      });
      if (bad) { note.textContent = "Bitte füllen Sie die markierten Pflichtfelder aus."; bad.focus(); return; }
      var data = {}; $$("input, textarea", form).forEach(function (f) { data[f.name] = f.value.trim(); });
      var endpoint = form.getAttribute("data-endpoint");
      if (endpoint) {
        note.textContent = "Wird gesendet …";
        fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(data) })
          .then(function (r) { if (!r.ok) throw new Error(); form.reset(); note.textContent = "Danke! Ihre Nachricht ist angekommen – wir melden uns."; })
          .catch(function () { note.textContent = "Das hat leider nicht geklappt. Bitte schreiben Sie direkt an buero@planungsbuero-guenther.de."; });
        return;
      }
      var body = "Name: " + data["Name"] + "\nE-Mail: " + data["E-Mail"] + "\nTelefon: " + data["Telefon"] + "\n\n" + data["Nachricht"];
      location.href = "mailto:buero@planungsbuero-guenther.de?subject=" + encodeURIComponent(data["Betreff"]) + "&body=" + encodeURIComponent(body);
      note.textContent = "Ihr E-Mail-Programm öffnet sich mit der vorbereiteten Nachricht.";
    });
  }
})();
