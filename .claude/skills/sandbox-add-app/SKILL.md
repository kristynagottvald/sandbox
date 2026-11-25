---
name: sandbox-add-app
description: Add a new app to the sandbox repo end to end: single-file index.html, back-nav bar, apps.json tile, record-clips.js entry and the thumb.webp/thumb.png. Use whenever the user asks for a new app, tool, engine, page or animation in this repo.
---

# Add a sandbox app

Follow in order. Every step is required (see /CLAUDE.md).

1. **Folder + page.** `<folder>/index.html`, one file, no build step, no framework. Kebab-case folder name. Assets (photos, images) sit beside it.
2. **Back nav.** First element in `<body>`, the 72px sandbox project bar, the same height as the home page nav (the clip crop and the 1280x792 viewport assume 72px). Copy it from `location-hero/index.html`: the `nav.back` markup `<a href="../">Sandbox</a><span>/</span><b>Title</b>` (SANDBOX / PROJECT NAME in the all-caps label style), plus its base `nav.back` rules and the `sandbox project bar` override block. Any app controls that belong in the bar go in one `<div>` after the `<b>`; the block pushes it to the right. On phones (≤640px) those controls move to a panel under the visual: copy the `sb-panel` CSS lines and the closing `sandbox project bar` script from `nlp-diagram/index.html`; if the panel should follow something other than the element after the bar, set `data-panel-after="<selector>"` on the nav.
3. **Clip hooks.** If the app animates on its own or has timelines, make it recordable: honour `#clip` in `location.hash` (adds a `clip` class that hides chrome, loops, or starts at the first frame) and expose a small `window.__rb`/`window.__pp`-style object (`play`, `seek`, `pause`) so the recorder can drive it. See `sander-troubleshoot/index.html` (`CLIP`, `window.__rb`).
4. **Recorder entry.** Add the app to `APPS` in `tools/record-clips.js` (vp `[1280,792]`, crop `[0,72,1280,720]`, `run` timeline; leave the first ~700ms alone, clip is ~6.5s). Use the `rerecord-clip` skill to run it and check the result.
5. **Homepage.** Add an object at the **top** of `/apps.json` (newest first): `id` (= folder), `title`, `category` (one of Motion, Interactive Engine, Mini Site, Tools, Landing Page, Email, Mockup), `url` (`<folder>/`), `thumbnail` (`<folder>/thumb.png`), `preview` (`<folder>/thumb.webp`), `alt` (one long, concrete sentence describing what the clip shows).
6. **README.** Add the project to the category row in `/README.md`.
7. **Ship.** Use the `ship-to-pages` skill. The app is not done until it and its tile are live.

Check before finishing: mobile width (no horizontal scroll), `file://` works, nav links back, `thumb.png` is the clip's first frame.
