---
name: locale-swap-copy
description: Maintain the data-driven city/market copy swap used by Location Hero and Paid Ad Pipeline (headline, stat blurbs with icons, neighbourhoods, SCF) and keep the two apps in sync. Use when adding a market, editing blurbs, or changing blurb styling.
---

# Locale swap copy

`location-hero/index.html` and `paid-ad-pipeline/index.html` both render three blurb cards from a market table (`CITIES` in location-hero; the paid-ad equivalent sets `b1h..b3p`):
1. `<N> day <i>delivery time</i>` / `Avg. First-Class time in your SCF, <zip range>`
2. `Sending from <i>City, ST</i>` / `<n> mi from your delivery zone, <zip>`
3. `<i>N,NNN</i> homes in your zone` / `<Hood>, <Hood> and <Hood> routes`

Rules:
- Add a market by adding one entry to the table in **both** files with the same facts. Italic serif (`<i>`) marks the variable phrase.
- Each blurb has an icon on the right: mail truck (1), map pin (2), house (3), `class="ic"` SVGs using `currentColor` (lime tile). Change an icon in both files; the supplied mail truck SVG is `viewBox="0 0 47 33"`.
- Both files duplicate the blurb CSS (`.bl`, `.bl .ic`, drift states `data-s`). Edit both, then re-record both clips (`rerecord-clip`) and ship once (`ship-to-pages`).
- Text swaps use the blur transition (`.bi.out`, `.sw`); keep `padding-right` so copy never runs under the icon, and `white-space:nowrap` lines must fit at 1.85cqw.
- Mobile: input and CTA text sized so the form fits.
