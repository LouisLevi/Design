(() => {
  "use strict";
  document.documentElement.classList.add("js");

  const C = window.SITE_CONTENT;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ───────── Images from the original site (images/manifest.js) ───────── */
  const pool = (window.SITE_IMAGES || []).filter((im) => im && im.src);
  const used = new Set();
  const area = (im) => (im.width || 0) * (im.height || 0);
  const take = (pred) => {
    const im = pool.find((x) => !used.has(x.src) && (!pred || pred(x)));
    if (im) used.add(im.src);
    return im || null;
  };
  const matches = (re) => (im) => re.test(`${im.src} ${im.alt || ""} ${im.page || ""}`);
  // Logos/icons are not photos
  const isPhoto = (im) => !/logo|icon|favicon|sprite/i.test(`${im.src} ${im.alt || ""}`) && (area(im) === 0 || area(im) > 160 * 160);

  const heroImg = (() => {
    const photos = pool.filter(isPhoto).filter((im) => !matches(/team|vita|portrait|guenther|günther/i)(im));
    const best = photos.sort((a, b) => area(b) - area(a))[0];
    if (best) used.add(best.src);
    return best || null;
  })();
  const portraitImg = take((im) => isPhoto(im) && matches(/vita|portrait|carsten|inhaber/i)(im));
  const nextPhoto = (pred) => take((im) => isPhoto(im) && (!pred || pred(im)));

  /* ───────── Drawn facade placeholder ───────── */
  function rng(seed) {
    let s = seed * 9301 + 49297;
    return () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  }
  function facadeSVG(seed) {
    const r = rng(seed);
    const W = 400, H = 300;
    const floors = 3 + Math.floor(r() * 4);
    const cols = 5 + Math.floor(r() * 6);
    const left = 40 + r() * 60, right = W - 40 - r() * 60;
    const ground = H - 36;
    const top = 60 + r() * 50;
    const fh = (ground - top) / floors;
    const cw = (right - left) / cols;
    let s = `<svg class="facade" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="0.8">`;
    s += `<line x1="0" y1="${ground}" x2="${W}" y2="${ground}"/>`;
    s += `<rect x="${left}" y="${top}" width="${right - left}" height="${ground - top}"/>`;
    if (r() > 0.5) s += `<path d="M${left - 6} ${top} L${(left + right) / 2} ${top - 34 - r() * 20} L${right + 6} ${top}"/>`;
    else s += `<line x1="${left - 6}" y1="${top}" x2="${right + 6}" y2="${top}"/><line x1="${left - 6}" y1="${top - 5}" x2="${right + 6}" y2="${top - 5}"/>`;
    for (let f = 0; f < floors; f++) {
      const y = top + f * fh;
      if (f > 0) s += `<line x1="${left}" y1="${y}" x2="${right}" y2="${y}" opacity="0.5"/>`;
      for (let c = 0; c < cols; c++) {
        const isDoor = f === floors - 1 && c === Math.floor(cols / 2);
        const x = left + c * cw + cw * 0.22;
        const w = cw * 0.56;
        const wy = y + fh * (isDoor ? 0.25 : 0.2);
        const wh = isDoor ? fh * 0.75 : fh * 0.58;
        s += `<rect x="${x.toFixed(1)}" y="${wy.toFixed(1)}" width="${w.toFixed(1)}" height="${wh.toFixed(1)}"/>`;
        if (!isDoor) s += `<line x1="${(x + w / 2).toFixed(1)}" y1="${wy.toFixed(1)}" x2="${(x + w / 2).toFixed(1)}" y2="${(wy + wh).toFixed(1)}" opacity="0.4"/>`;
      }
    }
    // dimension line
    s += `<g opacity="0.6"><line x1="${left}" y1="${ground + 16}" x2="${right}" y2="${ground + 16}"/><line x1="${left}" y1="${ground + 11}" x2="${left}" y2="${ground + 21}"/><line x1="${right}" y1="${ground + 11}" x2="${right}" y2="${ground + 21}"/></g>`;
    return s + `</svg>`;
  }

  function fillMedia(el, img, seed, label) {
    el.innerHTML = "";
    if (img) {
      const i = new Image();
      i.decoding = "async";
      i.loading = "lazy";
      i.alt = img.alt || label || "";
      i.addEventListener("load", () => i.setAttribute("data-loaded", ""), { once: true });
      i.addEventListener("error", () => fillMedia(el, null, seed, label), { once: true });
      i.src = img.src;
      el.appendChild(i);
      if (i.complete && i.naturalWidth) i.setAttribute("data-loaded", "");
      return true;
    }
    el.insertAdjacentHTML("beforeend", facadeSVG(seed));
    if (label) {
      const l = document.createElement("span");
      l.className = "media-label";
      l.textContent = label;
      el.appendChild(l);
    }
    return false;
  }

  /* Hero + portrait */
  const heroFig = document.querySelector('[data-slot="hero"]');
  if (fillMedia(heroFig.querySelector("[data-media]"), heroImg, 7, "Titelbild")) {
    heroFig.setAttribute("data-has-image", "");
    if (heroImg.alt) document.querySelector("[data-hero-caption]").textContent = heroImg.alt;
  }
  fillMedia(document.querySelector('[data-slot="portrait"] [data-media]'), portraitImg, 3, "Carsten Günther");

  /* ───────── Projects ───────── */
  const grid = document.querySelector("[data-project-grid]");
  const catLabel = Object.fromEntries(C.categories.map((c) => [c.id, c.label]));
  const projectImages = C.projects.map((p) => (p.image ? { src: p.image, alt: p.title } : nextPhoto()));

  C.projects.forEach((p, i) => {
    const li = document.createElement("li");
    li.className = "project reveal";
    li.dataset.category = p.category;
    if (p.size) li.dataset.size = p.size;
    li.innerHTML = `
      <button class="project-card" type="button" aria-haspopup="dialog">
        <div class="media project-media"></div>
        <div class="project-meta">
          <span class="project-title"></span>
          <span class="project-cat"></span>
        </div>
        <span class="project-more">Details
          <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 6h8M7 3l3 3-3 3" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </button>`;
    li.querySelector(".project-title").textContent = p.title;
    li.querySelector(".project-cat").textContent = catLabel[p.category] || "";
    fillMedia(li.querySelector(".project-media"), projectImages[i], 11 + i * 5, p.title);
    li.querySelector("button").addEventListener("click", () => openProject(i));
    grid.appendChild(li);
  });

  /* Filters */
  const filterWrap = document.querySelector("[data-filters]");
  const counts = C.projects.reduce((m, p) => ((m[p.category] = (m[p.category] || 0) + 1), m), {});
  C.categories.forEach((c) => {
    const n = c.id === "all" ? C.projects.length : counts[c.id] || 0;
    if (!n) return;
    const b = document.createElement("button");
    b.type = "button";
    b.className = "filter";
    b.setAttribute("aria-pressed", c.id === "all" ? "true" : "false");
    b.innerHTML = `<span></span><span class="filter-count">${n}</span>`;
    b.firstChild.textContent = c.label;
    b.addEventListener("click", () => setFilter(c.id, b));
    filterWrap.appendChild(b);
  });
  function setFilter(id, btn) {
    filterWrap.querySelectorAll(".filter").forEach((f) => f.setAttribute("aria-pressed", String(f === btn)));
    grid.querySelectorAll(".project").forEach((li, i) => {
      const show = id === "all" || li.dataset.category === id;
      const wasHidden = li.hidden;
      li.hidden = !show;
      if (show && (wasHidden || id !== "all")) {
        li.removeAttribute("data-entering");
        void li.offsetWidth; // restart animation
        li.style.animationDelay = `${Math.min(i, 5) * 40}ms`;
        li.setAttribute("data-entering", "");
      }
      // in filtered views, wide cards would leave gaps
      li.dataset.size = id === "all" ? C.projects[i].size || "" : "";
    });
  }

  /* Dialog */
  const dlg = document.querySelector("[data-dialog]");
  function openProject(i) {
    const p = C.projects[i];
    dlg.querySelector("[data-dialog-cat]").textContent = catLabel[p.category] || "";
    dlg.querySelector("[data-dialog-title]").textContent = p.title;
    dlg.querySelector("[data-dialog-text]").textContent = p.text;
    const facts = dlg.querySelector("[data-dialog-facts]");
    facts.innerHTML = "";
    [["Ort", p.place], ["Jahr", p.year], ["Leistungen", p.phases]].forEach(([k, v]) => {
      if (!v) return;
      const dt = document.createElement("dt"); dt.textContent = k;
      const dd = document.createElement("dd"); dd.textContent = v;
      facts.append(dt, dd);
    });
    const m = document.createElement("div");
    m.className = "media";
    const holder = dlg.querySelector("[data-dialog-media]");
    holder.replaceChildren(m);
    fillMedia(m, projectImages[i], 11 + i * 5, p.title);
    m.querySelector("img")?.removeAttribute("loading");
    dlg.showModal();
  }
  dlg.querySelector("[data-dialog-close]").addEventListener("click", () => dlg.close());
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });

  /* ───────── Phases accordion ───────── */
  const phases = document.querySelector("[data-phases]");
  C.phases.forEach((ph, i) => {
    const li = document.createElement("li");
    li.className = "phase reveal";
    li.style.setProperty("--d", `${Math.min(i, 8) * 30}ms`);
    li.dataset.open = i === 0 ? "true" : "false";
    li.innerHTML = `
      <button class="phase-btn" type="button" aria-expanded="${i === 0}" aria-controls="ph-${ph.n}">
        <span class="phase-n">LPH ${ph.n}</span>
        <span class="phase-title"></span>
        <span class="phase-icon" aria-hidden="true"></span>
      </button>
      <div class="phase-panel" id="ph-${ph.n}" role="region"><div><p></p></div></div>`;
    li.querySelector(".phase-title").textContent = ph.title;
    li.querySelector("p").textContent = ph.text;
    li.querySelector("button").addEventListener("click", (e) => {
      const open = li.dataset.open !== "true";
      li.dataset.open = String(open);
      e.currentTarget.setAttribute("aria-expanded", String(open));
    });
    phases.appendChild(li);
  });

  /* ───────── Team strip: only when real images exist ───────── */
  const strip = document.querySelector("[data-team-strip]");
  const teamImgs = [];
  for (let k = 0; k < 4; k++) {
    const im = nextPhoto(matches(/team|buero|büro|office/i)) || nextPhoto();
    if (im) teamImgs.push(im);
  }
  if (teamImgs.length >= 2) {
    teamImgs.forEach((im, i) => {
      const li = document.createElement("li");
      li.className = "reveal";
      li.style.setProperty("--d", `${i * 50}ms`);
      const m = document.createElement("div");
      m.className = "media";
      li.appendChild(m);
      fillMedia(m, im, 40 + i, "");
      strip.appendChild(li);
    });
  }

  /* ───────── Header: scrolled state, mobile menu, active section ───────── */
  const header = document.querySelector("[data-header]");
  const onScroll = () => header.dataset.scrolled = String(window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const menuBtn = document.querySelector("[data-menu-btn]");
  const setMenu = (open) => {
    header.dataset.open = String(open);
    menuBtn.setAttribute("aria-expanded", String(open));
  };
  menuBtn.addEventListener("click", () => setMenu(header.dataset.open !== "true"));
  document.querySelectorAll("[data-mobile-nav] a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  const navLinks = [...document.querySelectorAll(".nav a")];
  const sectionObs = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      navLinks.forEach((a) => a.setAttribute("aria-current", String(a.getAttribute("href") === `#${en.target.id}`)));
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  document.querySelectorAll("main section[id]").forEach((s) => sectionObs.observe(s));

  /* ───────── Copy e-mail ───────── */
  const copyBtn = document.querySelector("[data-copy]");
  const hint = document.querySelector("[data-copy-hint]");
  let hintTimer;
  copyBtn.addEventListener("click", async () => {
    const addr = copyBtn.dataset.copy;
    try {
      await navigator.clipboard.writeText(addr);
      hint.textContent = "Kopiert";
    } catch {
      window.location.href = `mailto:${addr}`;
      return;
    }
    hint.removeAttribute("data-flash"); void hint.offsetWidth; hint.setAttribute("data-flash", "");
    clearTimeout(hintTimer);
    hintTimer = setTimeout(() => { hint.textContent = "Kopieren"; hint.removeAttribute("data-flash"); }, 1800);
  });

  document.querySelector("[data-year]").textContent = new Date().getFullYear();

  /* ───────── Scroll reveal ───────── */
  // Stagger siblings that enter together.
  document.querySelectorAll(".hero .reveal").forEach((el, i) => el.style.setProperty("--d", `${i * 70}ms`));
  document.querySelectorAll(".focus-list .reveal, .project-grid .reveal").forEach((el) => {
    const idx = [...el.parentElement.children].indexOf(el);
    el.style.setProperty("--d", `${(idx % 4) * 60}ms`);
  });
  if (reduceMotion || !("IntersectionObserver" in window)) {
    document.querySelectorAll(".reveal").forEach((el) => el.setAttribute("data-in", ""));
  } else {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.setAttribute("data-in", ""); obs.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    document.querySelectorAll(".reveal").forEach((el) => obs.observe(el));
  }
})();
