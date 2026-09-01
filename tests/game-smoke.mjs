// Headless smoke test for game.html (Ink Runner).
// Usage:  node tests/game-smoke.mjs            (screenshots go to $OUT_DIR or the OS temp dir)
// Needs Playwright: a local `playwright` package, or the global install under /opt/node22.
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const HERE = dirname(fileURLToPath(import.meta.url));
const URL = pathToFileURL(join(HERE, '..', 'game.html')).href;
const OUT = process.env.OUT_DIR || join(tmpdir(), 'ink-runner-shots');
mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Autopilot that runs inside the page: steers to the nearest pad / crack gap, lifts over dust.
const PILOT = `
(() => {
  const K = window.__ink, G = K.G, IN = K.IN;
  if (window.__pilotTimer) clearInterval(window.__pilotTimer);
  window.__pilotTimer = setInterval(() => {
    if (G.state !== 'playing') return;
    const NX = K.NX;
    const ahead = G.objs.map(o => ({ o, sx: o.x - G.dist })).filter(a => a.sx > NX - 40 && a.sx < NX + 420).sort((a, b) => a.sx - b.sx);
    let ty = null;
    const crack = ahead.find(a => a.o.type === 'crack' && a.sx > NX - 20 && a.sx < NX + 260);
    if (crack) {
      const cr = ahead.filter(a => a.o.type === 'crack' && Math.abs(a.sx - crack.sx) < 5).map(a => a.o);
      const laneH = (K.PLAY_BOT - K.PLAY_TOP) / 6;
      let bestY = null, bestD = 1e9;
      for (let i = 0; i < 6; i++) {
        const y = K.PLAY_TOP + (i + .5) * laneH;
        const blocked = cr.some(c => y > c.y1 - 14 && y < c.y2 + 14);
        if (!blocked && Math.abs(y - G.ny) < bestD) { bestD = Math.abs(y - G.ny); bestY = y; }
      }
      if (bestY !== null) ty = bestY;
    }
    if (ty === null) {
      const pad = ahead.find(a => a.o.type === 'pad' && !a.o.done && a.sx > NX - 10);
      const ink = G.ink < 55 ? ahead.find(a => a.o.type === 'ink' && a.sx > NX - 10) : null;
      const flash = ahead.find(a => a.o.type === 'flash' && a.sx > NX - 10);
      const tgt = [pad, ink, flash].filter(Boolean).sort((a, b) => a.sx - b.sx)[0];
      if (tgt) ty = tgt.o.type === 'ink' ? tgt.o.yb : tgt.o.y;
    }
    if (ty !== null) G.ty = ty;
    const danger = ahead.some(a => a.o.type === 'dust' && a.sx > NX - 34 && a.sx < NX + 34 && Math.abs(a.o.y - G.ny) < 34);
    IN.key = !danger;
  }, 30);
})();
`;
const jump = px => `(() => { const G = window.__ink.G; G.dist += ${px}; G.spawnX += ${px}; for (const o of G.objs) o.x += ${px}; })()`;

async function run() {
  const browser = await chromium.launch();
  const errors = [];
  const S = {};
  const hook = page => {
    page.on('console', m => { if (m.type() === 'error' && !/ERR_|net::/.test(m.text())) errors.push(`[console] ${m.text()}`); });
    page.on('pageerror', e => errors.push(`[pageerror] ${e.message}`));
  };

  // ---------- desktop, Korean locale ----------
  const A = await browser.newContext({ viewport: { width: 1280, height: 720 }, locale: 'ko-KR' });
  let page = await A.newPage(); hook(page);
  await page.goto(URL); await sleep(1000);
  S.defaultLang = await page.evaluate(() => document.documentElement.lang);
  await page.screenshot({ path: `${OUT}/01-menu-ko.png` });
  await page.click('#pMenu .jLang'); await sleep(150);
  await page.screenshot({ path: `${OUT}/02-menu-en.png` });
  await page.click('#pMenu .jLang'); await sleep(100);

  await page.click('#bStart'); await sleep(300);
  S.stateAfterStart = await page.evaluate(() => window.__ink.G.state);
  await page.evaluate(() => { window.__frames = 0; const f = () => { window.__frames++; requestAnimationFrame(f); }; requestAnimationFrame(f); });
  await page.evaluate(PILOT);
  await sleep(4000);
  await page.screenshot({ path: `${OUT}/03-play-early.png` });
  await sleep(8000);
  S.fps = Math.round(await page.evaluate(() => window.__frames) / 12);
  S.at12s = await page.evaluate(() => { const G = window.__ink.G; return { score: G.score, pads: G.pads, maxCombo: G.maxCombo, lives: G.lives, ink: Math.round(G.ink), dist_m: Math.floor(G.dist / 100) }; });

  // later stage: dust, cracks, and a forced sintering flash
  await page.evaluate(jump(14000));
  await page.evaluate(() => { const G = window.__ink.G; G.flashNext = 0; G.sinceFlash = 1e9; });
  let sinterSeen = false; const t1 = Date.now();
  while (Date.now() - t1 < 12000) { if (await page.evaluate(() => window.__ink.G.flash > 0)) { sinterSeen = true; break; } await sleep(100); }
  if (sinterSeen) await page.screenshot({ path: `${OUT}/04-sinter.png` });
  await sleep(3000);
  await page.screenshot({ path: `${OUT}/05-play-late.png` });
  S.late = await page.evaluate(() => { const G = window.__ink.G; return { score: G.score, pads: G.pads, maxCombo: G.maxCombo, lives: G.lives, ink: Math.round(G.ink), stage: G.stage, dist_m: Math.floor(G.dist / 100), speed: Math.round(G.speed), objs: G.objs.length, tracePts: G.traces.reduce((s, t) => s + t.length, 0) }; });
  S.sinterSeen = sinterSeen;

  // pause / resume
  await page.keyboard.press('KeyP'); await sleep(250);
  S.paused = await page.evaluate(() => window.__ink.G.state);
  await page.screenshot({ path: `${OUT}/06-paused.png` });
  await page.keyboard.press('KeyP'); await sleep(200);
  S.resumed = await page.evaluate(() => window.__ink.G.state);

  // real game-over path: one life left, print blindly into hazards at a high stage
  await page.evaluate(() => { clearInterval(window.__pilotTimer); const K = window.__ink; K.G.lives = 1; K.IN.key = true; K.G.ty = 300; });
  await page.evaluate(jump(12000));
  const t2 = Date.now();
  while (Date.now() - t2 < 25000) { if ((await page.evaluate(() => window.__ink.G.state)) === 'over') break; await sleep(200); }
  S.overState = await page.evaluate(() => window.__ink.G.state);
  await sleep(400);
  await page.screenshot({ path: `${OUT}/07-gameover.png` });
  S.bestStored = await page.evaluate(() => localStorage.getItem('ppel-ink-runner:best'));
  await page.click('#bCopy'); await sleep(200);
  S.copyLabel = await page.evaluate(() => document.getElementById('bCopy').textContent);

  // restart with R, keyboard + mouse control
  await page.keyboard.press('KeyR'); await sleep(300);
  S.afterR = await page.evaluate(() => { const G = window.__ink.G; return { state: G.state, score: G.score, lives: G.lives }; });
  const y0 = await page.evaluate(() => window.__ink.G.ny);
  await page.keyboard.down('ArrowUp'); await page.keyboard.down('Space'); await sleep(700);
  await page.keyboard.up('ArrowUp'); await page.keyboard.up('Space');
  S.keyboard = await page.evaluate(y0 => { const G = window.__ink.G; return { movedUp: G.ny < y0 - 100, tracePts: G.traces.reduce((s, t) => s + t.length, 0), inkUsed: G.ink < 100 }; }, y0);
  await page.mouse.move(900, 600); await sleep(400);
  const yMouse = await page.evaluate(() => Math.round(window.__ink.G.ny));
  await page.mouse.down(); await sleep(250);
  const printing = await page.evaluate(() => window.__ink.G.printing);
  await page.mouse.up(); await sleep(100);
  S.mouse = { yMouse, printingWhileHeld: printing, printingAfterRelease: await page.evaluate(() => window.__ink.G.printing) };
  // HUD buttons usable during play
  await page.click('#bPause'); await sleep(150);
  S.hudPause = await page.evaluate(() => window.__ink.G.state);
  await A.close();

  // ---------- reduced motion (the owner's machine) ----------
  const B = await browser.newContext({ viewport: { width: 1280, height: 720 }, reducedMotion: 'reduce' });
  page = await B.newPage(); hook(page);
  await page.goto(URL); await sleep(700);
  const snap = () => page.evaluate(() => document.getElementById('game').toDataURL().slice(-80));
  const s1 = await snap(); await sleep(400); const s2 = await snap();
  await page.click('#bStart'); await page.evaluate(PILOT); await sleep(3000);
  S.reducedMotion = { menuAnimates: s1 !== s2, ...(await page.evaluate(() => ({ state: window.__ink.G.state, dist_m: Math.floor(window.__ink.G.dist / 100), score: window.__ink.G.score }))) };
  await B.close();

  // ---------- phone, landscape (touch) ----------
  const Cx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'ko-KR' });
  page = await Cx.newPage(); hook(page);
  await page.goto(URL); await sleep(700);
  S.phoneMenu = await page.evaluate(() => { const r = document.getElementById('pMenu').getBoundingClientRect(); const o = document.getElementById('overlay'); return { panelTop: Math.round(r.top), scrollable: o.scrollHeight > o.clientHeight }; });
  await page.screenshot({ path: `${OUT}/08-phone-landscape-menu.png` });
  await page.tap('#bStart'); await sleep(300);
  const cdp = await Cx.newCDPSession(page);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 600, y: 120 }] }); await sleep(500);
  const hold = await page.evaluate(() => ({ printing: window.__ink.G.printing, ny: Math.round(window.__ink.G.ny) }));
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 600, y: 300 }] }); await sleep(500);
  const moved = await page.evaluate(() => ({ printing: window.__ink.G.printing, ny: Math.round(window.__ink.G.ny) }));
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await sleep(150);
  const released = await page.evaluate(() => ({ printing: window.__ink.G.printing }));
  S.touch = { hold, moved, released };
  await page.screenshot({ path: `${OUT}/09-phone-landscape-play.png` });
  await Cx.close();

  // ---------- phone, portrait ----------
  const D = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: 'ko-KR' });
  page = await D.newPage(); hook(page);
  await page.goto(URL); await sleep(700);
  S.portrait = await page.evaluate(() => ({ hint: getComputedStyle(document.getElementById('rot')).display, panelTop: Math.round(document.getElementById('pMenu').getBoundingClientRect().top) }));
  await page.screenshot({ path: `${OUT}/10-phone-portrait-menu.png` });
  await D.close();

  await browser.close();
  console.log(JSON.stringify(S, null, 2));
  console.log('screenshots:', OUT);
  console.log('ERRORS:', errors.length ? errors : 'none');
  const ok = S.stateAfterStart === 'playing' && S.late.score > 0 && S.overState === 'over' && S.reducedMotion.menuAnimates && S.reducedMotion.dist_m > 0
    && S.keyboard.movedUp && S.mouse.printingWhileHeld && !S.mouse.printingAfterRelease && S.touch.hold.printing && !S.touch.released.printing && errors.length === 0;
  console.log(ok ? 'SMOKE TEST PASSED' : 'SMOKE TEST FAILED');
  process.exit(ok ? 0 : 1);
}
run().catch(e => { console.error(e); process.exit(1); });
