---
name: asset-generator-engine
description: Build a live-controls asset generator (banner, social post, end card, image or motion engine) as a single HTML file with multi-format preview and export. Use for Blog Banner Studio, Conference Post Generator, Lifecycle Image Studio, Grubclub End Card style tools.
---

# Asset generator engine

Reference implementations: `blog-banner-studio` (SVG banners), `conference-post-generator` (canvas, PNG + video), `lifecycle-image-engine`, `grubclub-end-card`, `hero-banner-engine`, `postmark-*-engine`.

Shape:
- **State object `S`** (template, format, copy, palette, seed). One `render()` draws everything from `S`; controls only mutate `S` and call it. Seeded generation so results are reproducible.
- **Controls left, preview right**, collapsing to stacked on mobile.
- **Formats:** support the real set (1:1, 4:5, 16:9, 9:16, 2:1) from one layout function that takes width/height; stacked layouts for tall formats (bigger headline badges and photos).
- **Brand constraints in code, not in the user's hands:** fixed palettes, one safe line colour per background, foreground centred on the vertical thirds. No free colour picking unless asked.
- **Photos:** upload, delete, reorder, reset-all. Reserve a slot when no photo.
- **Export:** PNG via `canvas.toBlob`, SVG copy, and for motion `MediaRecorder` on `canvas.captureStream(30)` (webm vp9, feature-detect and fall back to PNG with a status message). Downloads may be blocked in iframes; offer Copy as well.
- **Motion in exports:** loops must finish, not cut off (calligraphy finishes drawing; record a whole cycle). Align text to the logo edge; badges that overlap a bar need explicit z-order.
- Sanity-check every format by screenshotting each one (Playwright) before shipping.
