// Screenshot sections of a sandbox app.
//   (python3 -m http.server 8123 &)   # from the repo root
//   S=<scratchpad> APP=<app-folder> NODE_PATH=$(npm root -g) node shot.js <id[:scrollOffset]> ...
// Env: W, H viewport (default 1440x900), PFX file name prefix, HASH extra hash params (default "t=2.6" freezes animation).
// Each argument scrolls to the element #<id> (or the top for "top") plus an offset in px, then saves $S/s_<PFX><id><offset>.png.
const { chromium } = require('playwright');
(async () => {
  const w = +(process.env.W || 1440), h = +(process.env.H || 900), app = process.env.APP || '';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const errs = [];
  p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', (e) => errs.push('PAGEERR ' + e.message));
  await p.goto('http://localhost:8123/' + app + '/#' + (process.env.HASH || 't=2.6'), { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  for (const arg of process.argv.slice(2)) {
    const [id, off] = arg.split(':');
    await p.evaluate(([i, o]) => {
      const e = i === 'top' ? document.body : document.querySelector('#' + i);
      window.scrollTo(0, e.getBoundingClientRect().top + scrollY + o);
    }, [id, +off || 0]);
    await p.waitForTimeout(900);
    await p.screenshot({ path: process.env.S + '/s_' + (process.env.PFX || '') + id + (off || '') + '.png' });
  }
  console.log('errors:', JSON.stringify(errs));
  await b.close();
})();
