---
name: rerecord-clip
description: Record or re-record an app's 6 second home page clip (thumb.webp and thumb.png) with tools/record-clips.js and verify it. Use whenever an app's look changes or a new app is added.
---

# Re-record a clip

```bash
export NODE_PATH=$(npm root -g)
node tools/record-clips.js <folder> [<folder> ...]   # no args = every app
```

Needs Node, Playwright and ffmpeg with libwebp. `P5_LIB=/path/p5.min.js` for Stop Building Demos if cdnjs is unreachable. Full option list is in `tools/README.md`.

## Entry options (APPS table)
- `vp` `[1280,769]` gives a 1280x720 stage under the 49px nav; `crop` `[0,49,1280,720]` (16:9). Or `setup(page)` returning a measured rect (`cropOf('#sel')`).
- `run(page)`: timeline via `at(t0, ms, fn)`; first ~700ms stays still. Total ~6.5s.
- `hash: '#clip'`, `ready` (ms to wait), `q` (WebP quality, default 62, lower for grainy apps), `http: true` for apps that iframe another app.
- Use `setup` to park the app in its starting state (e.g. `lp.stop(); bl.stop(); bl.instant()`), then drive it in `run`.

## Verify (always)
1. Read `<folder>/thumb.png` as an image. It must be the clip's first frame and look like the app's starting state, not a half-loaded or mid-transition frame (past fixes were exactly this).
2. Check file size is sane (typically 250-600KB; if larger, lower `q`).
3. The last half second cross-fades to the first frame, so the loop has no jump.
4. Commit `thumb.webp` and `thumb.png` together with the change, then use `ship-to-pages`.
