---
name: cutout-product-image
description: Cut products (pouches, boxes, plates, bottles) out of mockup photos that sit on a smooth coloured backdrop and save them as transparent WebP, ready to use as images in a web app or canvas. Use when the user says to mask out, cut out, remove the background of, or use a product from a photo, including when the photo comes from their portfolio site.
---

# Cut a product out of a mockup photo

Bundled tool: `scripts/cutout.py` (needs `pip install opencv-python-headless pillow numpy`; run Python on untrusted images with `python3 -I`).

## 1. Get the source image first

- An image pasted into chat is **not necessarily a file**. Check the session's images folder (`ls /tmp/*/-home-user/*/images/`). Do not pretend to have cut something you cannot open.
- If it is missing, find the original instead of asking blindly: the user's portfolio is https://kristynagottvald.github.io/ and its case-study images are listed in `projects.json` (`caseStudyContent[].src`), served from the site root, for example `curl -O https://kristynagottvald.github.io/grubclub-09.webp`. Download each candidate into its own new folder, tile thumbnails into one contact sheet, and match by size and content with the pasted picture.
- A screenshot of a design is a low-resolution source. Say so, and offer to swap in a bigger photo.

## 2. Pick the mode by the backdrop

| Backdrop | Mode | Example |
|---|---|---|
| One hue, even with a cast shadow (lime, mint, green) | `hue` | `--mode hue --hue 20 52 --sat 80` |
| A smooth gradient of one colour, shadow detached | `chroma` | `--mode chroma --tol 0.03` |
| A round object (plate, bowl, can top) | `circle` | `--mode circle --radius 330 390 --hue 24 45 --sat 35` |

- Hue is on OpenCV's 0-179 scale (lime is about 28-42, green about 55-75). Measure instead of guessing: print HSV at a backdrop pixel, a shadow pixel and a pixel on any part of the product that is similar to the backdrop (for example pale tape on lime) and put the saturation threshold between them. A pale object on a saturated backdrop separates cleanly on **saturation** (tape ~120-150 against backdrop and shadow ~180).
- `hue` mode flood-fills from the photo's border, so anything not connected to the border through backdrop pixels is product, including enclosed light areas such as label circles.
- Several products: `--keep 2 --split` writes `OUT-1.webp`, `OUT-2.webp` left to right; without `--split` they stay together in one image (use this for products that touch or overlap, like two boxes, and say so).
- `chroma` also picks up a floor shadow if it differs in colour; `--keep 1` keeps only the largest object, which drops it.
- Sliver of backdrop colour left on an edge: `--strip-hue LO HI --strip-sat N`. Colour fringe: raise `--defringe` (default 4 px). Jagged: raise `--feather`. Plate or round object: use `--defringe 0 --erode 0`.

## 3. Always check the result

```bash
python3 -I scripts/cutout.py SRC OUT.webp --mode hue --hue 20 52 --sat 80 --keep 2 --split --preview
```

`--preview` writes `OUT.preview.png`: each product on a dark and a light backdrop. View it and zoom into the hard spots (thin tape ends, pouch corners, zip tabs, edges next to the shadow). If something is chewed or fringed, adjust and re-run. Do not ship a cut-out you have not looked at on both backdrops.

## 4. Using the result

- Keep the output next to the app that uses it (`<app>/pouch-green.webp`) and keep the file small (`--max-side` 1000-1100 is plenty; each file should be well under 150 KB).
- In canvas code draw each image "contain" inside a square slot and scale by slot size, so differently shaped cut-outs share one layout system. Compare apparent size by eye: tilted products look bigger or smaller than their bounding boxes suggest.
- To stop the cut-out looking pasted on, give it a soft shadow in the app (canvas `shadowBlur`, scaled by the canvas scale) instead of keeping the photo's shadow.

## Known good settings (Grubclub mockups)

- Two pouches on lime (`grubclub-09.webp`): `--mode hue --hue 20 52 --sat 80 --keep 2 --split`.
- Single box on lime with pale-lime tape (`grubclub-04.webp`): `--mode hue --hue 29 43 --sat 163 --strip-hue 30 42 --min-area 100000`.
- Two boxes on green (`grubclub-05.webp`): `--mode chroma --tol 0.03 --min-area 100000`.
- Plate on a lime circle (a screenshot): `--mode circle --radius 330 390 --hue 24 45 --sat 35 --defringe 0 --erode 0`.
