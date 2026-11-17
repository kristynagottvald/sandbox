---
name: canvas-card-maker
description: Build or extend a canvas-based brand "card maker" tool in the sandbox (end cards, social tiles, banners) with a timeline, looping preview, video export, aspect ratios, brand themes, headline fitting and ported motions. Use when working on grubclub-end-card or when asked for a similar tool that previews an animated card and exports it. Reference implementation is grubclub-end-card/index.html.
---

# Canvas card maker

Reference: `grubclub-end-card/index.html` (one file). Read the named functions there instead of re-deriving them. Pair with `cutout-product-photo` (product images), `sandbox-visual-check` and `ship-to-pages`.

## Architecture
- **One pure `draw(ctx, W, H, frame, k)`** renders the whole card for a frame number. Preview, scrubbing, looping, video export and homepage-clip recording all call it, so they cannot disagree. Never keep animation state outside `frame` and the settings object `S`.
- Logical size per ratio (16:9 1920x1080, 1:1 1080x1080, 4:5, 3:4 1080x1350/1440, 9:16 1080x1920); the preview canvas is half size and the context is scaled by `k`. Canvas `shadowBlur` is not scaled by transforms, so multiply it by `k`.
- Timeline: 125 frames at 25 fps. Playback loops with a 1 s rest on the finished card (`HOLD`), then restarts; pause stops it. Add a `loop:false` option to the page hook for clip recording. Expose `window.ec = {play, seek, pause}` for `tools/record-clips.js`. Do not autoplay over a `seek()` made by a script.
- Export: draw to an offscreen full-size canvas in real time and record `captureStream(25)` with `MediaRecorder` (mp4 if supported, else webm), one pass plus a 1 s hold. It needs http(s); on `file://` the canvas is tainted, which is fine for local checks.
- Easing: gentle only. Use `sine(x) = .5 - .5*cos(pi*x)` (in-out, no overshoot) for everything the user has called "aggressive"; keep overshoot out of reveals and motions.

## Layout (`layout()`)
One function returns the logo, product zone, headline box and bottom margin per ratio. Wide ratios put logo and headline left and products right; tall ratios stack logo, visual, headline. Tuning rules learned: taller cards push the visual and headline lower (interpolate on `H/W`); anchor the headline block to a bottom line on tall cards and centre it on wide ones; the subheading height is subtracted from the headline's room.
- **Headline fitting** (`wrapText`, `fit`): largest size that fits the box; prefer two lines so the last two words stay together; never leave one word alone on the last line; 16:9 uses an exact line count with a balanced split (small DP minimising the widest line). Decide line counts per layout, not globally.
- Optional subheading under the headline: fixed smaller size, up to two lines, fades in after the last headline word.

## Brand constraints
- When the user gives allowed colour combinations, make them the only themes (`THEMES`) and make the logo single-coloured per combo (as in their panels). Derive anything else from those: the `INV` map picks the other combo a reveal flips to.
- **Take palettes from the reference, not by eye:** sample pixels along a radius of the reference image (print `#RRGGBB` where the colour changes), then check each ring or accent against the theme background. A colour close to the background looks muddy (mid-green rings on a green card); move to brighter limes.
- Product images are transparent cut-outs in `SETS`; each set can override its slot layout (equal-size pouches with one tucked under; box + pouch like the reference). Apparent size matters more than bounding boxes.

## Motions (ported from the Brand Motion sketch)
Grow (one circle that swells and shrinks), Evolve (concentric rings shifting through palette stops, ring count slider), Macro (a circle grows over the card and reveals it in the flipped combo through a clipped second draw). All are functions of `frame`, with speed and scale sliders and a contextual third slider (elasticity or ring count). Motion is always on; default is grow. To port another sketch: fetch its `sketch.js`, read the draw function, re-express it in `frame` terms with integer cycle counts so it loops.
- Circle style: a big accent circle bleeding off the card behind the hero (capped below the logo on tall ratios), hero scaled to ~72% of it, soft shadow. A spinning hero turns slowly (about 26 degrees across the card) and is revealed by a circle expanding from its centre; draw its shadow as a separate disc so the clip does not cut it.

## Check before shipping
Playwright contact sheet of themes x ratios x motion x product set x text lengths (including a long one and a two-word one), at frames 14, 60 and 125 for animations. Look for: text touching the visual, logo crowded by the visual, clipped rings, orphans. Then `sandbox-ship-app` / `ship-to-pages`, re-recording the clip because the panel or default look changed.

## Traps
- A `//` comment at the end of a line that continues with code silently deletes that code (an inline comment once swallowed a `drawImage`). Put comments on their own line.
- Scripted edits: replace helper that asserts the old text occurs exactly once.
- After changing which button is first (for example removing "off"), update the record-clips selectors in the same change.
