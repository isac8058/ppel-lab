// Run against a local server: node tests/research-captions.cjs
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const url=process.env.TEST_URL||'http://127.0.0.1:8765/';
const data=require('../scripts/research-video-data.json');
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  for(const reducedMotion of ['no-preference','reduce']){
   const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion});
   const page=await context.newPage(),errors=[];page.setDefaultTimeout(15000);page.on('pageerror',error=>errors.push(error.message));
   await page.goto(url);await sleep(2000);
   const motion=()=>page.evaluate(()=>({transform:getComputedStyle(document.querySelector('.hero-sway')).transform,ink:document.querySelector('#inkflow').toDataURL()}));
   const before=await motion();await sleep(900);const after=await motion();
   assert.notEqual(before.transform,after.transform,'Hero sway remains active');
   assert.notEqual(before.ink,after.ink,'Hero ink remains active');
   assert.equal(await page.locator('video source[src]').count(),0,'Media stays lazy before play');
   await page.locator('#langBtn').click();
   for(const item of data){
    console.log(`Checking ${reducedMotion} / ${item.id}`);
    const root=page.locator(`[data-film="${item.id}"]`),video=root.locator('video');
    await root.locator('.film-start').click();
    await page.waitForFunction(id=>document.querySelector(`#film-${id}`).readyState>=1,item.id);
    assert.equal(await video.evaluate(video=>video.duration),30);
    await video.evaluate(video=>{video.pause();video.currentTime=10;});
    const expectedCaption=item.id==='cherry-blossom'?'오늘 수율 좋다!':item.captions[2][3];
    await page.waitForFunction(({id,caption})=>document.querySelector(`[data-film="${id}"] .film-subtitles`).textContent===caption,{id:item.id,caption:expectedCaption});
    const bounds=await root.evaluate(root=>({video:root.querySelector('video').getBoundingClientRect().bottom,panel:root.querySelector('.film-subtitle-panel').getBoundingClientRect().top,modes:Array.from(root.querySelector('video').textTracks).map(track=>track.mode)}));
    assert(bounds.panel>=bounds.video-1,'Captions must sit outside the picture');
    assert(!bounds.modes.includes('showing'),'No native caption overlay');
   }
   const cherry=page.locator('[data-film="cherry-blossom"]');
   await cherry.locator('video').evaluate(video=>{video.currentTime=25;});
   await page.waitForFunction(()=>document.querySelector('#subtitles-cherry-blossom').textContent==='벚꽃잎 소자의 단일·이중 탭 신호를 머신러닝으로 구별합니다.');
   await cherry.screenshot({path:`.video-work/anime-science-${reducedMotion}.png`});
   const first=page.locator('[data-film="ai-paper"]');
   await page.locator('#langBtn').click();
   await page.waitForFunction(text=>document.querySelector('#subtitles-ai-paper').textContent===text,data[0].captions[2][2]);
   await first.locator('.film-fullscreen').click();
   await page.waitForFunction(()=>document.fullscreenElement?.classList.contains('film-viewer'));
   assert(await first.evaluate(root=>root.querySelector('.film-subtitle-panel').getBoundingClientRect().top>=root.querySelector('video').getBoundingClientRect().bottom-1));
   await page.screenshot({path:`.video-work/captions-fullscreen-${reducedMotion}.png`});
   await first.locator('.film-fullscreen').click();
   await page.setViewportSize({width:390,height:844});
   await first.scrollIntoViewIfNeeded();
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow on mobile');
   await first.screenshot({path:`.video-work/captions-mobile-${reducedMotion}.png`});
   assert.deepEqual(errors,[]);console.log(`${reducedMotion}: 5 films, Korean/English cues, seeking, fullscreen, mobile and hero motion passed`);
   await context.close();
  }
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
