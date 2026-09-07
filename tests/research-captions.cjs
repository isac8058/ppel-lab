// Run against a local server: node tests/research-captions.cjs
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const url=process.env.TEST_URL||'http://127.0.0.1:8765/';
const path=require('node:path');
const data=require('../Video/research/v4/films.json').map(item=>({...item,media:'v4/'+item.stem,sample:11}));
data.push({id:'cherry-blossom',media:'v3/cherry-action-30s',duration:30,sample:5});
function captionAt(item,language,seconds){
 const content=fs.readFileSync(path.join(__dirname,'../Video/research',item.media+'.'+language+'.vtt'),'utf8');
 const time=text=>text.trim().split(/\s+/)[0].split(':').reduce((sum,n)=>sum*60+Number(n),0);
 for(const block of content.trim().split(/\r?\n\r?\n/)){
  const lines=block.split(/\r?\n/),index=lines.findIndex(line=>line.includes(' --> '));if(index<0)continue;
  const [start,end]=lines[index].split(' --> ');if(seconds>=time(start)&&seconds<time(end))return lines.slice(index+1).join('\n');
 }
 throw new Error('No expected caption: '+item.id+' '+language+' at '+seconds);
}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try{
  for(const reducedMotion of ['no-preference','reduce']){
   const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion});
   const page=await context.newPage(),errors=[];page.setDefaultTimeout(15000);page.on('pageerror',error=>errors.push(error.message));
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
   assert.equal(await page.locator('.film-error:not([hidden])').count(),0,'Unplayed lazy films must not report playback errors');
   await page.locator('#langBtn').click();
   for(const item of data){
    console.log(`Checking ${reducedMotion} / ${item.id}`);
    const root=page.locator(`[data-film="${item.id}"]`),video=root.locator('video');
    await root.locator('.film-start').click();
    await page.waitForFunction(id=>document.querySelector(`#film-${id}`).readyState>=1,item.id);
    assert(Math.abs(await video.evaluate(video=>video.duration)-item.duration)<0.15,'Video duration matches its displayed length');
    await video.evaluate((video,seconds)=>{video.pause();video.currentTime=seconds;},item.sample);
    const expectedCaption=captionAt(item,'ko',item.sample);
    await page.waitForFunction(({id,caption})=>document.querySelector(`[data-film="${id}"] .film-subtitles`).textContent===caption,{id:item.id,caption:expectedCaption});
    const bounds=await root.evaluate(root=>({video:root.querySelector('video').getBoundingClientRect().bottom,panel:root.querySelector('.film-subtitle-panel').getBoundingClientRect().top,modes:Array.from(root.querySelector('video').textTracks).map(track=>track.mode)}));
    assert(bounds.panel>=bounds.video-1,'Captions must sit outside the picture');
    assert(!bounds.modes.includes('showing'),'No native caption overlay');
   }
   const cherry=page.locator('[data-film="cherry-blossom"]');
   await cherry.locator('video').evaluate(video=>{video.currentTime=22;});
   await page.waitForFunction(()=>document.querySelector('#subtitles-cherry-blossom').textContent==='한 번·두 번 탭의 신호를 머신러닝으로 구별합니다.');
   await cherry.screenshot({path:`.video-work/action-science-${reducedMotion}.png`});
   const first=page.locator('[data-film="ai-paper"]');
   await page.locator('#langBtn').click();
   await page.waitForFunction(text=>document.querySelector('#subtitles-ai-paper').textContent===text,captionAt(data[0],'en',data[0].sample));
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
