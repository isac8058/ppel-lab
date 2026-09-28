// Browser acceptance checks: TEST_URL=http://127.0.0.1:8765/ node tests/design-polish.cjs
// Reuses the same Playwright/CHROME_PATH environment as research-captions.cjs.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const url=process.env.TEST_URL||'http://127.0.0.1:8765/';
const widths=[360,375,390,414,600,601,720,721,760,761,768,820,980,981,1024,1100,1180,1181,1280,1440,1920];
const nav=['#home','#research','#professor','#members','#publications','#simulation','#patents','#collaborations','#equipment','#game'];
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function auditLayout(){
 const ctx=document.createElement('canvas').getContext('2d');ctx.canvas.width=ctx.canvas.height=1;
 const rgb=color=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=color;ctx.fillRect(0,0,1,1);return Array.from(ctx.getImageData(0,0,1,1).data).map((n,i)=>i===3?n/255:n);};
 const over=(a,b)=>[0,1,2].map(i=>a[i]*a[3]+b[i]*(1-a[3])).concat(1);
 const lum=c=>c.slice(0,3).map(n=>{n/=255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4;}).reduce((a,n,i)=>a+n*[.2126,.7152,.0722][i],0);
 const ratio=(a,b)=>{const l1=lum(a),l2=lum(b);return (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);};
 const bg=el=>el?over(rgb(getComputedStyle(el).backgroundColor),bg(el.parentElement)):[255,255,255,1];
 const selectors=['.if-badge','.tag-top','.st-transfer','.pat.transfer .yr','.pat-summary .chip.tr b','.rcard .quote','.film-caption a','.research-details span:last-child','.rcard .tag','.paper .pmeta b','.paper .pno','.btn-primary','.fbtn.active','.stats .lbl','footer .foot-brand','footer .foot-desc','footer h5','footer a','footer p','.email-copy','.email-copy .hint','.foot-bottom','.build-stamp','.arcade-cta .btn-ghost'];
 const contrast=[];
 for(const selector of selectors)for(const el of document.querySelectorAll(selector)){
  const style=getComputedStyle(el),rect=el.getBoundingClientRect();if(!rect.height||!rect.width)continue;
  const back=bg(el);contrast.push({selector,ratio:ratio(over(rgb(style.color),back),back)});
 }
 // Gradient numbers must pass even at the darker cyan endpoint.
 for(const color of ['#fff','#00E6C6'])contrast.push({selector:'.stat .num gradient endpoint',ratio:ratio(rgb(color),bg(document.querySelector('.stats')))});
 if(matchMedia('(hover:hover) and (pointer:fine)').matches)for(const el of document.querySelectorAll('.film-deck')){
  const pseudo=getComputedStyle(el,'::before');contrast.push({selector:'.film-deck::before',ratio:ratio(rgb(pseudo.color),rgb(pseudo.backgroundColor))});
 }
 const small=[],brokenWords=[];
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let text;
 while(text=walker.nextNode()){
  const el=text.parentElement;if(!text.textContent.trim()||el.closest('script,style,noscript,.film-title,.plus,sup,svg,.toast'))continue;
  const rect=el.getBoundingClientRect(),style=getComputedStyle(el);
  if(!rect.width||!rect.height||style.visibility==='hidden')continue;
  if(parseFloat(style.fontSize)<12)small.push([el.className,text.textContent.trim().slice(0,40),style.fontSize]);
  if(document.documentElement.lang==='ko'&&innerWidth===390&&el.closest('.sec-head,.arcade-title,.arcade-sub,.arcade-keys,.pat-row .pt,footer,.rcard .desc')){
   for(const word of text.textContent.matchAll(/[가-힣]{2,}/g)){
    const range=document.createRange();range.setStart(text,word.index);range.setEnd(text,word.index+word[0].length);
    if(new Set([...range.getClientRects()].map(r=>Math.round(r.top))).size>1)brokenWords.push(word[0]);
   }
  }
 }
 const shortTargets=matchMedia('(pointer:coarse)').matches?[...document.querySelectorAll('.doi-link,.film-caption a,.welcome-email,.welcome-photo figcaption a,.prof-card a[href*="scholar"],.viewall a,.foot-nav a')].filter(el=>el.getBoundingClientRect().height<32).map(el=>el.className):[];
 const ifDoiSplit=[...document.querySelectorAll('.paper-links')].filter(el=>{const a=el.querySelector('a').getBoundingClientRect(),b=el.querySelector('.if-badge').getBoundingClientRect();return a.bottom<b.top||b.bottom<a.top;}).length;
 const titlesClipped=matchMedia('(max-width:760px), (pointer:coarse)').matches?[...document.querySelectorAll('.pub-row .pt,.pat-row .pt')].filter(el=>el.scrollHeight>el.clientHeight+1||el.scrollWidth>el.clientWidth+1||getComputedStyle(el).webkitLineClamp!=='none'||getComputedStyle(el).whiteSpace==='nowrap').map(el=>el.textContent):[];
 const emphasis=document.createRange();emphasis.selectNodeContents(document.querySelector('.hero-interface h1 span'));
 const heroEmphasisLines=new Set([...emphasis.getClientRects()].map(r=>Math.round(r.top))).size;
 const footerColumns=new Set([...document.querySelectorAll('.foot-nav a')].map(el=>Math.round(el.getBoundingClientRect().left))).size;
 const splitFooterLinks=[...document.querySelectorAll('.foot-nav a')].filter(el=>{const range=document.createRange();range.selectNodeContents(el);return new Set([...range.getClientRects()].map(r=>Math.round(r.top))).size>1;}).map(el=>el.textContent);
 return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,memberHeight:document.getElementById('members').getBoundingClientRect().height,heroFont:parseFloat(getComputedStyle(document.querySelector('h1')).fontSize),heroEmphasisLines,footerColumns,splitFooterLinks,minContrast:Math.min(...contrast.map(c=>c.ratio)),contrastFailures:contrast.filter(c=>c.ratio<4.5),small,shortTargets,brokenWords,ifDoiSplit,titlesClipped};
}
(async()=>{
 fs.mkdirSync('.video-work',{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 const results=[],errors=[],consoleErrors=[],missingPhotos=[];
 try{
  for(const touch of [true,false]){
   const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:touch,isMobile:touch,reducedMotion:'reduce'});
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   page.on('console',m=>{if(m.type()==='error')consoleErrors.push({text:m.text(),url:m.location().url});});
   page.on('response',r=>{if(r.status()===404&&/STUDENTS.*_v2\.jpg/.test(r.url()))missingPhotos.push(r.url());});
   await page.goto(url);await page.evaluate(()=>document.fonts.ready);
   assert.equal(await page.locator('html').getAttribute('lang'),'en','Default language is English');
   assert.deepEqual(await page.locator('#navlinks a').evaluateAll(es=>es.map(e=>e.getAttribute('href'))),nav);
   assert.deepEqual(await page.locator('.foot-col').first().locator('a').evaluateAll(es=>es.map(e=>e.getAttribute('href'))),nav);
   assert.equal(await page.locator('.paper-links').count(),await page.locator('.pub-row').count(),'Every IF/DOI pair remains grouped');
   for(const lang of ['en','ko'])for(const theme of ['light','dark']){
    await page.evaluate(({lang,theme})=>{
     document.documentElement.dataset.theme=theme;
     if(document.documentElement.lang!==lang)document.getElementById('langBtn').click();
     document.querySelectorAll('.rcard').forEach(c=>c.classList.add('open'));
     document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'));
    },{lang,theme});await sleep(450);
    for(const width of widths){
     await page.setViewportSize({width,height:width<800?844:1080});
     const data=await page.evaluate(auditLayout);results.push({touch,lang,theme,...data});
     const label=`${touch?'touch':'mouse'}/${lang}/${theme}/${width}`;
     assert(data.scrollWidth<=width,`${label} overflow`);
     for(const key of ['contrastFailures','small','shortTargets','brokenWords','titlesClipped','splitFooterLinks'])assert.deepEqual(data[key],[],`${label} ${key}`);
     assert.equal(data.ifDoiSplit,0,`${label} DOI stays with IF`);
     assert.equal(data.heroEmphasisLines,1,`${label} hero emphasis is unbroken`);
     if(width>=721)assert(data.footerColumns>=2&&data.footerColumns<=3,`${label} footer navigation uses 2–3 columns`);
     if(width<=600)assert(data.heroFont>=28&&data.heroFont<=34,`${label} mobile heading`);
     if(width===390&&lang==='ko')assert(data.memberHeight<7335.55*.6,`${label} member height reduction exceeds 40%`);
    }
    if(!touch){
     await page.setViewportSize({width:1440,height:1000});
     const alignment=await page.locator('.research-grid').evaluate(el=>{const [first,...rest]=el.children;const a=first.getBoundingClientRect(),b=rest.at(-1).getBoundingClientRect(),g=el.getBoundingClientRect();return {width:Math.abs(a.width-b.width),center:Math.abs(b.x+b.width/2-g.x-g.width/2)};});
     assert(alignment.width<1&&alignment.center<1,'Last research card keeps the same width and is centered');
     const deck=page.locator('.film-deck').first();await deck.locator('.research-film').nth(1).locator('.film-start').focus();
     assert.match(await deck.getAttribute('data-next'),lang==='ko'?/^다른 영상 1\/2 ▲ /:/^OTHER FILM 1\/2 ▲ /);
     assert.equal(await deck.locator('.research-film:not(.is-front) .film-play').evaluate(el=>getComputedStyle(el).visibility),'hidden');
     assert.equal(await deck.locator('.research-film.is-front .film-play').evaluate(el=>getComputedStyle(el).visibility),'visible');
     await deck.locator('.research-film').first().locator('.film-start').focus();
     assert.match(await deck.getAttribute('data-next'),/2\/2 ▲ /);
    }
   }
   assert.deepEqual(await page.locator('.monogram').allTextContents(),['HL','AA','XQ','HS']);
   assert(await page.locator('.pat-row .pt').evaluateAll(es=>es.every(el=>el.title===el.textContent)));
   assert(await page.locator('.pat-row.granted,.pat-row.transfer').evaluateAll(es=>es.every(el=>getComputedStyle(el).borderLeftWidth==='3px')));
   await page.setViewportSize({width:390,height:844});
   for(const id of ['members','game']){await page.locator('#'+id).scrollIntoViewIfNeeded();await sleep(800);await page.locator('#'+id).screenshot({path:`.video-work/design-${id}-${touch?'touch':'mouse'}.png`});}
   await page.locator('footer').scrollIntoViewIfNeeded();await sleep(800);await page.locator('footer').screenshot({path:'.video-work/design-footer.png'});
   await page.locator('.stats').scrollIntoViewIfNeeded();await sleep(500);await page.locator('.stats').screenshot({path:'.video-work/design-stats.png'});
   await page.reload();
   assert.equal(await page.locator('html').getAttribute('lang'),'ko','Language choice survives reload');
   assert.equal(await page.locator('#langBtn').textContent(),'KO');
   assert(await page.locator('.game-link').evaluateAll(es=>es.every(el=>new URL(el.href).searchParams.get('lang')==='ko')));
   assert.equal(await page.locator('.rcard .tags .tag').first().textContent(),'머신러닝');
   assert.equal(await page.locator('#members .rl').first().textContent(),'박사후 연구원');
   assert.equal(await page.locator('#home .hero-motion').getAttribute('aria-label'),'모션 멈춤');
   await context.close();
  }
  // Normal and reduced-motion preferences have identical explicit playback controls.
  for(const reducedMotion of ['no-preference','reduce']){
   const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion});
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto(url);await sleep(500);
   const hero=()=>page.locator('.hero-scene').evaluate(el=>el.style.transform);
   let before=await hero();await sleep(400);assert.notEqual(await hero(),before);
   await page.locator('#home .hero-motion').click();before=await hero();await sleep(2200);assert.equal(await hero(),before,'Watchdog respects manual pause');
   await page.locator('#home .hero-motion').click();await sleep(400);assert.notEqual(await hero(),before);
   await page.locator('#arcadeMotion').scrollIntoViewIfNeeded();await sleep(500);
   const dash=()=>page.locator('#arcadeFrame .dash').getAttribute('stroke-dashoffset');
   before=await dash();await sleep(200);assert.notEqual(await dash(),before);
   await page.locator('#arcadeMotion').click();before=await dash();await sleep(250);assert.equal(await dash(),before);
   assert.equal(await page.locator('#arcadeMotion').getAttribute('aria-pressed'),'true');
   await page.locator('#langBtn').click();assert.equal(await page.locator('#arcadeMotion').getAttribute('aria-label'),'포스터 모션 재생');
   await page.locator('#arcadeMotion').click();await sleep(250);assert.notEqual(await dash(),before);
   await context.close();
  }
  // Simulate a frozen rAF driver to exercise the actual self-heal path.
  const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  await context.addInitScript(()=>{window.requestAnimationFrame=()=>0;});
  const page=await context.newPage();await page.goto(url);await sleep(2600);
  const before=await page.locator('.hero-scene').evaluate(el=>el.style.transform);await sleep(200);
  assert.notEqual(await page.locator('.hero-scene').evaluate(el=>el.style.transform),before,'Interval watchdog revives stalled motion');
  await context.close();
  // Storage may be blocked; the page still loads in English without errors.
  const blocked=await browser.newContext();await blocked.addInitScript(()=>{Storage.prototype.getItem=()=>{throw new Error('Storage blocked');};Storage.prototype.setItem=()=>{throw new Error('Storage blocked');};});
  const p=await blocked.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(url);assert.equal(await p.locator('html').getAttribute('lang'),'en');await p.locator('#langBtn').click();assert.equal(await p.locator('html').getAttribute('lang'),'ko');await blocked.close();
  assert.deepEqual(errors,[],'No uncaught page errors');
  const environmentErrors=consoleErrors.filter(e=>/^https:\/\/(fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net)\//.test(e.url)&&/ERR_NETWORK_ACCESS_DENIED/.test(e.text));
  const unexpectedConsole=consoleErrors.filter(e=>!environmentErrors.includes(e)&&!(/STUDENTS.*_v2\.jpg/.test(e.url)&&/404/.test(e.text)));
  assert.deepEqual(unexpectedConsole,[],'No console errors (pending member photos reported separately)');
  fs.writeFileSync('.video-work/design-polish-results.json',JSON.stringify({results,errors,consoleErrors,environmentErrors,missingPhotos:[...new Set(missingPhotos)]},null,2));
  console.log(`PASS: ${results.length} responsive/theme/language/input combinations; contrast >=4.5; type >=12; touch >=32; full titles, word boundaries, compact members, decks, persisted/blocked storage, normal/reduced motion and self-heal; no application console errors.`);
  if(environmentErrors.length)console.log('Environment limitation: existing external font CDNs blocked by sandbox; fallback fonts used. Details in .video-work/design-polish-results.json.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
