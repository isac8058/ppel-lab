// Run against a local server: node tests/research-captions.cjs
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const url=process.env.TEST_URL||'http://127.0.0.1:8765/';
const path=require('node:path');
const data=require('../Video/research/v5/films.json').map(item=>({...item,id:item.stem,media:'v5/'+item.stem,sample:11}));
function captionAt(item,language,seconds){
 const content=fs.readFileSync(path.join(__dirname,'../Video/research',item.media+'.'+language+'.vtt'),'utf8');
 const time=text=>text.trim().split(/\s+/)[0].split(':').reduce((sum,n)=>sum*60+Number(n),0);
 for(const block of content.trim().split(/\r?\n\r?\n/)){
  const lines=block.split(/\r?\n/),index=lines.findIndex(line=>line.includes(' --> '));if(index<0)continue;
  const [start,end]=lines[index].split(' --> ');if(seconds>=time(start)&&seconds<time(end))return lines.slice(index+1).join('\n');
 }
 return ''; // Gaps between cues intentionally leave the panel empty.
}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 fs.mkdirSync(path.join(__dirname,'../.video-work'),{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  for(const reducedMotion of ['no-preference','reduce']){
   const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion});
   const page=await context.newPage(),errors=[],mediaRequests=[];page.setDefaultTimeout(15000);page.on('pageerror',error=>errors.push(error.message));
   page.on('request',request=>{if(/\.mp4(?:\?|$)/.test(request.url()))mediaRequests.push(request.url());});
   await page.goto(url);await sleep(2000);
   const motion=()=>page.evaluate(()=>({transform:getComputedStyle(document.querySelector('.hero-scene')).transform,ink:document.querySelector('.hero-signals').toDataURL()}));
   const before=await motion();await sleep(900);const after=await motion();
   if(reducedMotion==='reduce'){
    assert.deepEqual(before,after,'Reduced motion keeps the hero still');
   }else{
    assert.notEqual(before.transform,after.transform,'Hero depth motion is active');
    assert.notEqual(before.ink,after.ink,'Hero signals are active');
    await page.locator('.hero-motion').click();
    const paused=await motion();await sleep(350);
    assert.deepEqual(paused,await motion(),'Pause stops both perspective and signals');
   }
   assert.equal(await page.locator('video source[src]').count(),0,'Media stays lazy before play');
   assert.equal(mediaRequests.length,0,'No MP4 network request before a click');
   for(const card of [...new Set(data.map(item=>item.card))]){
    const starts=page.locator(`#research-${card} .film-start`);
    assert.equal(await starts.count(),2);
    for(const start of await starts.all())assert(await start.isVisible(),'Both posters are visible without tabs');
   }
   assert.equal(await page.locator('.film-error:not([hidden])').count(),0,'Unplayed lazy films must not report playback errors');
   await page.locator('#langBtn').click();
   assert.equal(mediaRequests.length,0,'Switching language before play remains lazy');
   for(const item of data){
    assert((await page.locator(`#film-${item.id}`).getAttribute('poster')).endsWith(`${item.stem}-ko.jpg`));
    assert((await page.locator(`[data-film="${item.id}"] .film-error a`).getAttribute('href')).endsWith(`${item.stem}-ko.mp4`));
   }
   for(const item of data){
    console.log(`Checking ${reducedMotion} / ${item.id}`);
    const root=page.locator(`[data-film="${item.id}"]`),video=root.locator('video');
    await root.locator('.film-start').click();
    await page.waitForFunction(id=>document.querySelector(`#film-${id}`).readyState>=1,item.id);
    assert((await video.evaluate(video=>video.currentSrc)).endsWith(`${item.stem}-ko.mp4`));
    assert(Math.abs(await video.evaluate(video=>video.duration)-item.duration)<0.15,'Video duration matches its displayed length');
    await video.evaluate((video,seconds)=>{video.pause();video.currentTime=seconds;},item.sample);
    const expectedCaption=captionAt(item,'ko',item.sample);
    await page.waitForFunction(({id,caption})=>document.querySelector(`[data-film="${id}"] .film-subtitles`).textContent===caption,{id:item.id,caption:expectedCaption});
    const bounds=await root.evaluate(root=>({video:root.querySelector('video').getBoundingClientRect().bottom,panel:root.querySelector('.film-subtitle-panel').getBoundingClientRect().top,modes:Array.from(root.querySelector('video').textTracks).map(track=>track.mode)}));
    assert(bounds.panel>=bounds.video-1,'Captions must sit outside the picture');
    assert(!bounds.modes.includes('showing'),'No native caption overlay');
   }
   const first=page.locator('[data-film="ai-paper"]');
   // All ten paused players must preserve their time through both directions.
   for(const language of ['en','ko']){
    const before=await page.evaluate(()=>{
     const times=Array.from(document.querySelectorAll('.research-film video'),v=>({id:v.id,time:v.currentTime}));
     document.querySelector('#langBtn').click();return times;
    });
    for(const item of data){
     await page.waitForFunction(({id,language})=>{
      const v=document.getElementById(id);
      return v.currentSrc.endsWith(`-${language}.mp4`)&&v.readyState>=2&&!v.seeking&&!filmSwitches.has(v);
     },{id:'film-'+item.id,language});
     const state=await page.locator('#film-'+item.id).evaluate(v=>({time:v.currentTime,paused:v.paused}));
     assert(state.paused,'Paused state survives source replacement');
     assert(Math.abs(state.time-before.find(v=>v.id==='film-'+item.id).time)<=0.5,'Language switch preserves time within 0.5 s');
     await page.waitForFunction(({id,text})=>document.getElementById('subtitles-'+id).textContent===text,{id:item.id,text:captionAt(item,language,item.sample)});
    }
   }
   // Switch while playing, then start another film to verify page-wide exclusivity.
   for(const language of ['en','ko']){
    await first.locator('video').evaluate(async v=>{v.currentTime=15;await v.play();});
    const time=await page.evaluate(()=>{const time=document.getElementById('film-ai-paper').currentTime;document.querySelector('#langBtn').click();return time;});
    await page.waitForFunction(language=>{const v=document.getElementById('film-ai-paper');return v.currentSrc.endsWith(`-${language}.mp4`)&&!v.paused&&!v.seeking&&!filmSwitches.has(v);},language);
    const restored=await first.locator('video').evaluate(v=>{const time=v.currentTime;v.pause();return time;});
    assert(Math.abs(restored-time)<=0.5,'Playing switch preserves time within 0.5 s');
   }
   await first.locator('video').evaluate(v=>v.play());
   await page.locator('#film-cherry-blossom-2').evaluate(v=>v.play());
   assert(await first.locator('video').evaluate(v=>v.paused));
   assert.equal(await page.locator('.research-film video').evaluateAll(videos=>videos.filter(v=>!v.paused).length),1);
   await page.locator('#film-cherry-blossom-2').evaluate(v=>v.pause());
   await first.locator('video').evaluate(v=>{v.currentTime=11;});
   await page.locator('#langBtn').click(); // English again
   await page.waitForFunction(text=>document.querySelector('#subtitles-ai-paper').textContent===text,captionAt(data[0],'en',data[0].sample));
   await first.locator('.film-fullscreen').click();
   await page.waitForFunction(()=>document.fullscreenElement?.classList.contains('film-viewer'));
   assert(await first.evaluate(root=>root.querySelector('.film-subtitle-panel').getBoundingClientRect().top>=root.querySelector('video').getBoundingClientRect().bottom-1));
   await page.screenshot({path:`.video-work/captions-fullscreen-${reducedMotion}.png`});
   await first.locator('.film-fullscreen').click();
   await page.setViewportSize({width:390,height:844});
   await page.reload();
   assert.equal(await page.locator('.film-start:visible').count(),10,'Both posters per card fit mobile');
   await first.scrollIntoViewIfNeeded();
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'No horizontal overflow on mobile');
   await first.screenshot({path:`.video-work/captions-mobile-${reducedMotion}.png`});
   // A real failed request must reveal the language-specific fallback.
   await page.route('**/Video/research/v5/memory-2-*.mp4*',route=>route.abort());
   await page.locator('#film-memory-2').evaluate(v=>{v.querySelector('source').src='Video/research/v5/memory-2-en.mp4?error-test';v.load();});
   await page.waitForFunction(()=>!document.querySelector('[data-film="memory-2"] .film-error').hidden);
   assert((await page.locator('[data-film="memory-2"] .film-error a').getAttribute('href')).endsWith('-en.mp4'));
   assert.deepEqual(errors,[]);console.log(`${reducedMotion}: 10 films, bilingual sources/time/state, lazy/exclusive playback, captions, fullscreen, errors, mobile and hero motion passed`);
   await context.close();
  }
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
