---
name: sandbox-motion-timeline
description: The timeline engine and smoothness check behind the sandbox motion apps (NLP Diagram, Sander Troubleshoot). Use when building or editing a looping motion page, adding scrub controls, tuning easing, or when motion looks jerky.
---

# Sandbox motion timeline

Reference implementations: `nlp-diagram/index.html` (SVG) and `sander-troubleshoot/index.html` (HTML/CSS). Copy the script block and adapt.

## Structure
- **One pure `render(t)`** sets every element's opacity/transform from time `t`. No per-element timers. This is what makes scrubbing, pausing and clip recording work.
- **Cycle:** `T = 9` seconds. The page starts and ends in the finished composition. `t < R0 (0.7)` shows it, `R0..R1 (0.7..1.2)` fades everything out (`rst`), then the build plays from `R1`. Hold the finished state for the last 2-3 seconds. The loop point is therefore seamless.
- **Easing:** `eio` (cubic in-out) for moves and fades, `eob` (ease-out-back) for pops such as check marks. Helpers: `clamp`, `pulse(start, dur)` (a sine bump).
- **Typing:** reveal the text with `clip-path: inset(0 X% 0 0)` (HTML) or a clip rect (SVG), quantise progress to 20 steps (`Math.round(u*20)/20`) so it reads as keystrokes, and blink a caret while typing.
- **Stagger lists:** start item `i` at `base + i*0.1`, 0.3 s each, with a 3px rise.
- **Flying chip:** position = lerp(from, to, eio(p)) minus `arc * sin(pi*p)`, slight rotation and scale easing to 1, fade in at the start and out at landing. On landing, pop the target's check with `eob` and expand a ring: `scale(1 + .3*eio(k))`, opacity `.9*(1-k)` over about 0.55 s.
- **Continuous motion** (sanding, breathing) uses `sin(2*pi*N*t/T)` with **integer N**, so it is continuous across the loop point.

## Page contract
- Nav bar with `#pp` (Play/Pause), `#tl` range slider (0..1000 maps to 0..T), `#replay`. Clicking the art toggles play. Pointer-down on the slider remembers whether it was playing and resumes on change.
- `window.__rb = { play({from, speed, loop}), seek(t), pause(), T }`: `tools/record-clips.js` drives it, typically `__rb.play({ from: 0, speed: 1.4, loop: false })` for a 6.4 s clip.
- `#clip` in the URL hash adds `html.clip` (tighter padding) and disables autoplay.
- Honour `prefers-reduced-motion`: do not autoplay, show `t = 0` (finished composition).

## Smoothness check (do this after tuning any motion)
Jerk usually comes from trains of overlapping `pulse()` calls (one kick per event). Fix it with one eased lift: `lift = eio(clamp((t-a)/d1)) * (1 - eio(clamp((t-b)/d2)))`, with an optional slow sine scaled by `lift`.

Measure it instead of eyeballing:
```js
// in Playwright, page loaded with #clip
const o=[]; for(let t=0;t<9;t+=1/30){ __rb.seek(t); o.push(+/rotate\(([-\d.e]+)/.exec(el.getAttribute('transform'))[1]); }
let mx=0; for(let i=2;i<o.length;i++) mx=Math.max(mx,Math.abs(o[i]-2*o[i-1]+o[i-2]));  // max second difference, degrees/frame^2
```
Under about 0.2 degrees per frame squared reads as smooth for small rotations; the NLP Diagram arm went from visibly kicking to 0.13. Check translation the same way in px.

Then re-record the clip (`sandbox-ship-app`) since the look changed.
