---
name: brand-system-page
description: Turn a brand's visual language (type, colour, grid, geometry, motion) into CSS tokens and an on-brand guidelines or landing page in the sandbox style. Use for Thread, Clearco, Grubclub, Postmark, Lob style brand pages, guidelines, visuals or conference landers.
---

# Brand system page

Method that the Thread, Clearco, Grubclub and Postmark projects share:

1. **Read the source of truth first.** Existing brand projects in the repo are the reference: `thread-brand-guidelines`, `thread-brand-visuals`, `thread-conference-landing`, `clearco-*`, `grubclub-*`, `postmark-*`. Reuse their tokens rather than re-inventing; ask the user for the brand assets/screenshots if the brand is new.
2. **Tokens on `:root`.** Colours (with the brand's names), font stacks (`--sans`, `--serif`; italic serif for emphasis is a common device), spacing/grid unit, radius. Never hard-code a colour twice.
3. **Grid and geometry.** Identify the brand's constructive device (hairline grid, tilts, frames, calligraphic loops, 3D capitals) and build it as reusable CSS/SVG/canvas, not images.
4. **Motion style.** Define durations/easing once; keep motion on-brand (e.g. sweeping hairlines, single pop, slower fades). Respect `prefers-reduced-motion`.
5. **Palette switching.** If the brand has several palettes, one control drives every example (CSS variables on a wrapper), including demo stages.
6. **Copy rules.** Voice and tone are part of the page. Obey user edits to wording exactly (dates, names, headline text) and keep them in sync across sections.
7. **Details that bit us before:** clipped type samples (check overflow at every width), things bleeding off the right edge only when intended, drop shadows removed on demo stages if the brand is flat, inline three-colour palette, hero lettering unclipped.
8. Then use `sandbox-add-app` and `rerecord-clip`.
