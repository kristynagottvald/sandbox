"""Writes a favicon <link> (the brick mark coloured from each app's thumb.png) into every app page and the cube into the home page.
Run: python3 tools/favicons.py   (re-run after changing an app's look; run tools/sync-lob-reel.py afterwards)"""
import colorsys
import json
import os
import re
import urllib.parse

from PIL import Image

ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))) + '/'


def hexc(c):
    return '#%02x%02x%02x' % tuple(c)


def sat(c):
    r, g, b = [v / 255 for v in c]
    return colorsys.rgb_to_hsv(r, g, b)[1]


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def palette(png):
    im = Image.open(png).convert('RGB').resize((160, 90))
    q = im.quantize(10, method=Image.MEDIANCUT)
    pal = q.getpalette()[:30]
    cols = [tuple(pal[i * 3:i * 3 + 3]) for i in range(10)]
    counts = sorted(q.getcolors(), reverse=True)  # (count, index)
    return [(n, cols[i]) for n, i in counts]


def pick(pal):
    bg = pal[0][1]
    best, score = None, -1
    for n, c in pal[1:]:
        d = dist(c, bg)
        if d < 70:
            continue
        sc = (0.35 + sat(c)) * d * (n ** 0.25)
        if sc > score:
            best, score = c, sc
    if best is None:
        best = (255, 255, 255) if lum(bg) < 128 else (20, 20, 20)
    return bg, best


def svg(bg, fg):
    # a 64 unit tile with the brick: a square with two opposite corners cut at 45 degrees
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="%s"/>'
            '<path fill="%s" d="M14 14H38L50 26V50H26L14 38Z"/></svg>') % (bg, fg)


def link(svgtxt):
    return '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%s">' % urllib.parse.quote(svgtxt, safe="/:=,' ")


CUBE = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="28" fill="#151515"/>'
        '<path fill="#f4f4f4" d="M100 28L162 64V136L100 172L38 136V64Z"/>'
        '<path fill="none" stroke="#151515" stroke-width="9" stroke-linejoin="miter" d="M38 64L100 100L162 64M100 100V172"/></svg>')

apps = json.load(open(ROOT + 'apps.json'))
sheet = []
for a in apps:
    f = ROOT + a['id'] + '/index.html'
    s = open(f, errors='ignore').read()
    if a['id'] == 'brickanta-enterprise':
        bg, fg = '#0e1f4c', '#e8584f'
    else:
        b, c = pick(palette(ROOT + a['id'] + '/thumb.png'))
        bg, fg = hexc(b), hexc(c)
    tag = link(svg(bg, fg))
    s = re.sub(r'\n?<link rel="icon"[^>]*>', '', s)
    m = re.search(r'</title>', s)
    assert m, a['id']
    s = s[:m.end()] + '\n' + tag + s[m.end():]
    open(f, 'w').write(s)
    sheet.append((a['id'], bg, fg))

h = open(ROOT + 'index.html').read()
h = re.sub(r'\n?\s*<link rel="icon"[^>]*>', '', h)
m = re.search(r'</title>', h)
h = h[:m.end()] + '\n  ' + link(CUBE) + h[m.end():]
open(ROOT + 'index.html', 'w').write(h)

print(len(sheet))
