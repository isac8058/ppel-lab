/* 30초 애니메이션을 결정적으로 프레임 캡처한다.
   사용법: node tools/capture.mjs <출력폴더> all
   그 다음: ffmpeg -framerate 24 -i <출력폴더>/f%04d.jpg ... cap-run-30s.mp4
   playwright-core와 크로미움이 필요하다 (executablePath는 환경에 맞게 고친다). */
import pw from 'playwright-core';
import fs from 'fs';
const { chromium } = pw;
const [,, outDir, mode] = process.argv;
fs.mkdirSync(outDir, { recursive: true });
const b = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
const errs = [];
p.on('pageerror', e => errs.push(String(e)));
await p.goto('file://' + new URL('../cap-run-30s.html', import.meta.url).pathname);
await p.waitForTimeout(300);
const times = mode === 'all'
  ? Array.from({ length: 720 }, (_, i) => i / 24)
  : [0.6, 2.0, 2.55, 4.0, 6.0, 8.5, 11.5, 14.2, 16.5, 19.6, 22.2, 25.2, 28.6];
let n = 0;
for (const t of times) {
  const data = await p.evaluate((tt) => {
    window.__frame(tt);
    return document.getElementById('c').toDataURL('image/jpeg', 0.94);
  }, t);
  fs.writeFileSync(`${outDir}/f${String(n).padStart(4, '0')}.jpg`, Buffer.from(data.split(',')[1], 'base64'));
  n++;
}
await b.close();
console.log(JSON.stringify({ frames: n, pageErrors: errs.slice(0, 5) }));
