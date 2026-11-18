#!/usr/bin/env python3
"""Regenerate lob-unwrapped-reel/index.html from lob-unwrapped/index.html.
The reel is the same page forced to a 9:16 stage with only the progress bars.
Run after ANY change to lob-unwrapped/index.html, then re-record the clip:
  python3 tools/sync-lob-reel.py && NODE_PATH=$(npm root -g) node tools/record-clips.js lob-unwrapped-reel
"""
s = open('lob-unwrapped/index.html').read()
def rep(a, b):
    global s
    assert a in s, 'source changed, update the transform: ' + a[:60]
    s = s.replace(a, b)
rep('.stage{position:relative;flex:none;width:min(100vw,calc((100dvh - 49px)*16/9));height:min(calc(100dvh - 49px),calc(100vw*9/16));',
    '.stage{position:relative;flex:none;width:min(100vw,calc((100dvh - 49px)*9/16));height:min(calc(100dvh - 49px),calc(100vw*16/9));')
rep('@media(max-aspect-ratio:1/1){.stage{width:100vw;height:calc(100dvh - 49px)}}\n', '')
rep('<title>Lob Unwrapped</title>', '<title>Lob Unwrapped Reel</title>')
rep('<b>Lob Unwrapped</b></nav>', '<b>Lob Unwrapped Reel</b></nav>')
rep('lob-unwrapped/thumb.png', 'lob-unwrapped-reel/thumb.png')
rep('.clip .toast{display:none}', '.clip .toast{display:none}\n/* standalone reel: just the 9:16 picture and its progress bars */\n#hShare,.dock{display:none!important}\nbody{align-items:center}')
open('lob-unwrapped-reel/index.html', 'w').write(s)
