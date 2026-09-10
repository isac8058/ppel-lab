// List verification. Optional: EQUIPMENT_MANIFEST, PLAYWRIGHT_MODULE, EQUIPMENT_TEST_OUT.
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.resolve(process.env.EQUIPMENT_TEST_OUT||path.join(root,'.equipment-work/browser-list'));
assert(out.startsWith(root+path.sep));
const manifestPath=process.env.EQUIPMENT_MANIFEST||path.join(root,'../ppel-lab-equipment-input/manifest.json');
const manifest=JSON.parse((await readFile(manifestPath,'utf8')).replace(/^\uFEFF/,''));
assert.equal(manifest.length,36);
const expected=manifest.map(({no,name_en})=>({no,name_en})).sort((a,b)=>a.no-b.no);
const categories=[[1,2,23,26,27,28],[4,22,24,29,30],[5,31],[11,12,17,25,32,33,34],[7,8,9,10,15],[3,6,13,14,16,18,19,20,21,35,36]];
const markup=await readFile(path.join(root,'index.html'),'utf8');
assert(!/image\/equipment\/|equipment-photo|equipment-lightbox/.test(markup),'Photo/lightbox code remains');
await mkdir(out,{recursive:true});process.env.TEMP=out;process.env.TMP=out;
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(root,'.equipment-work/node_modules/playwright-core'));
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.vtt':'text/vtt'};
const server=createServer(async(req,res)=>{
  try{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const target=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
    if(!target.startsWith(root+path.sep)){res.writeHead(403).end();return;}
    const content=await readFile(target);res.writeHead(200,{'Content-Type':mime[path.extname(target)]||'application/octet-stream'}).end(content);
  }catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url=`http://127.0.0.1:${server.address().port}/`;
let browser;const results=[];
try{
  browser=await chromium.launch({channel:'chrome',headless:true});
  for(const width of [320,390,768,1920])for(const theme of ['light','dark'])for(const reducedMotion of ['no-preference','reduce']){
    const context=await browser.newContext({viewport:{width,height:900},reducedMotion});
    await context.addInitScript(theme=>localStorage.setItem('ppel-theme',theme),theme);
    const page=await context.newPage();page.setDefaultTimeout(10000);
    const errors=[],failed=[],httpErrors=[],photoRequests=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
    page.on('response',r=>{if(r.status()>=400)httpErrors.push({url:r.url(),status:r.status()});});
    page.on('request',r=>{if(r.url().includes('/image/equipment/'))photoRequests.push(r.url());});
    await page.goto(url,{waitUntil:'load',timeout:30000});
    assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
    assert.equal(await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches),reducedMotion==='reduce');
    assert.equal(await page.locator('.equipment-group').count(),6);assert.equal(await page.locator('.equipment-item').count(),36);
    const rows=await page.locator('.equipment-item').evaluateAll(els=>els.map(el=>({no:Number(el.dataset.equipmentNo),name_en:el.querySelector('.equipment-en').textContent})));
    assert.deepEqual(rows.sort((a,b)=>a.no-b.no),expected,'36 names must exactly match manifest, including duplicates');
    assert.deepEqual(await page.locator('.equipment-group').evaluateAll(gs=>gs.map(g=>[...g.querySelectorAll('.equipment-item')].map(el=>Number(el.dataset.equipmentNo)))),categories);
    assert.equal(await page.locator('#equipment img,#equipment picture,#equipment video,#equipment source,#equipment canvas,#equipment svg,#equipment [src],#equipment [srcset]').count(),0);
    assert.equal(await page.locator('#equipment').evaluate(el=>[el,...el.querySelectorAll('*')].filter(e=>[getComputedStyle(e),getComputedStyle(e,'::before'),getComputedStyle(e,'::after')].some(s=>s.backgroundImage!=='none')).length),0);
    const topLink=page.locator('#navlinks a[href="#equipment"]');
    if(await page.locator('#burger').isVisible())await page.locator('#burger').click();
    await topLink.click();
    await page.waitForFunction(()=>location.hash==='#equipment'&&Math.abs(document.getElementById('equipment').getBoundingClientRect().top-80)<5);
    assert.equal(await topLink.evaluate(el=>el.previousElementSibling.getAttribute('href')),'#research');
    for(const language of ['en','ko']){
      if(language==='ko')await page.locator('#langBtn').click();
      assert.equal(await page.locator('#equipment-heading').textContent(),language==='ko'?'장비':'Equipment');
      assert.equal(await topLink.textContent(),language==='ko'?'장비':'Equipment');
      assert(await page.locator('.equipment-group h3').evaluateAll(els=>els.every(el=>el.textContent===el.dataset[document.documentElement.lang])));
      assert.equal(await page.locator('.equipment-ko').evaluateAll(els=>els.filter(el=>el.textContent.trim()&&el.lang==='ko').length),36);
      const layout=await page.locator('#equipment').evaluate(section=>({opacity:getComputedStyle(section).opacity,
        hidden:[section,...section.querySelectorAll('.equipment-group,.equipment-item,.equipment-en,.equipment-ko')].some(el=>getComputedStyle(el).display==='none'||getComputedStyle(el).visibility==='hidden'||Number(getComputedStyle(el).opacity)===0),
        overflow:[section,...section.querySelectorAll('*')].some(el=>{const r=el.getBoundingClientRect();return r.left<0||r.right>innerWidth+.5||el.scrollWidth>el.clientWidth+1;}),
        columns:getComputedStyle(section.querySelector('.equipment-grid')).gridTemplateColumns}));
      assert.equal(layout.opacity,'1');assert.equal(layout.hidden,false);assert.equal(layout.overflow,false);
      await page.screenshot({path:path.join(out,`${width}-${theme}-${reducedMotion}-${language}.png`)});
      if(width===1920&&theme==='light'&&reducedMotion==='reduce'&&language==='ko')await page.locator('#equipment').screenshot({path:path.join(out,'section-desktop-ko.png')});
    }
    const footerLink=page.locator('footer a[href="#equipment"]');
    assert.equal(await footerLink.textContent(),'장비');assert.equal(await footerLink.evaluate(el=>el.previousElementSibling.getAttribute('href')),'#research');
    await footerLink.click();await page.waitForFunction(()=>Math.abs(document.getElementById('equipment').getBoundingClientRect().top-80)<5);
    assert((await page.locator('footer').textContent()).includes('v2026.09.08-5'));
    const result={width,theme,reducedMotion,languages:['en','ko'],names:36,categories:6,imageReferences:0,photoRequests,errors,failed,httpErrors,passed:!errors.length&&!failed.length&&!httpErrors.length&&!photoRequests.length};
    results.push(result);console.log(JSON.stringify(result));await writeFile(path.join(out,'results.json'),JSON.stringify(results,null,2));await context.close();
  }
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
assert(results.length===16&&results.every(r=>r.passed),'Browser verification failed: inspect results.json');
