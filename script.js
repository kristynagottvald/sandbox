(() => {
  'use strict';

  /* Sandbox home page — the sketches site's script without the hero: cards from apps.json (newest first),
     hover plays a card's clip, phone nav menu and current-section highlight. */

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (s) =>
    String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const CARD_ARROW = '<svg class="card-arrow" width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><path d="M2.3 7.7l5.1-5.1M2.3 2.1h5.5v5.5" fill="none" stroke="currentColor"/></svg>';

  async function load() {
    const list = $('#cards');
    let apps = [];
    try {
      const res = await fetch('apps.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error(res.status);
      apps = (await res.json()).filter((a) => !a.hidden && a.url);
    } catch (err) {
      console.error(err);
    }
    if (!apps.length) { list.innerHTML = '<p class="load-error">Could not load apps.json.</p>'; return; }

    list.innerHTML = apps.map((a) => `<article class="card">
      <a href="${esc(a.url)}" aria-label="${esc(a.title)}">
        <div class="card-media"><img src="${esc(a.thumbnail)}" data-still="${esc(a.thumbnail)}" data-preview="${esc(a.preview || '')}" alt="${esc(a.alt || '')}" loading="lazy"></div>
        <div class="card-meta">
          <h3 class="card-title">${esc(a.title)}</h3>
          <p class="card-sub">${esc(a.category || '')}</p>${CARD_ARROW}
        </div>
      </a>
    </article>`).join('');

    // hover swaps the still for the looping clip (the still is the clip's first frame)
    const play = (e, on) => {
      const a = e.target.closest('.card a');
      if (!a || (e.relatedTarget && a.contains(e.relatedTarget))) return;
      const im = a.querySelector('img');
      if (im.dataset.preview) im.src = on ? im.dataset.preview : im.dataset.still;
    };
    if (!reduced) {
      list.addEventListener('mouseover', (e) => play(e, true));
      list.addEventListener('mouseout', (e) => play(e, false));
    }
  }

  // Phones: the current section's name opens a stacked list of the sections
  const top = $('#top'), jump = $('#nav-jump'), jumpLabel = $('#nav-jump-label');
  const setMenu = (open) => { top.classList.toggle('open', open); jump.setAttribute('aria-expanded', String(open)); };
  jump.addEventListener('click', (e) => { e.stopPropagation(); setMenu(!top.classList.contains('open')); });
  document.addEventListener('click', (e) => { if (!top.contains(e.target)) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });
  top.querySelectorAll('.top-nav a, .status').forEach((a) => a.addEventListener('click', () => setMenu(false)));

  // keep the nav's current section highlighted as you scroll
  const links = [...document.querySelectorAll('.top-nav a')];
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((a) => {
          const on = a.getAttribute('href') === '#' + e.target.id;
          if (on) { a.setAttribute('aria-current', 'true'); jumpLabel.textContent = a.textContent; } else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    ['projects', 'contact'].forEach((id) => { const el = document.getElementById(id); if (el) io.observe(el); });
  }
  addEventListener('scroll', () => { if (scrollY < 120) jumpLabel.textContent = 'Sandbox'; }, { passive: true });

  load();
})();
