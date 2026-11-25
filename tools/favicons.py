"""Writes a favicon <link> into every app page: the home page gets the sandbox cube, Brickanta Enterprise its brick,
and every other app a small flat glyph taken from what that app itself shows (Klir's drop, Lob's stamp, Thread's loop ...).
Run: python3 tools/favicons.py   then python3 tools/sync-lob-reel.py (the reel is a generated copy of lob-unwrapped).
To give a new app an icon, add a line to ICONS: id -> (background, svg shapes on a 64 x 64 grid)."""
import json
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'


def R(x, y, w, h, c):
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x, y, w, h, c)


def P(d, c):
    return '<path fill="%s" d="%s"/>' % (c, d)


def C(x, y, r, c):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (x, y, r, c)


def L(d, c, w):
    return '<path fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="miter" d="%s"/>' % (c, w, d)


def stamp(bg, fg):
    pts = ''.join(C(x, y, 3, bg) for x in range(14, 52, 8) for y in (10, 54)) + ''.join(C(x, y, 3, bg) for y in range(14, 52, 8) for x in (10, 54))
    return R(8, 8, 48, 48, fg) + pts + R(16, 16, 32, 32, bg) + R(24, 24, 16, 16, fg)


DROP = 'M32 8C32 8 16 28 16 40a16 16 0 0 0 32 0C48 28 32 8 32 8Z'
STAR8 = ''.join(L('M32 8V56', '#e8f066', 7) if False else '' for _ in range(1))

ICONS = {
    'lob-visual-editor': ('#2b2d83', R(10, 15, 44, 34, '#3f33f2') + R(34, 15, 20, 34, '#a28bff') + R(15, 21, 14, 5, '#e4ee5c') + R(15, 31, 14, 3, '#ffffff')),
    'brickanta-enterprise': ('#0e1f4c', P('M14 14H38L50 26V50H26L14 38Z', '#e8584f')),
    'brickanta-enterprise-visuals': ('#e8584f', P('M14 14H38L50 26V50H26L14 38Z', '#0e1f4c')),
    'lob-12-days-unwrap': ('#1e2247', R(12, 14, 40, 40, '#8263fd') + R(29, 14, 6, 40, '#1e2247') + R(12, 31, 40, 6, '#1e2247') + L('M32 33C24 22 16 24 18 30C20 35 28 34 32 33C36 34 44 35 46 30C48 24 40 22 32 33Z', '#1e2247', 4)),
    'lob-12-days': ('#E64A89', stamp('#E64A89', '#fbe3ef')),
    'lob-12-days-linkedin': ('#0a66c2', stamp('#0a66c2', '#ffffff')),
    'lob-unwrapped': ('#3b2cf0', stamp('#3b2cf0', '#ffffff')),
    'lob-unwrapped-reel': ('#000000', stamp('#000000', '#8b5cf6')),
    'lob-get-started': ('#12143a', R(8, 10, 34, 24, '#e4ee5c') + R(16, 20, 34, 24, '#d045dc') + R(24, 30, 34, 24, '#4131f1')),
    'lob-integrations-hero': ('#14163f', ''.join(P('M32 6L38 12H46L48 20L56 26L52 34L56 42L48 48L46 56H38L32 62L26 56H18L16 48L8 42L12 34L8 26L16 20L18 12H26Z', '#5b45f5') for _ in [0]) + C(32, 34, 13, '#14163f') + R(29, 22, 6, 24, '#ffffff')),
    'brand-guidelines-settings': ('#10102a', R(10, 10, 20, 20, '#ffffff') + R(34, 10, 20, 20, '#4a3df0') + R(10, 34, 20, 20, '#4a3df0') + R(34, 34, 20, 20, '#22225a')),
    'clearco-paid-ad-pipeline': ('#000000', ''.join(C(round(32 + 19 * __import__('math').cos(a * 0.7854), 1), round(32 + 19 * __import__('math').sin(a * 0.7854), 1), 4.2, '#ffffff') for a in range(1, 8))),
    'clearco-attribution-guide': ('#04070f', R(8, 14, 36, 8, '#3a8bff') + R(20, 28, 36, 8, '#3a8bff') + R(12, 42, 28, 8, '#9fc4ff')),
    'clearco-logistics-motion': ('#000000', L('M12 12H52V52H12Z', '#555', 2.5) + R(30, 18, 4, 28, '#ffffff') + R(18, 30, 28, 4, '#ffffff')),
    'clearco-logistics-guide': ('#000000', L('M14 8V56M8 20H56', '#777', 2.5) + R(22, 26, 28, 8, '#ffffff') + R(22, 40, 18, 8, '#ffffff')),
    'clearco-terrain': ('#161616', L('M8 20V8H20M44 8H56V20M56 44V56H44M20 56H8V44', '#ffffff', 4)),
    'clearco-target-frame': ('#101010', R(29, 12, 6, 40, '#ffffff') + R(12, 29, 40, 6, '#ffffff')),
    'porcupine-glitch': ('#ffffff', P('M32 6L38 24L58 14L44 30L60 40L40 40L46 58L32 44L18 58L24 40L4 40L20 30L6 14L26 24Z', '#0a0a0a') + R(14, 44, 36, 6, '#ff2a1a')),
    'postmark-awards-brand-visuals': ('#000000', stamp('#000000', '#ffd23f')),
    'postmark-awards-motion': ('#3b2cf0', R(8, 10, 48, 9, '#ffffff') + R(8, 24, 48, 9, '#ffffff') + R(8, 38, 48, 9, '#ffffff') + R(8, 52, 30, 6, '#ffffff')),
    'postmark-ribbon-engine': ('#6a3df0', P('M0 20L44 0H64L0 40Z', '#ff7a3d') + P('M0 44L64 12V32L0 64Z', '#ff7a3d') + P('M24 64L64 44V64Z', '#ff7a3d')),
    'klir-landing-page': ('#ffffff', P(DROP, '#3b3bef')),
    'klir-landing-page-side-reveal': ('#3b3bef', P(DROP, '#ffffff')),
    'klir-image-styles': ('#14163f', P(DROP, '#7d7dff')),
    'hob-social-studio': ('#000000', R(6, 10, 52, 10, '#fff3c4') + R(6, 27, 40, 10, '#ff3b1f') + R(6, 44, 52, 10, '#fff3c4')),
    'hob-pattern-generator': ('#2a0a0c', R(6, 10, 30, 9, '#f3e9a8') + R(28, 24, 30, 9, '#f3e9a8') + R(6, 38, 22, 9, '#f3e9a8') + R(36, 50, 22, 7, '#f3e9a8')),
    'sander-troubleshoot': ('#2f7cf6', P('M8 10H56V42H30L18 54V42H8Z', '#ffffff') + R(16, 20, 28, 5, '#2f7cf6') + R(16, 30, 18, 5, '#2f7cf6')),
    'thread-brand-visuals': ('#fff07a', R(12, 12, 40, 40, '#111111') + R(24, 24, 16, 16, '#fff07a')),
    'thread-conference-landing': ('#f7f1d4', L('M14 44C14 22 50 22 50 40C50 54 30 52 30 38C30 28 44 28 44 36', '#111111', 5)),
    'thread-brand-guidelines': ('#fff07a', R(8, 8, 24, 24, '#111111') + R(32, 32, 24, 24, '#111111') + R(32, 8, 24, 24, '#ffffff') + R(8, 32, 24, 24, '#ffffff')),
    'thread-live-session': ('#fff07a', C(32, 32, 20, '#111111') + C(32, 32, 9, '#ff3b1f')),
    'conference-post-generator': ('#f7f1d4', P('M14 54V30C14 14 50 14 50 30V54Z', '#ffd84a') + L('M14 54V30C14 14 50 14 50 30V54Z', '#111111', 3.5) + R(26, 32, 12, 4, '#111111')),
    'asterisk': ('#000000', R(28, 6, 8, 52, '#5affc0') + P('M8 19L14 15L56 45L50 49Z', '#5affc0') + P('M56 19L50 15L8 45L14 49Z', '#5affc0')),
    'paid-ad-pipeline': ('#0a66c2', R(12, 24, 8, 28, '#ffffff') + R(12, 12, 8, 8, '#ffffff') + R(26, 24, 8, 28, '#ffffff') + R(26, 24, 26, 8, '#ffffff') + R(44, 24, 8, 28, '#ffffff')),
    'nlp-diagram': ('#2f7cf6', L('M18 20L46 20M18 20L32 46M46 20L32 46', '#ffffff', 3) + R(10, 12, 16, 16, '#ffffff') + R(38, 12, 16, 16, '#ffffff') + R(24, 38, 16, 16, '#ffd84a')),
    'mavenoid-hero': ('#3a7ed4', R(10, 14, 44, 36, '#ffffff') + C(25, 32, 8, '#f96442') + R(38, 23, 12, 7, '#f9e898') + R(38, 34, 12, 7, '#f9e898')),
    'grid-alphabet': ('#c9c9c9', R(14, 8, 36, 10, '#111') + R(14, 8, 10, 24, '#111') + R(14, 27, 36, 10, '#111') + R(40, 27, 10, 28, '#111') + R(14, 46, 36, 10, '#111')),
    'location-hero': ('#4a3df0', P('M32 6C20 6 12 15 12 26C12 40 32 58 32 58C32 58 52 40 52 26C52 15 44 6 32 6Z', '#ffffff') + C(32, 26, 8, '#4a3df0')),
    'arrow-line-generator': ('#050505', L('M12 52L50 14M24 14H50V40', '#ff3b2a', 7)),
    'brand-audit-engine': ('#14143a', L('M26 14C18 14 22 32 14 32C22 32 18 50 26 50M38 14C46 14 42 32 50 32C42 32 46 50 38 50', '#ff8a3d', 5)),
    'agentic-storefront': ('#111111', P('M12 8H52V46H30L18 56V46H12Z', '#ffffff') + R(20, 18, 24, 5, '#111111') + R(20, 29, 16, 5, '#111111')),
    'ilg-pixel-globe': ('#000000', ''.join(R(8 + 8 * i, 8 + 8 * j, 6, 6, '#ffffff') for i in range(7) for j in range(7) if (i - 3) ** 2 + (j - 3) ** 2 <= 10)),
    'human-tech-motion': ('#cfcfcf', C(26, 30, 18, '#f6c42f') + R(34, 34, 22, 22, '#e2342c')),
    'workout-year-reels': ('#2a66f5', C(26, 28, 16, '#ffffff') + C(38, 28, 16, '#ff7a3d') + C(32, 40, 16, '#0f2a66')),
    'grubclub-holiday': ('#0f2a4a', R(8, 8, 24, 24, '#e8f066') + R(32, 8, 24, 24, '#1f7a4a') + R(8, 32, 24, 24, '#1f7a4a') + R(32, 32, 24, 24, '#e8f066') + C(20, 20, 7, '#1f7a4a') + C(44, 44, 7, '#1f7a4a')),
    'grubclub-order': ('#0f3b2a', P('M10 50C10 24 30 10 54 10C54 36 40 54 10 50Z', '#a8e063') + L('M12 48L40 24', '#0f3b2a', 3.5)),
    'grubclub-end-card': ('#a8e8c8', R(14, 12, 36, 40, '#1f7a4a') + C(32, 28, 10, '#ffd84a')),
    'flavor-all-stars': ('#1f3b2a', P('M32 6L38 24L58 24L42 36L48 56L32 44L16 56L22 36L6 24L26 24Z', '#e8f066')),
    'lifecycle-image-engine': ('#14143a', P('M10 54L14 40L42 12L52 22L24 50Z', '#f7e96b') + P('M42 12L48 6L58 16L52 22Z', '#e85cf0')),
    'prompt-demos': ('#cfe3f7', P('M32 6L38 26L58 32L38 38L32 58L26 38L6 32L26 26Z', '#111111')),
    'video-synopsis': ('#10131a', P('M4 32C14 18 50 18 60 32C50 46 14 46 4 32Z', '#ffffff') + C(32, 32, 9, '#10131a') + L('M20 18V12H28M44 12H52V18M52 46V52H44M28 52H20V46', '#f6c42f', 3)),
    'hero-banner-engine': ('#14143a', R(8, 8, 16, 16, '#5b6bff') + R(24, 8, 16, 16, '#ffd84a') + R(40, 8, 16, 16, '#ff7ad9') + R(8, 24, 16, 16, '#ffd84a') + R(24, 24, 16, 16, '#ff7ad9') + R(40, 24, 16, 16, '#5b6bff') + R(8, 40, 16, 16, '#ff7ad9') + R(24, 40, 16, 16, '#5b6bff') + R(40, 40, 16, 16, '#ffd84a')),
    'blog-banner-studio': ('#6a4cf5', R(8, 14, 48, 36, '#ffffff') + R(14, 20, 24, 6, '#6a4cf5') + R(14, 30, 36, 14, '#d4ccff')),
    'ab-testing': ('#0e1116', R(10, 24, 18, 32, '#6f9bff') + R(36, 38, 18, 18, '#8a8f99') + R(10, 10, 44, 4, '#2a2f38')),
}


def svg(bg, body):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="%s"/>%s</svg>' % (bg, body)


def link(svgtxt):
    return '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%s">' % urllib.parse.quote(svgtxt, safe="/:=,' ")


CUBE = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect width="200" height="200" rx="28" fill="#151515"/>'
        '<path fill="#f4f4f4" d="M100 28L162 64V136L100 172L38 136V64Z"/>'
        '<path fill="none" stroke="#151515" stroke-width="9" stroke-linejoin="miter" d="M38 64L100 100L162 64M100 100V172"/></svg>')


def put(path, tag, indent=''):
    s = open(path, errors='ignore').read()
    s = re.sub(r'\n?[ \t]*<link rel="icon"[^>]*>', '', s)
    m = re.search(r'</title>', s)
    assert m, path
    s = s[:m.end()] + '\n' + indent + tag + s[m.end():]
    open(path, 'w').write(s)


if __name__ == '__main__':
    apps = json.load(open(ROOT + 'apps.json'))
    missing = [a['id'] for a in apps if a['id'] not in ICONS]
    assert not missing, 'add an ICONS entry for: %s' % missing
    for a in apps:
        bg, body = ICONS[a['id']]
        put(ROOT + a['id'] + '/index.html', link(svg(bg, body)))
    put(ROOT + 'index.html', link(CUBE), '  ')
    put(ROOT + 'skills-library/index.html', link(CUBE), '  ')  # the library is a sandbox page (own nav item), not an app tile
    print(len(apps))
