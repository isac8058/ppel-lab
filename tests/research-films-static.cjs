// Dependency-free structural checks: node tests/research-films-static.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const films=require('../Video/research/v5/films.json');
const decode=s=>s.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>');
// Strict explicit-tag balance (including noscript fallback markup). Raw script/style
// bodies and comments are excluded so JS operators cannot masquerade as HTML.
const markup=html.replace(/<!--[\s\S]*?-->/g,'').replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi,'');
const stack=[],nodes=[],ids=new Map();
const voids=new Set('area base br col embed hr img input link meta param source track wbr'.split(' '));
for(const match of markup.matchAll(/<\/?[a-zA-Z](?:[^"'<>]|"[^"]*"|'[^']*')*>/g)){
  const token=match[0],tag=token.match(/^<\/?([\w:-]+)/)[1].toLowerCase();
  if(token.startsWith('</')){
    assert.equal(stack.at(-1)?.tag,tag,`Unbalanced closing tag ${token}`);stack.pop();continue;
  }
  const attrs={};
  const body=token.slice(token.indexOf(tag)+tag.length,-1);
  for(const a of body.matchAll(/([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)){
    assert(!(a[1] in attrs),`Duplicate attribute ${a[1]}`);
    attrs[a[1]]=decode(a[2]??a[3]??a[4]??'');
  }
  const node={tag,attrs,parent:stack.at(-1),offset:match.index};nodes.push(node);
  if(attrs.id){assert(!ids.has(attrs.id),`Duplicate id: ${attrs.id}`);ids.set(attrs.id,node);}
  if(tag==='a')assert(!stack.some(n=>n.tag==='a'),'Nested anchor');
  if(!voids.has(tag)&&!token.endsWith('/>'))stack.push(node);
}
assert.equal(stack.length,0,'Unclosed HTML tags');
const has=(n,c)=>(n.attrs.class||'').split(/\s+/).includes(c);
const under=(n,parent)=>{for(let p=n.parent;p;p=p.parent)if(p===parent)return true;return false;};
const inside=(parent,predicate)=>nodes.filter(n=>under(n,parent)&&predicate(n));
const one=(parent,predicate)=>{const found=inside(parent,predicate);assert.equal(found.length,1);return found[0];};
assert.equal(films.length,10);
const cards=[...new Set(films.map(f=>f.card))];assert.equal(cards.length,5);
assert.equal(nodes.filter(n=>has(n,'research-film')).length,10);
const files=new Set();
for(const card of cards){
  const cardNode=ids.get('research-'+card);assert(cardNode);
  const pair=films.filter(f=>f.card===card);assert.deepEqual(pair.map(f=>f.order),[1,2]);
  assert.equal(inside(cardNode,n=>has(n,'research-film')).length,2);
  const paperList=ids.get('papers-'+card);assert(paperList);
  assert(inside(paperList,n=>n.tag==='a').some(n=>n.attrs.href==='https://doi.org/'+pair[1].doi),'Second paper missing');
  const numbers=inside(paperList,n=>has(n,'pno')).map(n=>markup.slice(n.offset).match(/>(\d+)</)[1]);
  assert.deepEqual(numbers,numbers.map((_,i)=>String(i+1).padStart(2,'0')));
}
for(const f of films){
  assert.equal(f.duration,36);assert(f.title.en&&f.title.ko&&f.doi);
  const film=nodes.find(n=>n.attrs['data-film']===f.stem);assert(film);
  // Both films sit together in the card's film deck (overlapped on pointer devices, stacked otherwise).
  assert(has(film.parent,'film-deck'),'Film is inside a film deck');
  assert.equal(film.parent.parent,ids.get('research-'+f.card),'Film deck is a direct card child');
  assert(!('hidden' in film.attrs));
  const video=ids.get('film-'+f.stem),sub=ids.get('subtitles-'+f.stem);
  assert(video&&sub&&under(video,film)&&under(sub,film));
  assert.equal(video.attrs.preload,'none');assert(!('src' in video.attrs));assert(!('autoplay' in video.attrs));
  const source=one(video,n=>n.tag==='source');assert(!('src' in source.attrs),'MP4 must remain lazy');
  const start=one(film,n=>has(n,'film-start'));assert(!('hidden' in start.attrs));
  assert.equal(start.attrs['aria-controls'],video.attrs.id);
  assert.equal(start.attrs.title,f.title.en);assert.equal(start.attrs['aria-label'],f.title.en);
  const image=one(start,n=>n.tag==='img');
  for(const lang of ['ko','en']){
    const base='Video/research/v5/'+f.stem;
    assert.equal(source.attrs['data-src-'+lang],base+'-'+lang+'.mp4');
    assert.equal(video.attrs['data-poster-'+lang],base+'-'+lang+'.jpg');
    assert.equal(image.attrs['data-src-'+lang],base+'-'+lang+'.jpg');
    assert.equal(video.attrs['data-label-'+lang],f.title[lang]);
    const track=one(video,n=>n.tag==='track'&&n.attrs.srclang===lang);
    assert.equal(track.attrs.src,base+'.'+lang+'.vtt');
    const content=fs.readFileSync(path.join(root,track.attrs.src),'utf8');
    assert(content.startsWith('WEBVTT')&&content.includes('-->'),'Valid VTT header/cues');
    [source.attrs['data-src-'+lang],video.attrs['data-poster-'+lang],track.attrs.src].forEach(p=>files.add(p));
  }
  assert.equal(video.attrs.poster,video.attrs['data-poster-en']);
  assert.equal(image.attrs.src,image.attrs['data-src-en']);
  const caption=one(film,n=>has(n,'film-caption'));
  assert.equal(one(caption,n=>n.tag==='a').attrs.href,'https://doi.org/'+f.doi);
  assert.equal(one(caption,n=>has(n,'film-note')).attrs['data-en'],'Animated dramatization · figures from the paper, not experimental footage.');
  assert.equal(one(caption,n=>has(n,'film-note')).attrs['data-ko'],'애니메이션 연출 · 수치는 논문 기준, 실제 실험 영상 아님');
  const error=one(film,n=>has(n,'film-error')),noscript=one(film,n=>n.tag==='noscript');
  for(const parent of [error,noscript])assert.equal(one(parent,n=>n.tag==='a').attrs.href,source.attrs['data-src-en']);
  one(film,n=>has(n,'film-subtitle-panel'));one(film,n=>has(n,'film-fullscreen'));
}
// Inspect every v5 URL attribute, including future additions outside the film blocks.
for(const n of nodes)for(const value of Object.values(n.attrs))if(value.startsWith('Video/research/v5/'))files.add(value);
for(const file of files)assert(fs.statSync(path.join(root,file)).size>0,`Missing/empty file ${file}`);
assert.equal(files.size,60);
assert(!html.includes('10.1016/j.cej.2024.'+'152345'));
assert.equal(html.split('10.1016/j.cej.2024.156993').length-1,3);
assert(!/30초|30 SEC|30-second|26초|26 SEC|26-second|Video\/research\/v[1-4]\//.test(html));
assert(/v20[0-9]{2}.[0-9]{2}.[0-9]{2}-[0-9]+/.test(html),'footer version');
for(const n of nodes)if(n.attrs['aria-controls'])for(const id of n.attrs['aria-controls'].split(/\s+/))assert(ids.has(id),`Broken aria-controls ${id}`);
for(const script of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)){
  if(script[0].includes('application/ld+json'))JSON.parse(script[1]);
  else new vm.Script(script[1]);
}
assert.equal((html.match(/<script src="assets\/hero-interface\.js\?v=20260928-1" defer><\/script>/g)||[]).length,1,'Load the external hero exactly once with defer');
assert(!html.includes('const hero = document.querySelector'), 'No duplicate inline hero renderer');
new vm.Script(fs.readFileSync(path.join(root,'assets/hero-interface.js'),'utf8'));
console.log('PASS: 5 cards x 2 films; 60 existing bilingual media files; lazy sources; titles/captions/papers/fallbacks; duplicate IDs 0; obsolete DOI 0; balanced HTML and valid inline/external hero JS.');
