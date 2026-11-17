---
name: cutout-product-photo
description: Cut a product (box, pouch, tub, plate) out of a flat-coloured studio photo and place it on a brand colour with a soft shadow, with no halo. Use when a design needs a clean masked product image, when the user says to mask out or use a product from a photo, or when a previous mask looks wrong (lime fringe, eaten tape, leftover neighbour, harsh edge).
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

## Other backdrops, several products at once: `cutout_any.py`
`cutout_any.py` (same folder, `pip install opencv-python-headless pillow numpy`, run with `python3 -I`) is a tested command-line tool for the cases the lime-box recipe above does not cover. Copy it to the scratchpad; do not run it from inside a downloaded-images folder.

| Backdrop | Mode | Example |
|---|---|---|
| One hue, even with a cast shadow (lime, mint, green) | `hue` | `--mode hue --hue 20 52 --sat 80` |
| A smooth gradient of one colour, shadow detached | `chroma` | `--mode chroma --tol 0.03` |
| A round object (plate, bowl) | `circle` | `--mode circle --radius 330 390 --hue 24 45 --sat 35 --defringe 0 --erode 0` |

- Hue is OpenCV's 0-179 scale (lime about 28-42, green about 55-75). Measure instead of guessing: print HSV for a backdrop pixel, a shadow pixel and a similar-looking part of the product (pale tape on lime), then set the saturation threshold between them. Pale tape (~120-150) separates from lime backdrop and shadow (~180) on saturation alone.
- `--keep 2 --split` writes `OUT-1.webp`, `OUT-2.webp` left to right. Leave `--split` off for products that touch or overlap (two boxes) and say they stay one image. `--keep 1` also drops a floor shadow in `chroma` mode.
- Edge sliver of backdrop colour: `--strip-hue LO HI --strip-sat N`. Fringe: raise `--defringe`. Jagged: raise `--feather`.
- **Always add `--preview`** and look at `OUT.preview.png` (each product on dark and light), zooming into thin tape ends, pouch corners and zip tabs.

Known good settings for the Grubclub mockups on kristynagottvald.github.io: two pouches `grubclub-09.webp` `--mode hue --hue 20 52 --sat 80 --keep 2 --split`; single box `grubclub-04.webp` `--mode hue --hue 29 43 --sat 163 --strip-hue 30 42 --min-area 100000`; two boxes `grubclub-05.webp` `--mode chroma --tol 0.03 --min-area 100000`; plate screenshot `--mode circle ...` as in the table.

## Get the source image first
An image pasted into chat is not necessarily a file on disk. Check the session's images folder (`ls /tmp/*/-home-user/*/images/`). If it is missing, do not fake the cut-out: find the original (portfolio case-study images are listed in `https://kristynagottvald.github.io/projects.json`, `caseStudyContent[].src`, served from the site root), match it with a contact sheet, or ask for the file. A screenshot of a design is a low-resolution source (a plate cut from one is only ~730 px); say so.

## Using the result in a canvas app
Draw each cut-out "contain" inside a square slot and scale by slot size so differently shaped products share one layout. Compare apparent sizes by eye (tilted products look bigger or smaller than their boxes). Give them a soft canvas shadow (`shadowBlur`, scaled by the canvas scale) rather than keeping the photo's shadow. Keep each file under ~150 KB (`--max-side 1000-1100`). See `canvas-card-maker`.
