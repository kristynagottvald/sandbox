---
name: sandbox-add-app
description: Add a new app to this sandbox repo end to end - the single-file index.html, the back nav bar, the homepage tile in apps.json, the recorded home page clip, then shipping it. Use when the user asks for a new app, tool, page or demo in this repo, or to rework an app's look (which needs the clip re-recorded).
---

# Add an app to the sandbox

Each app is a folder with a single-file `index.html` (no build step), a `thumb.webp` (the 6 second looping clip, 960x540) and a `thumb.png` (960x540 still, the clip's first frame). `tools/record-clips.js` writes both thumbs. This repo's `CLAUDE.md` is the source of the rules; this skill is the procedure.

## Steps

1. **Pick a folder name** in kebab case, the same as the `id`. If the app builds on another app's styles (a brand site from a generator, for example), read that app first and reuse its drawing code rather than imitating it. See `brand-guidelines-site`.
2. **Write `<folder>/index.html`.** Everything inline. Fonts from Google Fonts. Copy the back bar markup and CSS from any existing app (they are identical):
   ```html
   <nav class="back" aria-label="Sandbox"><a href="../">Sandbox</a><span>/</span><a href="../">Back to all projects</a><span>/</span><b>App Title</b></nav>
   ```
   It is 49px tall. Keep every other piece of the layout below it. Put images the app needs in the app's own folder (`<folder>/photos/...`), not in another app's folder, and add credits if they came from Unsplash or similar.
3. **Check it** with the `sandbox-visual-check` skill: desktop and a 390px phone width, console clean, every interaction clicked once.
4. **Add the homepage tile** to `apps.json`: an object at the very top of the array (newest first) with `id`, `title`, `category` (`Tools`, `Motion` and so on, matching existing entries), `url` (`<folder>/`), `thumbnail` (`<folder>/thumb.png`), `preview` (`<folder>/thumb.webp`) and `alt` (a sentence describing what the clip shows). Validate with `node -e "require('./apps.json')"`.
5. **Add the clip recipe** to the `APPS` table in `tools/record-clips.js`. Fields: `vp` (`[1280, 769]` gives a 1280x720 stage under the 49px bar), `crop` (`[0, 49, 1280, 720]` for a full-page app, or `setup: cropOf('#canvas')`), `ready` (ms to wait before recording), `q` (WebP quality, lower for grainy apps), and `run: async (p) => {...}`, a timeline of actions in ms after the page is ready (`at(t0, 900, () => ...)`, `domClick(p, selector)`). The clip is about 6.5 seconds, the first 700 ms should be left alone, and the last half second cross-fades into the first frame, so end near the start state. The existing entries show the patterns: self-playing apps just wait; others click through states.
6. **Record it:** `NODE_PATH=$(npm root -g) node tools/record-clips.js <folder>`. Needs Playwright and ffmpeg with libwebp. Open `<folder>/thumb.png` to confirm the first frame is right. ffmpeg cannot decode animated WebP, so to inspect the clip use Python: `from PIL import Image`, `Image.open('thumb.webp')`, `seek(n)` through a few frames, and paste them into a contact sheet. Clip size should be near the others (about 0.5 to 1.5 MB).
7. **Re-record whenever the app's look changes**, even for a label or colour change on a tile that the clip shows.
8. **Ship it** with the `sandbox-ship` skill, then confirm the app, `thumb.webp`, `thumb.png` and the `apps.json` entry are on the live site.

## Gotchas

- `apps.json` and `tools/record-clips.js` are the two files other sessions edit too. Expect add-at-the-top conflicts and resolve them by keeping both entries.
- Apps that depend on another app's folder at runtime break when it moves. Copy what you need.
- Respect `prefers-reduced-motion` in new apps, and make animated canvases draw only while visible.
- Use a hash parameter such as `#t=2.4` to freeze animation for stills and clip recording, and `#open=<section>` to deep-link a state.
