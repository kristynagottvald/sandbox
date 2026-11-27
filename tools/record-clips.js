#!/usr/bin/env node
/* Records the 6 second looping home page clip of each app and writes <app>/thumb.webp (and its first frame as <app>/thumb.png).
 *
 *   node tools/record-clips.js                 every app in the table below
 *   node tools/record-clips.js hero-banner-engine blog-banner-studio
 *
 * Needs Node, Playwright (`npm i -D playwright`, or a global install with NODE_PATH set) and ffmpeg with libwebp.
 * Set P5_LIB=/path/to/p5.min.js if the machine cannot reach cdnjs (Stop Building Demos loads p5 from there).
 * See tools/README.md for how to add an app.
 */
const { chromium } = require('playwright');
const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process'), http = require('http');

const ROOT = path.resolve(__dirname, '..') + '/';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const at = async (t0, t, fn) => { const d = t - (Date.now() - t0); if (d > 0) await sleep(d); await fn(); };
const click = async (p, txt) => { try { await p.locator('button').filter({ hasText: txt }).first().click({ timeout: 1500 }); } catch (e) { console.log('  click failed:', txt); } };
/* crop rectangle of an element, forced to 16:9, measured on the page being recorded */
const cropOf = (sel) => async (p) => {
  const r = await p.evaluate((s) => { const b = document.querySelector(s).getBoundingClientRect(); return [b.x, b.y, b.width]; }, sel);
  return [Math.round(r[0]), Math.round(r[1]), Math.round(r[2]), Math.round(r[2] * 9 / 16)];
};
const domClick = (p, sel) => p.evaluate((s) => document.querySelector(s).click(), sel);

/* vp: viewport, crop: [x, y, w, h] in css px (16:9, becomes 960x540), run: timeline of actions (ms after the page is ready).
   Apps that move on their own just wait; the others are driven the way a visitor would use them. */
const APPS = {
  // Wave Tax Weave Walkthrough: the Figma Weave node canvas finishes (Nano Banana origami creatures, headlines, sheet, Buzz counting to 480), the Figma page fills with 480 Buzz frames and zooms out, then the Instagram Reel ad (starts on the filled Weave graph; timeline runs at 2.4x)
  'wave-tax-weave-walkthrough': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, q: 38, run: async (p) => {
    await p.evaluate(() => window.__rb.seek(10.2));
    await sleep(700);
    await p.evaluate(() => window.__rb.play({ from: 10.2, speed: 2.4, loop: false }));
    await sleep(4300);
    await p.evaluate(() => window.__rb.play({ from: 26.1, speed: 1.3, loop: false }));
    await sleep(1500);
  } },
  // Wave File Without Fear, a Wave tax-season landing page: on full-bleed blue, a paper dragon folded from a CRA T1 form holds, then unfolds in 12 fps stop motion into a flat creased sheet (starts on the folded dragon)
  'wave-file-without-fear': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1200, q: 44, run: async (p) => {
    await p.evaluate(() => window.__rb.seek(0));
    await sleep(700);
    await p.evaluate(() => window.__rb.play({ from: 0, speed: 1.05, loop: false, to: 5.95 }));
    await sleep(5800);
  } },
  // Lob Get Started mockup on dark navy: "build your way" around the cycling mail collage, then the page scrolls into the five stacked templates and the middle one opens into the full template preview
  'lob-get-started': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1200, q: 62, run: async (p) => {
    await p.evaluate(() => window.__rb.play());
    await sleep(2500);
    await p.evaluate(() => new Promise((res) => {
      const el = document.getElementById('tpl'), hh = document.querySelector('.top').offsetHeight;
      const y1 = el.offsetTop - hh + (el.offsetHeight - (innerHeight - hh)) * 0.3, t0 = performance.now(), D = 3500;
      const io = (x) => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
      (function f(t) { const k = Math.min(1, (t - t0) / D); scrollTo(0, y1 * io(k)); k < 1 ? requestAnimationFrame(f) : res(); })(t0);
    }));
    await sleep(500);
  } },
  // Lob Visual Editor, a 16:9 motion piece in the Go from idea to mailbox faster style: Build your way on purple, then the Visual Editor builds a postcard from scratch and imports a new design (starts on the finished Build your way title; timeline runs at 1.5x)
  'lob-visual-editor': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, q: 62, run: async (p) => {
    await p.evaluate(() => window.__rb.seek(1.6));
    await sleep(700);
    await p.evaluate(() => window.__rb.play({ from: 1.6, speed: 1.5, loop: false }));
    await sleep(5800);
  } },
  // Lob 12 Days Unwrap, a 1:1 Day 1 advent post: the purple gift box's bow unties, the ribbon is pulled off, the doors swing open into side panels and the 1962 Christmas stamp drops onto a dotted card with the mail fact (starts on the closed, ribboned box; timeline runs at 1.55x)
  'lob-12-days-unwrap': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 600, q: 62, run: async (p) => {
    await p.evaluate(() => window.__rb.seek(0));
    await sleep(700);
    await p.evaluate(() => window.__rb.play({ from: 0, speed: 1.55, loop: false }));
    await sleep(5800);
  } },
  // Lob 12 Days on LinkedIn: the post sits in a dimmed feed, day 1 (tangible) settles, then the post steps to day 2 and day 3, the caption swapping to the story behind each word (the live page holds each day for 4 seconds)
  'lob-12-days-linkedin': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1800, q: 62, run: async (p) => {
    const t0 = Date.now();
    await at(t0, 1500, () => p.evaluate(() => window.__li.go(1)));
    await at(t0, 3900, () => p.evaluate(() => window.__li.go(2)));
    await sleep(2400);
  } },
  // Brickanta Enterprise, a long landing page: the coral tile opens along the logo's 45 degree line, then the page scrolls to the tabbed showcase whose example card changes colour and content, on to the big numerals and the trust numbers
  'brickanta-enterprise': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1500, q: 62, run: async (p) => {
    const t0 = Date.now(), b = (f, a) => p.evaluate(([f, a]) => window.__bk[f](a), [f, a]);
    await at(t0, 1700, () => b('sec', 'sysblock'));
    await at(t0, 3000, () => b('go', 2));
    await at(t0, 3900, () => b('go', 3));
    await at(t0, 4600, () => b('sec', 'edge'));
    await at(t0, 5600, () => b('sec', 'results'));
    await sleep(1000);
  } },
  // Lob 12 Days advent, a 1:1 motion post: the wrapped door pops in, the bow lifts away, the doors swing open on the day's illustration and title, then close on the next day's number
  'lob-12-days': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 600, q: 62, run: async (p) => { await sleep(6500); } },
  // Lob 12 Days Stamps, a 1:1 motion post: real US Christmas stamps from 1962 to 2021 fly onto a square perforated mount one a day, with the year and value top right
  'lob-12-days-stamps': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, q: 62, run: async (p) => { await sleep(6500); } },
  // Lob Unwrapped, a full-screen 16:9 reel of concentric flat geometry: the intro stamp presses in and sends waves out, then dots stream in to build the US map, the trail of fading rectangles, the offset squares and the mandala persona
  'lob-unwrapped': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1200, q: 62, run: async (p) => {
    const t0 = Date.now(), g = (n) => p.evaluate((i) => window.__lu.go(i), n);
    await at(t0, 1700, () => g(2));
    await at(t0, 2600, () => g(4));
    await at(t0, 3900, () => g(7));
    await at(t0, 4800, () => g(6));
    await at(t0, 5500, () => g(10));
    await sleep(1000);
  } },
  'lob-unwrapped-reel': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 1200, q: 62, run: async (p) => {
    const t0 = Date.now(), g = (n) => p.evaluate((i) => window.__lu.go(i), n);
    await at(t0, 1700, () => g(2));
    await at(t0, 2600, () => g(4));
    await at(t0, 3900, () => g(7));
    await at(t0, 4800, () => g(6));
    await at(t0, 5500, () => g(10));
    await sleep(1000);
  } },
  // three Klir image styles in a row (product UI card, abstract gradient hero, photo + gradient): switch the size 1:1 > 16:9 > 4:3, recolour all three from the palette, step the water images and turn the text on over the first
  'klir-image-styles': { http: true, vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1200, q: 70, run: async (p) => {
    const t0 = Date.now(), c = (s) => domClick(p, s);
    await at(t0, 1500, () => c('[data-s="16:9"]'));
    await at(t0, 2400, () => c('#allsw button:nth-child(5)'));
    await at(t0, 3200, () => c('[data-s="4:3"]'));
    await at(t0, 3900, () => { c('[data-i="0"] [data-img="1"]'); c('[data-i="1"] [data-img="1"]'); c('[data-i="2"] [data-img="1"]'); });
    await at(t0, 4700, () => c('#allsw button:nth-child(3)'));
    await at(t0, 5400, () => { c('[data-i="0"] [data-k=text]'); c('[data-i="2"] [data-k=card]'); });
  } },
  // the dashboard rests off the right edge of the hero; scrolling fades the headline, slides it to the centre, then the Klir pill fades in; then on down the page and back to the start
  'klir-landing-page-side-reveal': { http: true, vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 2500, q: 34, run: async (p) => {
    // eased scrolls of a fixed duration so the page is back at the top (the first frame) before the loop point at 6s
    const t0 = Date.now(), to = (y, ms) => p.evaluate(([v, d]) => { const a = scrollY, s = performance.now(); (function f(t) { const k = Math.min(1, (t - s) / d), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; scrollTo(0, a + (v - a) * e); if (k < 1) requestAnimationFrame(f); })(s); }, [y, ms]);
    await at(t0, 700, () => to(420, 1500));
    await at(t0, 3200, () => to(1300, 900));
    await at(t0, 4200, () => to(0, 1200));
  } },
  // the Klir wayfinding line: the moving blue water hero, then the waterdrop appears, crosses the hero edge (white to blue) and travels down the page with the scroll, lighting up each section node, then back up
  'klir-landing-page': { http: true, vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 4200, run: async (p) => {
    // the dashboard rises over the hero and fills in, the walkthrough clicks to the other tab, then the page scrolls on and returns to the dashboard
    const t0 = Date.now(), to = (y) => p.evaluate((v) => window.scrollTo({ top: v, behavior: 'smooth' }), y);
    await at(t0, 2600, () => to(1500));
    await at(t0, 3800, () => to(2600));
    await at(t0, 5000, () => to(600));
  } },
  // the badge rests at its angle over the muted tiles, then the mouse sweeps over the visual to tip it and leaves so it eases back
  'lob-integrations-hero': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1200, run: async (p) => {
    const t0 = Date.now();
    await at(t0, 800, () => p.mouse.move(1100, 280, { steps: 14 }));
    await at(t0, 2200, () => p.mouse.move(780, 560, { steps: 14 }));
    await at(t0, 3500, () => p.mouse.move(1000, 300, { steps: 12 }));
    await at(t0, 4600, () => p.mouse.move(300, 650, { steps: 10 }));
    await sleep(1800);
  } },
  // Mavenoid hero on the sandbox blue: the finished hero, then the search card and graph reset and rebuild, the robot presenting the query, the matches, the notes and the chosen result
  'mavenoid-hero': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, run: async (p) => {
    const t0 = Date.now();
    await at(t0, 700, () => p.evaluate(() => __rb.play({ from: 0, speed: 1.75, loop: false })));
    await sleep(5600);
  } },
  // the finished composition, then the whole 9 s cycle at 1.4x: the query is typed, matches appear, the query and context notes fly onto the graph, the result lands
  'nlp-diagram': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, run: async (p) => {
    const t0 = Date.now();
    await at(t0, 700, () => p.evaluate(() => __rb.play({ from: 0, speed: 1.75, loop: false })));
    await sleep(5600);
  } },
  // the finished composition, then the whole 9 s cycle at 1.4x: the picker, the search card and the worker come in, the query is typed, matches appear, the answer is picked and flies to Prep tools
  'sander-troubleshoot': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 900, run: async (p) => {
    const t0 = Date.now();
    await at(t0, 700, () => p.evaluate(() => __rb.play({ from: 0, speed: 1.4, loop: false })));
    await sleep(5600);
  } },
  // the three Thread brand visuals side by side, all moving on their own: the 3D characters turning 2 0 2 6 A B C, the frame lines drawing on and re-cutting, the calligraphy writing on and off (one 8 s loop, played at 1.33x)
  // the porcupine under perforated purple and red bands sweeping in different directions, with three whip zooms (eye, quills, feet) per 6 s loop; starts on the wide shot
  'porcupine-glitch': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#from=-1.8', ready: 1000, q: 55, run: async (p) => { await sleep(5800); } },
  'postmark-awards-brand-visuals': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1500, q: 55, run: async (p) => { await sleep(5600); } },
  // Brickanta Enterprise Visuals, eight 1:1 squares in two rows of four: hero tile opening on the logo's 45 degree line, the schedule card on concrete, the shard mask, the logo lockup with its duotone shard, the example switcher, a static bar pattern, a thick icon grid and rising step lines
  'brickanta-enterprise-visuals': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip&from=0.8', ready: 1500, q: 58, run: async (p) => { await sleep(5800); } },
  'thread-brand-visuals': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#from=8.4', ready: 1500, q: 55, run: async (p) => { await sleep(5600); } },
  // the landing page: hero with the live countdown and the hairline grid lighting up, then a scroll through the keynotes, tracks and community cards and back up
  'thread-conference-landing': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1500, q: 55, run: async (p) => {
    const t0 = Date.now(), to = (sel, off) => p.evaluate(([s, o]) => window.scrollTo({ top: document.querySelector(s).getBoundingClientRect().top + scrollY - 60 + o, behavior: 'smooth' }), [sel, off]);
    await at(t0, 1000, () => to('#agenda', 0));
    await at(t0, 2600, () => to('#tracks', 0));
    await at(t0, 4000, () => to('#community', -120));
    await at(t0, 5200, () => p.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' })));
  } },
  // starts on the tile mosaic hero, then opens the Badges tile (it grows to fill the screen), the Thread logo shrinks it back, and the Motion tile opens and shrinks back
  'thread-brand-guidelines': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1800, q: 55, run: async (p) => {
    const t0 = Date.now(), k = (sel) => domClick(p, sel);
    await at(t0, 800, () => k('.tile[data-sec="badges"]'));
    await at(t0, 2600, () => k('.site .logo'));
    await at(t0, 4000, () => k('.tile[data-sec="motion"]'));
    await at(t0, 5300, () => k('.site .logo'));
  } },
  // the starting soon countdown, then the intro title, the audience question, the session title and the statement card, switched the way a visitor would with the screen chips
  'thread-live-session': { vp: [1280, 769], setup: cropOf('#cv'), ready: 1200, q: 50, run: async (p) => {
    const t0 = Date.now(), scr = (n) => domClick(p, '#layout button:nth-child(' + n + ')');
    await at(t0, 1500, () => scr(2));
    await at(t0, 2800, () => scr(3));
    await at(t0, 4200, () => scr(4));
    await at(t0, 5300, () => scr(5));
  } },
  // a block letter on the 12x12 grid: starts on a finished S, then the cells wave through the letters of SANDBOX and back to S
  // House of Balloons patterns: opens on Stretch, then steps through Stack and Bitmap and back to Stretch
  'hob-pattern-generator': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#stretch&clip', ready: 600, q: 50, run: async (p) => {
    const t0 = Date.now(), go = (k) => p.evaluate((m) => __hob.set(m), k);
    await at(t0, 1500, () => go('stack'));
    await at(t0, 3200, () => go('bitmap'));
    await at(t0, 4900, () => go('stretch'));
  } },
  // House of Balloons social studio: opens on the bars layout (1920x1080), then cycles poster, full bleed and a new colour combo and back
  'hob-social-studio': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', http: true, ready: 900, q: 30, run: async (p) => {
    const t0 = Date.now(), go = (o) => p.evaluate((x) => __hobs.set(x), o);
    await at(t0, 1500, () => go({ layout: 'poster', combo: 0 }));
    await at(t0, 3000, () => go({ layout: 'bleed', combo: 3 }));
    await at(t0, 4400, () => go({ layout: 'bars', combo: 1, zone: 'bot25' }));
    await at(t0, 5500, () => go({ layout: 'bars', combo: 4, zone: 'bot60' }));
  } },
  'grid-alphabet': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#w=SANDBOX&clip', ready: 500, q: 55, run: async (p) => { const t0 = Date.now(); await at(t0, 700, () => p.evaluate(() => __ga.start())); await sleep(5600); } },
  'conference-post-generator': { vp: [1280, 769], setup: cropOf('#cv'), ready: 1200, q: 40, run: async (p) => {
    // it opens on the badges post (16:9, cream); step through the headline, speaker and pattern templates and come back to the badges
    const t0 = Date.now(), tpl = (n) => domClick(p, '#tpl button:nth-child(' + n + ')');
    await at(t0, 1300, () => tpl(1));
    await at(t0, 2600, () => tpl(2));
    await at(t0, 3900, () => tpl(4));
    await at(t0, 5100, () => tpl(3));
  } },

  // red lattice on black, then the orange flow and the grey arches as the generator cycles on its own (lines draw in first, then morph)
  'arrow-line-generator': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '?still', ready: 800, q: 48, run: async (p) => {
    const t0 = Date.now(), go = (n) => p.evaluate((k) => __alg.go(k), n);
    await at(t0, 1500, () => go(1));
    await at(t0, 3300, () => go(2));
    await at(t0, 5100, () => go(0));
  } },
  'workout-year-reels': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // the cycle starts on the circles; step through the newest styles and one older one the way a visitor would with the switcher
    ready: 1500,
    run: async (p) => {
      const t0 = Date.now(), st = (n) => domClick(p, '#sw button:nth-child(' + n + ')');
      await at(t0, 1500, () => st(12));
      await at(t0, 2600, () => st(13));
      await at(t0, 3600, () => st(14));
      await at(t0, 4600, () => st(11));
      await at(t0, 5600, () => st(8));
    } },
  // park on the chat with the recommendations already shown (that is the first frame), then carry on from there at 4x: pick the item, size, Buy, Apple Pay, Face ID, order confirmed in the chat
  'agentic-storefront': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '?park=1',
    ready: 1500, q: 70,
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 1300, () => p.evaluate(() => { fl.play({ from: 2, speed: 5.8, keep: true, loop: false }); }));
      await sleep(5200);
    } },
  // ten full-screen styles, each looping on its own with random events; click through five of them with the numbered switcher, ending back near the first
  'human-tech-motion': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#c=1&t=2&clip', ready: 1000, q: 30, run: async (p) => {
    const t0 = Date.now(), st = (n) => domClick(p, '#sw button:nth-child(' + n + ')');
    await at(t0, 1100, () => st(2));
    await at(t0, 2200, () => st(4));
    await at(t0, 3300, () => st(5));
    await at(t0, 4300, () => st(6));
    await at(t0, 5300, () => st(8));
  } },
  'grubclub-holiday': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // the grid pops in on its own, then shuffle it and try the other shapes the way a visitor would
    ready: 1800,
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 1500, () => domClick(p, '#shuf'));
      await at(t0, 3000, () => domClick(p, '#ratios .opt:nth-child(3)'));
      await at(t0, 4200, () => domClick(p, '#ratios .opt:nth-child(2)'));
      await at(t0, 5400, () => domClick(p, '#ratios .opt:nth-child(1)'));
    } },
  'flavor-all-stars': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // the first design plays in on its own, then the selector clicks through the other three and back to the first
    ready: 1800,
    run: async (p) => {
      const t0 = Date.now(), tab = (n) => domClick(p, '#picker button:nth-child(' + n + ')');
      await at(t0, 1400, () => tab(2));
      await at(t0, 2500, () => tab(3));
      await at(t0, 3600, () => tab(4));
      await at(t0, 4700, () => tab(1));
    } },
  'grubclub-order': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // park on the hero (collage already grown in), then play the order flow at 2.4x speed: click, pick four meals, email
    setup: async (p) => { await p.evaluate(() => gc.park()); },
    ready: 700,
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 700, () => p.evaluate(() => gc.play({ speed: 2.4, clip: true })));
      await sleep(5600);
    } },
  // the feed with the sponsored ad (viewer in San Diego), the blurbs drift up, switch the viewer's metro to Miami so the creative follows, click the ad through to the landing page, then on to the performance dashboard
  'paid-ad-pipeline': { vp: [1280, 792], http: true, crop: [0, 72, 1280, 720], ready: 1200, q: 55,
    setup: async (p) => { await p.evaluate(() => { window.scrollTo(0, 330); __pp.bl.stop(); __pp.bl.instant(); }); },
    run: async (p) => {
      const t0 = Date.now();
      await p.evaluate(() => __pp.bl.start(900));   // the blurbs drift up while the feed is on screen
      await at(t0, 1500, () => p.evaluate(() => __pp.setMarket(1)));
      await at(t0, 2800, () => domClick(p, '#adCr'));
      await at(t0, 4600, () => domClick(p, '#tog button[data-s="3"]'));
      await sleep(1700);
    } },
  // the Clearco attribution guide ad on LinkedIn (viewer: DTC founder): the three stat cards stay put, switch the marketer to a paid media manager so the copy follows, step the same ad through Facebook, Google Search and YouTube, click it through to the guide, then on to the performance dashboard
  'clearco-paid-ad-pipeline': { vp: [1280, 792], http: true, crop: [0, 72, 1280, 720], ready: 1400, q: 36,
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 1400, () => p.evaluate(() => __pp.setMarketer(2)));
      await at(t0, 2200, () => p.evaluate(() => __pp.setPlatform(1)));
      await at(t0, 2900, () => p.evaluate(() => __pp.setPlatform(2)));
      await at(t0, 3600, () => p.evaluate(() => __pp.setPlatform(3)));
      await at(t0, 4400, () => domClick(p, '#cr'));
      await at(t0, 5400, () => domClick(p, '#tog button[data-s="3"]'));
      await sleep(1000);
    } },
  'location-hero': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // park on the first two blurbs, let them drift up and a third pop in, and switch the copy to Miami halfway
    setup: async (p) => { await p.evaluate(() => { lp.stop(); lp.set(0); bl.stop(); bl.instant(); }); },
    ready: 1200,
    run: async (p) => {
      const t0 = Date.now();
      await p.evaluate(() => { bl.instant(); bl.start(1500); });
      await at(t0, 3200, () => p.evaluate(() => lp.set(1)));
      await sleep(5600);
    } },
  'grubclub-end-card': { vp: [1280, 792], crop: [0, 72, 1280, 720],
    // park on the finished card, replay the end card animation at 3x, then try the motion, circle style, theme and format the way a visitor would
    setup: async (p) => { await p.evaluate(() => ec.seek(125)); },
    ready: 700,
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 1400, () => p.evaluate(() => ec.play({ speed: 3, loop: false })));
      await at(t0, 3200, () => domClick(p, '#motions .opt:nth-child(2)'));
      await at(t0, 4200, () => domClick(p, '#styles .opt:nth-child(2)'));
      await at(t0, 5000, () => domClick(p, '#themes .opt:nth-child(3)'));
      await at(t0, 5700, () => domClick(p, '#ratios .opt:nth-child(2)'));
    } },
  // the hero pills run on a 8.2 s cycle on their own; wait until the circle has grown so the loop starts on the full composition
  'clearco-attribution-guide': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#still-title', ready: 1400, run: async () => {} },
  'clearco-logistics-guide': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async (p) => {
    const t0 = Date.now();
    const go = (id, d) => p.evaluate(([i, o]) => scrollTo(0, document.getElementById(i).offsetTop - 49 + o), [id, d]);
    await at(t0, 900, () => go('stmt', 0));      // the grid with sliding squares
    await at(t0, 3000, () => go('ch1', 40));     // chapter one, chart stuck to the top
    await at(t0, 4300, () => go('ch1', 260));
    await at(t0, 5200, () => p.evaluate(() => scrollTo(0, 0)));
  } },
  // the sequence starts part way in (#t=4.6): headline, sub-headline, then the logo fades in at the end
  'clearco-logistics-motion': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#v=hero&t=4.6', ready: 1500, run: async () => {} },
  // the globe turns and orders fly on their own; wait for the headline to fade in
  // hover three arms in turn; each breaks into particles and reforms
  'asterisk': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async (p) => {
    const t0 = Date.now();
    await at(t0, 800, () => p.mouse.move(560, 300, { steps: 8 }));
    await at(t0, 2600, () => p.mouse.move(760, 330, { steps: 8 }));
    await at(t0, 4300, () => p.mouse.move(660, 520, { steps: 8 }));
    await at(t0, 5400, () => p.mouse.move(1000, 700, { steps: 4 }));
  } },
  'ilg-pixel-globe': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1300, q: 50, run: async () => {} },
  'clearco-terrain': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async () => {} },
  'clearco-target-frame': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async () => {} },
  'video-synopsis': { vp: [1280, 769], setup: cropOf('#vSyn'), run: async () => {} },
  'prompt-demos': { vp: [1280, 792], crop: [19, 82, 1242, 699], ready: 2200, p5: true, run: async () => {} },
  'lifecycle-image-engine': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async (p) => {
    const t0 = Date.now();
    // first click at 1.5 s: the clip opens 0.5 s into the footage, and the video can lag the page enough that a click
    // at 0.9 s already shows the sidebar scrolling in the first frame
    await at(t0, 1500, () => click(p, /^Lavender$/));
    await at(t0, 2400, () => click(p, /^Sky$/));
    await at(t0, 3300, () => click(p, /^Sunny$/));
    await at(t0, 4200, () => click(p, /^Icons$/));
    await at(t0, 5100, () => click(p, /^Spot illo$/));
    await at(t0, 5600, () => click(p, /^Pink$/));
  } },
  // the whole 23.8 s loop played at 3.6x from the middle of the scan: flags land, result fills in, reviewer requests changes, library updates, next audit starts
  'brand-audit-engine': { vp: [1280, 792], crop: [0, 72, 1280, 720], ready: 1200, q: 40, run: async (p) => {
    await p.evaluate(() => ba.play({ from: 9000, speed: 3.6 }));
    await sleep(6600);
  } },
  // brand guidelines settings: starts on the colours the AI read from the sample guide, then confirms a colour and adds context, tunes the grid, switches to type styles and spacing with the red measurement bands
  'brand-guidelines-settings': { vp: [1280, 792], crop: [0, 72, 1280, 720], hash: '#clip', ready: 600, q: 50,
    setup: async (p) => { await p.evaluate(() => window.__bg.sample()); await p.waitForFunction(() => window.__bg.ready(), null, { timeout: 8000 }); await p.evaluate(() => { window.__bg.go('colours'); document.querySelector('#toast').classList.remove('on'); }); },
    run: async (p) => {
      const t0 = Date.now(), go = (s) => domClick(p, `.nv[data-sec="${s}"]`);
      await at(t0, 1500, () => p.type('.cc textarea', 'Primary text colour. Never on indigo.', { delay: 28 }));
      await at(t0, 2900, () => domClick(p, '.cc [data-confirm]'));
      await at(t0, 3200, () => go('layout'));
      await at(t0, 3600, () => p.fill('[data-path="layout.props.0.v"]', '8'));
      await at(t0, 4000, () => p.fill('[data-path="layout.props.0.v"]', '16'));
      await at(t0, 4500, () => go('type'));
      await at(t0, 5300, () => go('spacing'));
      await at(t0, 5800, () => p.fill('[data-path="spacing.props.1.v"]', '40'));
      await sleep(900);
    } },
  'hero-banner-engine': { vp: [1280, 769], setup: cropOf('#cv'), run: async (p) => {
    const t0 = Date.now();
    await at(t0, 800, () => click(p, /^Midnight$/));
    await at(t0, 1800, () => click(p, /^Lime$/));
    await at(t0, 2800, () => click(p, /^Lavender$/));
    await at(t0, 3700, () => click(p, /Shuffle/));
    await at(t0, 4700, () => click(p, /Shuffle/));
    await at(t0, 5600, () => click(p, /^Indigo$/));
  } },
  'postmark-awards-motion': { vp: [1280, 769], ready: 2500,
    // crop the middle 16:9 of the stage, then play each style in turn from its start
    setup: async (p) => {
      const r = await p.evaluate(() => { const b = document.querySelector('#cv').getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; });
      const h = Math.round(r[2] * 9 / 16);
      return [Math.round(r[0]), Math.round(r[1] + (r[3] - h) / 2), Math.round(r[2]), h];
    },
    run: async (p) => {
      const t0 = Date.now();
      await at(t0, 1500, () => click(p, /^Growth$/));
      await at(t0, 3000, () => click(p, /^Ticker$/));
      await at(t0, 4400, () => click(p, /^Personalize$/));
      await at(t0, 5900, () => click(p, /^Repeater$/));
    } },
  'postmark-ribbon-engine': { vp: [1280, 769], setup: cropOf('#cv'), ready: 800, run: async (p) => {
    const t0 = Date.now(), mode = (m) => p.evaluate((m) => rb.setMode(m), m), rand = () => p.evaluate(() => rb.randomize());
    await at(t0, 900, rand);
    await at(t0, 1900, rand);
    await at(t0, 2900, () => mode('chaos'));
    await at(t0, 3900, rand);
    await at(t0, 4700, () => mode('loop'));
    await at(t0, 5500, rand);
  } },
  'ab-testing': { vp: [1280, 792], crop: [0, 72, 1280, 720], run: async (p) => {
    const t0 = Date.now();
    const row = (i) => p.evaluate((i) => { const r = document.querySelectorAll('#rows tr'); (r[i] || r[0]).click(); }, i);
    await at(t0, 900, () => row(1));
    await at(t0, 2000, () => row(2));
    await at(t0, 3000, () => row(3));
    await at(t0, 4000, () => p.locator('#chart').click({ position: { x: 60, y: 90 }, timeout: 1500 }).catch(() => {}));
    await at(t0, 5200, () => row(0));
  } },
  'blog-banner-studio': { vp: [1400, 900],
    // the preview is sticky: scroll the controls into view first so it sits still, then crop its middle 16:9
    setup: async (p) => {
      await p.evaluate(() => document.querySelectorAll('details.sec').forEach((d) => (d.open = true)));
      await p.evaluate(() => { const c = document.querySelector('input[data-k="badge"]'); if (c && c.checked) c.click(); });   // no industry badge in the tile
      await p.evaluate(() => document.querySelector('[data-act="random-comp"]').scrollIntoView({ block: 'center' }));
      await p.waitForTimeout(500);
      const r = await p.evaluate(() => { const b = document.querySelector('#banner').getBoundingClientRect(); return [b.x, b.y, b.width, b.height]; });
      const ch = r[3], cw = ch * 16 / 9;
      return [Math.round(r[0] + (r[2] - cw) / 2), Math.round(r[1]), Math.round(cw), Math.round(ch)];
    },
    run: async (p) => {
      const t0 = Date.now(), rand = () => domClick(p, '[data-act="random-comp"]');
      // a long lead-in: the loop starts 0.5s into the footage and must show the default composition, even if the video lags the page a little
      await at(t0, 1400, rand); await at(t0, 2500, rand);
      await at(t0, 3600, () => domClick(p, '[data-act="random-palette"]'));
      await at(t0, 4600, rand); await at(t0, 5500, rand);
    } },
};

async function record(name) {
  const A = APPS[name];
  if (!A) throw new Error('unknown app ' + name + ' (add it to the table in tools/record-clips.js)');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'clip-' + name + '-'));
  const [vw, vh] = A.vp;
  const browser = await chromium.launch();
  const t0 = Date.now();
  const ctx = await browser.newContext({ viewport: { width: vw, height: vh }, recordVideo: { dir, size: { width: vw, height: vh } } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  if (A.p5 && process.env.P5_LIB) await page.route('**/p5.min.js', (r) => r.fulfill({ path: process.env.P5_LIB, contentType: 'application/javascript' }));
  if (A.http) {   // apps that embed another app in an iframe need one origin, which file:// does not give
    const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]).replace(/\/$/, '/index.html'));
      fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; return r.end(); } r.setHeader('content-type', { '.html': 'text/html', '.jpg': 'image/jpeg', '.png': 'image/png', '.js': 'text/javascript', '.css': 'text/css' }[path.extname(f)] || 'application/octet-stream'); r.end(d); }); });
    await new Promise((ok) => srv.listen(0, ok)); A.srv = srv;
    await page.goto('http://localhost:' + srv.address().port + '/' + name + '/' + (A.hash || ''));
  } else
  await page.goto('file://' + ROOT + name + '/index.html' + (A.hash || ''));
  await page.waitForLoadState('networkidle').catch(() => {});
  if (A.setup) { const c = await A.setup(page); if (Array.isArray(c)) A.crop = c; }
  await page.waitForTimeout(A.ready || 600);
  const start = (Date.now() - t0) / 1000;
  await Promise.all([A.run(page), sleep(6900)]);
  await ctx.close(); await browser.close(); if (A.srv) A.srv.close();
  if (errs.length) console.log('  page errors:', errs.slice(0, 2));
  return { src: path.join(dir, fs.readdirSync(dir).find((f) => f.endsWith('.webm'))), start };
}

/* 6.5 s of footage -> 6 s loop: the last half second cross-fades into the first, so the loop point is seamless.
   12 fps, 960x540, animated WebP that repeats forever. */
function encode(name, src, start) {
  const A = APPS[name], out = ROOT + name + '/thumb.webp';
  // pull the crop in a few px on every side (keeping 16:9): the video codec smears the hard edges just outside it (each
  // app's nav rule above, the page edge on the right) a pixel or two inwards, which showed as a hairline on the home page tiles
  const [x0, y0, w0, h0] = A.crop, INSET = 8;
  const cw = Math.round(w0 - 2 * INSET), ch = Math.round(cw * 9 / 16), cx = Math.round(x0 + (w0 - cw) / 2), cy = Math.round(y0 + (h0 - ch) / 2);
  const base = `[0:v]trim=start=${start.toFixed(3)}:duration=6.6,setpts=PTS-STARTPTS,fps=30,crop=${cw}:${ch}:${cx}:${cy},scale=960:540:flags=lanczos,format=yuv420p`;
  const fc = base + ',split=3[a0][b0][c0];[a0]trim=0.5:6.0,setpts=PTS-STARTPTS[a];[b0]trim=6.0:6.5,setpts=PTS-STARTPTS[b];[c0]trim=0:0.5,setpts=PTS-STARTPTS[c];[b][c]xfade=transition=fade:duration=0.5:offset=0[bc];[a][bc]concat=n=2:v=1,fps=12[v]';
  cp.execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-i', src, '-filter_complex', fc, '-map', '[v]', '-t', '6',
    '-c:v', 'libwebp_anim', '-q:v', String(A.q || 62), '-compression_level', '6', '-loop', '0', '-an', out]);
  // the still is the clip's first frame, which is also its loop point, so the tile never visibly cuts between the two
  cp.execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-i', src, '-filter_complex', fc, '-map', '[v]', '-frames:v', '1', ROOT + name + '/thumb.png']);
  console.log(name, '->', path.relative(ROOT, out), Math.round(fs.statSync(out).size / 1024) + ' KB, and thumb.png');
}

(async () => {
  const names = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(APPS);
  for (const n of names) { const r = await record(n); encode(n, r.src, r.start); fs.rmSync(path.dirname(r.src), { recursive: true, force: true }); }
})();
