---
name: sandbox-visual-check
description: Check a sandbox app in a real headless browser before shipping - serve it locally, drive it with Playwright, take screenshots, read them, and catch console errors and layout problems on desktop and mobile. Use after any visual or interaction change to an app in this repo.
---

# Visual check loop

Playwright and Chromium are pre-installed. With a global install, run scripts as `NODE_PATH=$(npm root -g) node script.js`. Do not run `playwright install`.

## Loop

1. **Serve the repo** from its root in the background, run the check, then stop it:
   ```bash
   (python3 -m http.server 8123 >/dev/null 2>&1 &); sleep 1
   S=<scratchpad dir> NODE_PATH=$(npm root -g) node <scratchpad>/shot.js <app> <section[:scrollOffset]> ...
   pkill -f "http.server 8123"
   ```
   `shot.js` in this skill's folder is a ready-made script: it opens `http://localhost:8123/<app>/#t=2.6`, scrolls to `#<section>` plus an offset, screenshots each to `$S/s_<section><offset>.png` and prints console and page errors. Copy it to the scratchpad and adapt it. Env vars: `W` and `H` set the viewport (default 1440x900), `PFX` prefixes file names.
2. **Read every screenshot** with the Read tool (it shows images). Look for clipped text, overlaps, wrong colours, empty areas, and things that are drawn but not visible against their background (yellow on yellow was a real one). Do not report a change as working from the code alone.
3. **Click through the interactions** in a second script: every chip, slider, input and tile once, taking a screenshot after the ones that change the picture. Print `errors: []` at the end.
4. **Mobile:** run again at `W=390 H=844`. Check nothing scrolls sideways and controls stack.
5. **Animation:** to judge motion, take several screenshots a few hundred milliseconds apart after a click (for example 200, 500, 800 ms) and tile them into one contact sheet with PIL (`from PIL import Image`). Say plainly that you judged motion from stills.
6. **Recorded clips:** ffmpeg cannot decode animated WebP. Use PIL: `im = Image.open('thumb.webp'); im.n_frames; im.seek(i)`.

## Tricks

- **Freeze animation** with a hash like `#t=2.6` (apps in this repo read it) so screenshots are deterministic. Open a state directly with `#open=<section>`.
- **Constantly animating elements** make `page.click` time out waiting for stability. Use `locator.click({ force: true })`, or `domClick` via `page.evaluate`.
- **Canvas apps** wait for fonts: `await p.waitForTimeout(1500)` after load, or `document.fonts.ready`.
- **Hover states and trails:** move the mouse in steps (`mouse.move(x, y, { steps: 6 })`) and screenshot a clipped region (`clip: { x, y, width, height }`) right after.
- **Layout inside a scroll container:** scroll the container (`el.scrollIntoView({ block: 'center' })`), not just the window.
- **Write helper scripts with the file tool** into the scratchpad. A shell command that contains `../` paths can be refused by the safety check.
- If a screenshot looks wrong at a given scroll position, the layout may have moved: scroll to the element with `scrollIntoView` rather than guessing an offset.

## Report

Say what you checked and how (screenshots, which widths, which clicks), what you did not check, and anything that looked off, in plain words.
