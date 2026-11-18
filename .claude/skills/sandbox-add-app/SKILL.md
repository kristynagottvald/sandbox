---
name: sandbox-add-app
description: Add a new app to the sandbox repo end to end: single-file index.html, back-nav bar, apps.json tile, record-clips.js entry and the thumb.webp/thumb.png. Use whenever the user asks for a new app, tool, engine, page or animation in this repo.
---

# Add a sandbox app

Follow in order. Every step is required (see /CLAUDE.md).

1. **Folder + page.** `<folder>/index.html`, one file, no build step, no framework. Kebab-case folder name. Assets (photos, images) sit beside it.
2. **Back nav.** First element in `<body>`, a 49px bar (the clip crop and the 1280x769 viewport assume 49px). Copy it from `location-hero/index.html` (`nav.back` CSS and markup): `Sandbox / Back to all projects / <b>Title</b>`, both links `href="../"`. Hide `.x` items under 640px.
3. **Clip hooks.** If the app animates on its own or has timelines, make it recordable: honour `#clip` in `location.hash` (adds a `clip` class that hides chrome, loops, or starts at the first frame) and expose a small `window.__rb`/`window.__pp`-style object (`play`, `seek`, `pause`) so the recorder can drive it. See `sander-troubleshoot/index.html` (`CLIP`, `window.__rb`).
4. **Recorder entry.** Add the app to `APPS` in `tools/record-clips.js` (vp `[1280,769]`, crop `[0,49,1280,720]`, `run` timeline; leave the first ~700ms alone, clip is ~6.5s). Use the `rerecord-clip` skill to run it and check the result.
5. **Homepage.** Add an object at the **top** of `/apps.json` (newest first): `id` (= folder), `title`, `category` (one of Motion, Interactive Engine, Mini Site, Tools, Landing Page, Email, Mockup), `url` (`<folder>/`), `thumbnail` (`<folder>/thumb.png`), `preview` (`<folder>/thumb.webp`), `alt` (one long, concrete sentence describing what the clip shows).
6. **README.** Add the project to the category row in `/README.md`.
7. **Ship.** Use the `ship-to-pages` skill. The app is not done until it and its tile are live.

Check before finishing: mobile width (no horizontal scroll), `file://` works, nav links back, `thumb.png` is the clip's first frame.
