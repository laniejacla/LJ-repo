// Renders video.html frame by frame into JPEGs.
// Usage: node render.js <outDir> [fps] [--stills]
//   --stills writes one frame from the middle of each scene (quick visual check).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const outDir = process.argv[2];
  const fps = Number(process.argv[3]) || 30;
  const stills = process.argv.includes('--stills');
  fs.mkdirSync(outDir, { recursive: true });
  const url = 'file://' + path.join(__dirname, 'video.html');
  const browser = await chromium.launch();
  const WORKERS = stills ? 1 : 4;

  const first = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await first.goto(url);
  await first.evaluate(() => document.fonts.ready);
  const { total, timeline } = await first.evaluate(() => ({ total: window.TOTAL, timeline: window.TIMELINE }));
  fs.writeFileSync(path.join(outDir, 'timeline.json'), JSON.stringify({ total, fps, timeline }, null, 1));

  const grab = (page, t) => page.evaluate((tt) => {
    window.renderFrame(tt);
    return document.getElementById('c').toDataURL('image/jpeg', 0.95).split(',')[1];
  }, t);

  if (stills) {
    for (const s of timeline) {
      for (const k of [0.3, 0.8]) {
        const b64 = await grab(first, s.start + s.dur * k);
        fs.writeFileSync(path.join(outDir, `${s.id}-${k}.jpg`), Buffer.from(b64, 'base64'));
      }
    }
    await browser.close();
    return;
  }

  const frames = Math.round(total * fps);
  let next = 0, done = 0;
  const work = async (page) => {
    for (;;) {
      const i = next++;
      if (i >= frames) return;
      const b64 = await grab(page, i / fps);
      fs.writeFileSync(path.join(outDir, `f${String(i).padStart(5, '0')}.jpg`), Buffer.from(b64, 'base64'));
      if (++done % 300 === 0) console.log(`${done}/${frames}`);
    }
  };
  const pages = [first];
  for (let i = 1; i < WORKERS; i++) {
    const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await p.goto(url);
    await p.evaluate(() => document.fonts.ready);
    pages.push(p);
  }
  await Promise.all(pages.map(work));
  console.log(`rendered ${frames} frames (${total.toFixed(1)}s at ${fps}fps)`);
  await browser.close();
})();
