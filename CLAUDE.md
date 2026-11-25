# Sandbox repo

Each app is a folder with an `index.html` (single file, no build step), a `thumb.webp` (the 6 second looping home page clip, 960×540) and a `thumb.png` (960×540 still that is the clip's first frame; `tools/record-clips.js` writes both).

**Whenever you add a new app, also add it to the homepage.** The homepage (`/index.html`, laid out like the sketches site) draws its tiles from `/apps.json`:
add an entry at the **top** of the array (tiles are ordered newest first) with `id`, `title`, `category`, `url` (`<folder>/`), `thumbnail` (`<folder>/thumb.png`), `preview` (`<folder>/thumb.webp`) and `alt`.
Make the clip by adding the app to the table in `tools/record-clips.js` and running it (see `tools/README.md`), and re-record the clip whenever the app's look changes.
Also add the app's 72px `<nav class="back">` "SANDBOX / PROJECT NAME" bar linking to `../` (copy it from `location-hero/index.html`), with any app controls in a `<div>` on its right.
Every page needs a favicon: run `python3 tools/favicons.py` (brick mark in the app's own clip colours; the home page has the sandbox cube), then `python3 tools/sync-lob-reel.py`.

**Every new or changed app must be live.** The site is GitHub Pages served from the default branch (`claude/epic-pasteur-fsjjc8`), so pushing a feature branch is not enough:
open a pull request into the default branch, merge it, and confirm the Pages deploy succeeded and the app and its homepage tile are on the live site (https://kristynagottvald.github.io/sandbox/).

**Skills.** Repeatable procedures live in `.claude/skills/` (committed, so every session has them). Use them instead of reconstructing the steps: `sandbox-add-app` (new app, homepage tile), `rerecord-clip` (home page clips), `ship-to-pages` (commit, PR, merge, confirm live, without force-pushing), `sandbox-visual-check` (Playwright screenshots and interaction checks before shipping), `brand-system-page` and `brand-guidelines-site` (brand pages, reusing a generator's engine, tile-to-section transition), `canvas-card-maker` (canvas card tools with timeline, export, themes and ported motions), plus the motion and engine skills in that folder.

**Skills Library is a page, not an app tile.** `skills-library/` has its own "Skills Library" item in the sandbox header nav (on `/index.html` and on the library itself), uses `../styles.css` with the home page's header, 2-column project grid and contact footer, and is not in `apps.json` or `tools/record-clips.js`. Add new skills to its `SKILLS` / `D` data.

**Lob Unwrapped Reel is a generated copy.** `lob-unwrapped-reel/index.html` is built from `lob-unwrapped/index.html` by `tools/sync-lob-reel.py`. Whenever `lob-unwrapped/` changes (any session), run that script, re-record the reel clip, and ship both together. Never hand-edit the reel's index.html.
