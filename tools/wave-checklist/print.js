// Prints tools/wave-checklist/checklist.html to the checklist PDF used by the Wave landing pages.
// Usage: node tools/wave-checklist/print.js [out.pdf ...]
// Default outputs: wave-tax-landing-origami/ and wave-file-without-fear/ wave-2026-tax-checklist.pdf
const { chromium } = require('playwright');
const path = require('path');
const root = path.resolve(__dirname, '../..');
const outs = process.argv.slice(2).length ? process.argv.slice(2) : ['wave-tax-landing-origami', 'wave-file-without-fear'].map((d) => path.join(root, d, 'wave-2026-tax-checklist.pdf'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'checklist.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  for (const o of outs) { await p.pdf({ path: o, format: 'Letter', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } }); console.log('wrote', o); }
  await b.close();
})();
