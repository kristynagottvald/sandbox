---
name: cutout-product-photo
description: Cut a product (box, pouch, tub) out of a flat-coloured studio photo and place it on a brand colour with a soft shadow, with no halo. Use when a design needs a clean masked product image, or when a previous mask looks wrong (lime fringe, eaten tape, leftover neighbour, harsh edge).
---

# Cut out a product from a coloured backdrop

Bundled script: `cutout.py` (box on a lime backdrop). Copy it to the scratchpad and adapt the constants. Run with `python3 -I`.

## Recipe that works
1. **Score the backdrop** per pixel (0..1) from channel relations, not one colour threshold. For lime: `s = clip((g-r-6)/10) * clip((105-b)/25) * clip((g-75)/15)`. Tight thresholds keep the product (tape, tinted shadows) intact. Loose ones eat it.
2. **Flood fill from the image border** over `s > .5` only. This removes the outer backdrop but keeps lime that is *inside* the product (the tape).
3. **Soft edge**: grow the removed region by about 3 px and set alpha from `1 - s` in that ring only.
4. **Remove the fringe**: un-mix edge pixels with the backdrop colour, `(pixel - (1-a)*bg) / a`, so no lime halo survives.
5. **Bite in 1 px and blur ~1 px**, then crop to the alpha bounding box.
6. **Neighbouring products** in the same photo: pick the target by flood-filling a seed point inside it, and paint the others out. Check every corner of the crop.
7. **Place on a flat brand colour** and add two blurred shadows (wide and faint, tight and darker) offset to the lower right, tinted a darker shade of the backdrop colour, not black.

## Check
Composite the result over both a dark navy and a light background and look at the edges at 2x. Look for: fringe, a rough tape end, a stray neighbour sliver, a hard cut at the shadow.

## Choosing the image
Prefer the photo that shows the whole product (portfolio project images such as `grubclub-04/09/12.webp` on kristynagottvald.github.io). Download each into its own new directory first. Do not invent label art; if only some products have art, use only those.

## When a cut-out is the wrong tool
If the product sits on a coloured card anyway, use the original photo inside a circle or rounded mask instead (a mask hides the edge problem entirely).
