---
name: match-reference-screenshot
description: Rebuild a screenshot or reference page as HTML exactly: measure text widths to solve font sizes, match spacing and layout, then verify side by side. Use when the user says "rebuild this exactly", shares a layout/spacing reference, or marks up a screenshot with red/blue annotations.
---

# Match a reference exactly

## Measure first
1. Render each text string in the real font at 100 px inside Playwright (`font:<weight> 100px <family>`, `white-space:nowrap`) and read its width.
2. Font size = (width in the reference) / (width at 100 px) * 100. Do this for every distinct line; sizes usually come out as a few repeating values. Convert the reference to the same coordinate space first (a 2x retina screenshot halves everything).
3. Read the reference for: colours (sample pixels), paddings, gaps, radii, line spacing. Build positions in absolute px on a fixed stage (e.g. 1280x720 scaled to fit).

## Read annotations literally
Red/blue marks on a screenshot mark where space or elements should change; the arrow, circle or line shows direction. Describe your reading in one line when you reply, so a wrong reading is cheap to correct.

## Copy and elements
Borrow structure and copy from a reference, but rewrite for the brand (sentence case, brand voice). Use user-supplied content for real values; invent nothing that looks like fact (addresses, prices) without saying so.

## Verify
Screenshot the build at the reference size and compare regions side by side. Check line breaks too: no widows or orphans (use `text-wrap: balance` for titles, `pretty` for paragraphs, and `&nbsp;` between the last two words of short titles).
