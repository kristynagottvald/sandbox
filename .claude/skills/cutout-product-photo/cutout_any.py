#!/usr/bin/env python3
"""Cut products out of a mockup photo with a smooth backdrop into transparent WebP files.

  python3 cutout_any.py SRC OUT.webp --mode hue    --hue 20 52 --sat 80      # backdrop of one hue (lime, green...), shadows included
  python3 cutout_any.py SRC OUT.webp --mode chroma --tol 0.03                # backdrop that is a smooth gradient of one colour
  python3 cutout_any.py SRC OUT.webp --mode circle --radius 330 390          # a round object (plate, bowl): fit the circle

Common options: --keep N (largest N objects), --split (one file per object, left to right: OUT-1.webp ...),
--min-area, --erode PX, --feather SIGMA, --defringe PX, --max-side PX, --pad PX, --preview (writes OUT.preview.png).
Needs: pip install opencv-python-headless pillow numpy
"""
import argparse, sys, os
import cv2, numpy as np
from PIL import Image

def fit_background(im, band=30):
    """Quadratic surface per channel, fitted to the outer band of the photo (the backdrop gradient)."""
    h, w = im.shape[:2]; ys, xs = np.mgrid[0:h, 0:w]
    m = np.zeros((h, w), bool); m[:band] = m[-band:] = True; m[:, :band] = m[:, -band:] = True
    def basis(x, y): return np.stack([np.ones_like(x), x, y, x * x, y * y, x * y], 1)
    X = basis(xs[m] / w, ys[m] / h); F = basis(xs.ravel() / w, ys.ravel() / h)
    out = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        co = np.linalg.lstsq(X, im[..., c][m].astype(np.float64), rcond=None)[0]
        out[..., c] = (F @ co).reshape(h, w)
    return out

def objects_from_background(bg, min_area):
    """Everything not connected to the border through backdrop pixels is an object (this also fills holes inside it)."""
    n, lab = cv2.connectedComponents(bg.astype(np.uint8), connectivity=4)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fg = (~np.isin(lab, list(border))).astype(np.uint8)
    n2, l2, st, cen = cv2.connectedComponentsWithStats(fg, connectivity=8)
    comps = [(i, st[i, cv2.CC_STAT_AREA], cen[i][0]) for i in range(1, n2) if st[i, cv2.CC_STAT_AREA] >= min_area]
    return l2, comps

def fit_circle(im, rmin, rmax, bgmask):
    g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (9, 9), 2)
    cs = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, dp=1, minDist=max(rmin, 50), param1=120, param2=40, minRadius=rmin, maxRadius=rmax)
    if cs is None: sys.exit('no circle found: widen --radius')
    cx0, cy0, r0 = cs[0][0]
    if bgmask is None: return cx0, cy0, r0
    # refine: the circle whose rim separates backdrop (outside) from not-backdrop (inside) best
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]; best = None
    for dx in range(-8, 9, 2):
        for dy in range(-8, 9, 2):
            d = np.hypot(xx - (cx0 + dx), yy - (cy0 + dy))
            for r in range(int(r0) - 10, int(r0) + 11, 2):
                sc = bgmask[(d > r + 2) & (d < r + 8)].mean() - bgmask[(d > r - 8) & (d < r - 2)].mean()
                if best is None or sc > best[0]: best = (sc, cx0 + dx, cy0 + dy, r)
    return best[1], best[2], best[3]

def finish(im, keep, a):
    k = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    k = cv2.morphologyEx(k, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    if a.strip_hue:   # backdrop-coloured slivers hugging the outline
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        edge = (k > 0) & (cv2.erode(k, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) == 0)
        sliver = (hsv[..., 0] >= a.strip_hue[0]) & (hsv[..., 0] <= a.strip_hue[1]) & (hsv[..., 1] >= a.strip_sat)
        k[edge & sliver] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(k, connectivity=8)
        if n > 1: k = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    img = im
    if a.defringe:    # repaint the outline band from the interior so no backdrop colour survives
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * a.defringe + 1,) * 2)
        band = ((k > 0) & (cv2.erode(k, ker) == 0)).astype(np.uint8) * 255
        img = cv2.inpaint(im, band, 4, cv2.INPAINT_TELEA)
    if a.erode: k = cv2.erode(k, np.ones((a.erode, a.erode), np.uint8))
    alpha = np.clip(cv2.GaussianBlur(k.astype(np.float32) * 255, (0, 0), a.feather), 0, 255).astype(np.uint8)
    return img, alpha

def save(img, alpha, path, a):
    ys, xs = np.where(alpha > 8); p = a.pad
    y0, y1 = max(0, ys.min() - p), min(alpha.shape[0] - 1, ys.max() + p); x0, x1 = max(0, xs.min() - p), min(alpha.shape[1] - 1, xs.max() + p)
    rgba = np.dstack([cv2.cvtColor(img, cv2.COLOR_BGR2RGB), alpha])[y0:y1 + 1, x0:x1 + 1]
    pil = Image.fromarray(rgba, 'RGBA'); pil.thumbnail((a.max_side, a.max_side), Image.LANCZOS)
    pil.save(path, 'WEBP', quality=92, method=6); print(path, pil.size)
    return pil

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--mode', choices=['hue', 'chroma', 'circle'], required=True)
    ap.add_argument('--hue', type=int, nargs=2, metavar=('LO', 'HI'), help='backdrop hue range, OpenCV scale 0-179 (lime ~ 28-42, green ~ 55-75)')
    ap.add_argument('--sat', type=int, default=80, help='minimum saturation (0-255) for a pixel to count as backdrop')
    ap.add_argument('--tol', type=float, default=0.03, help='chroma mode: max normalised-RGB distance from the fitted backdrop')
    ap.add_argument('--radius', type=int, nargs=2, metavar=('MIN', 'MAX'), default=[100, 600])
    ap.add_argument('--keep', type=int, default=1); ap.add_argument('--split', action='store_true')
    ap.add_argument('--min-area', type=int, default=20000); ap.add_argument('--erode', type=int, default=3)
    ap.add_argument('--feather', type=float, default=1.0); ap.add_argument('--defringe', type=int, default=4)
    ap.add_argument('--strip-hue', type=int, nargs=2, metavar=('LO', 'HI')); ap.add_argument('--strip-sat', type=int, default=135)
    ap.add_argument('--max-side', type=int, default=1100); ap.add_argument('--pad', type=int, default=6); ap.add_argument('--preview', action='store_true')
    a = ap.parse_args()
    im = cv2.imread(a.src, cv2.IMREAD_COLOR)
    if im is None:
        pil = Image.open(a.src).convert('RGB'); im = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)   # formats OpenCV cannot read
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); outs = []
    if a.mode == 'hue':
        if not a.hue: sys.exit('--hue LO HI is required')
        bg = (hsv[..., 0] >= a.hue[0]) & (hsv[..., 0] <= a.hue[1]) & (hsv[..., 1] >= a.sat)
        lab, comps = objects_from_background(bg, a.min_area)
        comps = sorted(sorted(comps, key=lambda c: -c[1])[:a.keep], key=lambda c: c[2])
        masks = [(lab == i).astype(np.uint8) for i, _, _ in comps]
    elif a.mode == 'chroma':
        m = fit_background(im); c = im.astype(np.float32)
        d = np.linalg.norm(c / np.maximum(c.sum(2, keepdims=True), 1) - m / np.maximum(m.sum(2, keepdims=True), 1), axis=2)
        lab, comps = objects_from_background(d < a.tol, a.min_area)
        comps = sorted(sorted(comps, key=lambda c: -c[1])[:a.keep], key=lambda c: c[2])
        masks = [(lab == i).astype(np.uint8) for i, _, _ in comps]
    else:
        bgm = None
        if a.hue: bgm = ((hsv[..., 0] >= a.hue[0]) & (hsv[..., 0] <= a.hue[1]) & (hsv[..., 1] >= a.sat)).astype(np.float32)
        cx, cy, r = fit_circle(im, a.radius[0], a.radius[1], bgm); print('circle', round(float(cx), 1), round(float(cy), 1), round(float(r), 1))
        yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
        masks = [(np.hypot(xx - cx, yy - cy) <= r - 1.0).astype(np.uint8)]
    if not masks: sys.exit('nothing found: check --hue/--sat or lower --min-area')
    groups = [[m] for m in masks] if a.split else [masks]
    base, ext = os.path.splitext(a.out)
    for gi, grp in enumerate(groups):
        keep = np.maximum.reduce(grp)
        img, alpha = finish(im, keep, a)
        path = a.out if len(groups) == 1 else f'{base}-{gi + 1}{ext}'
        pil = save(img, alpha, path, a); outs.append((path, pil))
    if a.preview:   # the product on a dark and a light backdrop: look for fringes and chewed edges
        h = 480; sheet = Image.new('RGB', (sum(int(p.width * h / p.height) * 2 for _, p in outs), h))
        x = 0
        for _, p in outs:
            q = p.resize((int(p.width * h / p.height), h))
            for bgc in ('#12525A', '#EEFB71'):
                b = Image.new('RGBA', q.size, bgc); b.alpha_composite(q); sheet.paste(b.convert('RGB'), (x, 0)); x += q.width
        sheet.save(base + '.preview.png'); print(base + '.preview.png')

if __name__ == '__main__': main()
