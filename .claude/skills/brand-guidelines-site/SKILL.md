---
name: brand-guidelines-site
description: Recipe for building an interactive brand guidelines site in this sandbox from an existing generator app and a reference site (the Thread Brand Guidelines page is the worked example, in thread-brand-guidelines/). Use when asked to build a brand site, guidelines page, or any page that must reuse another app's exact styles, or to reuse its tile-expands-to-section transition.
---

# Brand guidelines site recipe

Worked example: `thread-brand-guidelines/index.html`, built from `conference-post-generator/index.html` and the look of brand.dropbox.com. Read it for working code of everything below.

## 1. Reuse the generator's engine, do not imitate it

The point of a guidelines page is that specimens are the real thing. Take the generator's drawing code (logo paths, calligraphy, prints, badges, templates) and run it in the new page.

- The generator is one file with a script. Slice the engine out (everything before its UI section) with a small Python assemble script: read the generator, take the line range, and concatenate `head.html` + engine + `site.js`. Keep the head and site code in the scratchpad as separate files and write the result into the app folder. Apply small patches to the copy with asserted `str.replace`, and fail loudly if a pattern is missing.
- The engine reads a global state object `S`. Give each canvas its own settings with a wrapper that sets keys, draws, and restores: `withS({ tpl: 'headline', theme: 'ink' }, () => render(ctx, W, H, t, still))`.
- Use one shared animation loop with a surface per canvas (logical size, draw function, `fit()` for devicePixelRatio). Draw only canvases that are on screen (IntersectionObserver), and pass `still = true` for `prefers-reduced-motion`.
- Wait for fonts (`document.fonts.load(...)` for each family used) before the first draw, then clear any caches.
- Copy the photos, logo paths and fonts into the app; do not reach into the generator's folder at runtime.

## 2. Section anatomy (from the reference site)

Each guideline is a section with: a small outlined tag (`01 · Framework`), a big display headline in the brand headline voice, a short intro paragraph, then a demo (stage plus a controls column) and a rules grid (big number or word, one sentence under each). Sections take the colour of their tile. Hairline rail and top and bottom lines draw on when the section opens. Types of demo that worked: live measurement overlay on the real post; a slider from corporate copy to brand copy; logo clear space and a minimum-size warning; an editable type specimen with toggles; swatches that copy a hex and a contrast pairings list; draggable photo prints with filters; a shape picker with PNG download; a scrubbable animation with a timeline.

Rules the user cared about, worth applying by default:
- Annotations (measurements) go in a colour outside the palette (red) so they read as annotation.
- Only list colour pairings that pass AA contrast (4.5:1). Compute it, do not eyeball it.
- Never put a drop shadow in the foreground colour on a ground of the same colour.
- Sharp corners if the brand has them. Title Case and sentence case rules should match what the generator does.
- Any control that recolours the page should recolour every example in that section, not only the first.

## 3. Tile mosaic hero and the expand transition

The hero is a colour tile mosaic; each tile opens its section.

- Lay the mosaic out with CSS grid (15 columns by 9 rows worked for 9 tiles). Each tile has a title and a small illustration; some illustrations are live canvases.
- Wrap each section in a `.panel` (absolute, scrollable, `display:none` until open) inside a flex `#app` stage under the nav and a 64px site header.
- **Open:** measure the tile rect relative to the stage. Add a ghost, a plain full-stage div the colour of the tile, with `clip-path: inset(...)` set to the tile rect and transition `clip-path .85s`. Set the clip to `inset(0)` next frame. After the transition, show the panel (same background colour, so the swap is invisible), remove the ghost, and add an `in` class that fades each child of the section up in a stagger and draws the hairlines.
- **Close (logo click or Escape):** remove `in` so the content fades out, then show a full-stage ghost, hide the panel, transition the clip back to the tile rect, and remove the ghost. Do not clone tile content into the ghost: scaling it looked jumpy and blurry; a plain colour block is smooth.
- Nav links open a section from its own tile; clicking the section you are already in replays its reveal. Lock input (`busy`) while animating.
- Match each section's theme colour to its tile colour so the colour block grows into the page without a jump.
- Hide the mosaic canvases from the draw loop while a section is open.
- Deep link with `#open=<id>` and `#t=` for stills.

## 4. Before you hand it over

Run the `sandbox-visual-check` skill (desktop, 390px, every control clicked), then `sandbox-add-app` for the homepage tile and `rerecord-clip` for the clip, then `ship-to-pages`. For the colour tokens, grid and copy rules shared by the brand pages, see `brand-system-page`.
