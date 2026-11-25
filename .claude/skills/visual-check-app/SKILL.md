---
name: visual-check-app
description: Look at a sandbox app the way a visitor would before publishing: headless Chromium screenshots of each scene, frame strips for timing and loops, and measured element positions. Use after any visual or motion change, before committing, and whenever the user reports spacing, alignment, jumping or animation problems.
---

# Visual check for a sandbox app

Never publish a look change you have not seen. Playwright is preinstalled: run with `NODE_PATH=$(npm root -g) node file.js` (never `playwright install`). Keep scratch scripts in the scratchpad, not in the repo.

## 1. Screenshot a scene
Viewport `1280x792` (the 72px nav bar leaves a 1280x720 stage). Open `file:///.../<app>/index.html`, trigger the scene (a nav button, `?park`, or a hook such as `window.gc`), wait for it to settle, then `page.screenshot({path})`. Read the PNG and compare with the request. Screenshot after each edit, not just at the end.

## 2. Timing and loops (frame strip)
Take 6-8 clipped screenshots of the element only (`clip` = its `getBoundingClientRect()` plus a few px) 150-400 ms apart, paste them into one sheet with `PIL` (run Python with `-I`) and read the sheet. Use this for:
- loaders and crawling/looping animations: every frame must show something (no empty gap between cycles);
- transitions: sample the header, banner and bottom bar through a scene change and confirm they never fade;
- "does not animate" requests: read a transform before and after 1.5 s and compare for equality.

## 3. Measure, do not eyeball
When something must "be in the same place" in two states (inactive and active button, title before and after an address is typed), evaluate `getBoundingClientRect()` in both states and print the numbers. Also print the offset from the parent's centre for "centred" requests.

## 4. Whole-loop smoke test
Poll the active `.scene` id every 400 ms for one full loop, record the order visited, and print `pageerror` and console errors. The list of scenes visited must match the intended story and errors must be empty.

## 5. Things the sandbox blocks
Outbound hosts such as `tile.openstreetmap.org` are refused. Intercept with `context.route('**/host/**', r => r.fulfill(...))` and serve a stand-in image so the layout can still be checked. Say in the summary that the real data was not seen.

## Reporting
Say what was checked (screens, states, measurements) and what was not (live site in a normal browser, real network data).
