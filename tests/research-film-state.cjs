// Run the actual page functions with deterministic media events; no browser/codec.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const code=html.slice(html.indexOf('const filmSwitches='),html.indexOf("document.querySelectorAll('.rcard').forEach"));
class Element{
  constructor(){this.attrs={};this.dataset={};this.hidden=false;this.textContent='';}
  getAttribute(k){return this.attrs[k]??null;}
  setAttribute(k,v){this.attrs[k]=v;}
  set src(v){this.attrs.src=v;}
  get src(){return this.attrs.src;}
}
class Video extends EventTarget{
  constructor(stem){
    super();this.stem=stem;this.dataset={labelEn:stem+' EN',labelKo:stem+' KO',posterEn:stem+'-en.jpg',posterKo:stem+'-ko.jpg'};
    this.attrs={};this.source=new Element();this.source.dataset={srcEn:stem+'-en.mp4',srcKo:stem+'-ko.mp4'};
    this._time=0;this.duration=36;this.paused=true;this.ended=false;this.seeking=false;this.readyState=0;this.playbackRate=1;this.loads=0;this.plays=0;
    this.textTracks=['en','ko'].map(language=>({language,mode:'disabled',activeCues:[]}));
    this.parts=Object.fromEntries(['.film-error','.film-error a','.film-subtitles','.film-fullscreen','.film-start','.film-viewer','noscript'].map(s=>[s,new Element()]));
    this.parts.noscript.textContent=`<p><a href="${stem}-en.mp4">Watch</a></p>`;
    this.image=new Element();this.image.dataset={srcEn:stem+'-en.jpg',srcKo:stem+'-ko.jpg'};
    this.parts['.film-start'].querySelector=()=>this.image;
    this.film={querySelector:s=>this.parts[s]};
  }
  get currentTime(){return this._time;}
  set currentTime(value){this._time=value;this.seeking=true;}
  setAttribute(k,v){this.attrs[k]=v;}
  querySelector(){return this.source;}
  closest(){return this.film;}
  pause(){this.paused=true;}
  play(){this.paused=false;this.plays++;return Promise.resolve();}
  load(){this.loads++;this.readyState=0;this._time=0;this.paused=true;this.seeking=false;this.playbackRate=1;}
  metadata(){this.readyState=1;this.dispatchEvent(new Event('loadedmetadata'));}
  seeked(){this.seeking=false;this.dispatchEvent(new Event('seeked'));}
  settle(){this.metadata();this.seeked();}
}
const videos=Array.from({length:10},(_,i)=>new Video('film-'+i));
const context=vm.createContext({document:{querySelectorAll:()=>videos,fullscreenElement:null},lang:'en'});
vm.runInContext(code,context);
const run=js=>vm.runInContext(js,context);
context.videos=videos;
run('syncFilmLanguage()');
assert(videos.every(v=>v.loads===0&&!v.source.src),'Initial language sync cannot fetch MP4');
context.lang='ko';run('syncFilmLanguage()');
assert(videos.every(v=>v.loads===0&&!v.source.src),'Unplayed language switch stays lazy');
for(const v of videos){
  assert.equal(v.poster,v.stem+'-ko.jpg');assert.equal(v.image.src,v.poster);
  assert.equal(v.parts['.film-error a'].href,v.stem+'-ko.mp4');
  assert(v.parts.noscript.textContent.includes(v.stem+'-ko.mp4'));
  assert.equal(v.parts['.film-start'].attrs['aria-label'],v.stem+' KO');
  v.source.src=v.stem+'-ko.mp4';v.readyState=1;v.currentTime=12.345;v.seeking=false;
}
// All ten paused videos round-trip while preserving the exact timestamp.
for(const language of ['en','ko']){
  context.lang=language;run('syncFilmLanguage()');
  for(const v of videos){v.settle();assert.equal(v.currentTime,12.345);assert(v.paused);assert.equal(v.source.src,v.stem+'-'+language+'.mp4');}
}
const a=videos[0],b=videos[1];
run('claimFilmPlayback(videos[0])');a.play();a.playbackRate=1.5;
context.lang='en';run('syncFilmLanguage()');a.settle();
assert(!a.paused);assert.equal(a.currentTime,12.345);assert.equal(a.playbackRate,1.5);
for(const v of videos.slice(1))v.settle();
// Rapid KO -> EN before metadata must retain the pre-load timestamp and intent.
a.currentTime=18.75;a.seeking=false;
context.lang='ko';run('syncFilmLanguage()');
context.lang='en';run('syncFilmLanguage()');
for(const v of videos)v.settle();
assert.equal(a.currentTime,18.75);assert(!a.paused);assert.equal(a.source.src,a.stem+'-en.mp4');
assert.equal(run('filmSwitches.has(videos[0])'),false);
// A switch after metadata but before seeked must cancel the old completion.
context.lang='ko';run('syncFilmLanguage()');a.metadata();
context.lang='en';run('syncFilmLanguage()');
const plays=a.plays;a.seeked();assert.equal(a.plays,plays,'Stale seeked must not resume');
for(const v of videos)v.settle();assert.equal(a.currentTime,18.75);assert(!a.paused);
// Starting another video wins over a pending resume, regardless of completion order.
context.lang='ko';run('syncFilmLanguage()');
run('claimFilmPlayback(videos[1])');b.play();a.settle();b.settle();
assert(a.paused,'A replaced player must not steal playback back');
assert(!b.paused,'The newly selected player resumes after its pending switch');
assert.equal(videos.filter(v=>!v.paused).length,1);
for(const v of videos.slice(2))v.settle();
// Ended/paused videos restore the final frame without restarting.
a.currentTime=36;a.ended=true;a.pause();
context.lang='en';run('syncFilmLanguage()');a.settle();
assert.equal(a.currentTime,36);assert(a.paused);
for(const v of videos.slice(1))v.settle();
const loads=videos.map(v=>v.loads);run('syncFilmLanguage()');
assert.deepEqual(videos.map(v=>v.loads),loads,'Metadata/fullscreen sync with unchanged language cannot reload');
console.log('PASS: actual page switch functions; 10 lazy players; bilingual posters/links; paused/playing time preservation; playback rate; rapid-switch races; exclusive playback; ended state; no redundant reloads.');
