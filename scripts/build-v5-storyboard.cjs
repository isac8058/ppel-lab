// Generate Video/research/v5/storyboard.html and PROMPT_PACK.md from films.json (the single source of truth).
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'Video/research/v5');
const data=JSON.parse(fs.readFileSync(path.join(dir,'films.json'),'utf8').replace(/^﻿/,''));
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const castBlock=Object.values(data.cast).map(c=>c.prompt).join(' ');
const fullPrompt=clip=>`${data.style.block}\n\nCAST (match the attached reference images): ${castBlock}\n\n${clip.prompt}`;
const order=['cherry-blossom','ai-paper','energy-storage','biosensor','memory'];
const films=order.map(id=>data.films.find(f=>f.id===id));

// ---------- PROMPT_PACK.md ----------
let md=`# v5 Flow 프롬프트 팩 (생성 순서대로)\n\n생성 파일. 원본은 \`films.json\`, 수정은 \`node scripts/build-v5-storyboard.cjs\`로 다시 만든다. 각 프롬프트는 스타일 블록과 출연진 블록이 이미 앞에 붙어 있으므로 그대로 붙여 넣는다. 재료(Ingredients)는 각 클립에 적힌 것만 첨부한다.\n\n## 재료 이미지 6장\n\n`;
for(const ing of data.ingredients)md+=`### ${ing.id} · ${ing.label}\n\n\`\`\`\n${ing.prompt}\n\`\`\`\n\n`;
for(const f of films){
 md+=`## ${f.titleKo} · ${f.titleEn} (${f.id})\n\n논문: ${f.paper.journal} ${f.paper.year}, DOI ${f.paper.doi}. 포스터: 클립 ${f.posterClip}, ${f.posterTime}초.\n\n`;
 for(const c of f.clips)md+=`### ${f.id} · clip-${c.n} (완성본 ${c.timeline[0]}–${c.timeline[1]}초) · 재료 ${c.ingredients.join(', ')}\n\n비트: ${c.beatKo}\n\n\`\`\`\n${fullPrompt(c)}\n\`\`\`\n\n`;
}
fs.writeFileSync(path.join(dir,'PROMPT_PACK.md'),md);

// ---------- storyboard.html ----------
const css=`
:root{--bg:#f6f3ec;--card:#fff;--ink:#1c2528;--soft:#5b6a70;--line:#e2ddd2;--accent:#3565DC;--panel:#172226;--panel-ink:#fff;--chip:#eef1f6}
:root:not([data-theme="light"]){color-scheme:light dark}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121a1d;--card:#1b262a;--ink:#f1ede4;--soft:#a7b3b8;--line:#2c393e;--accent:#7ea2ff;--panel:#0d1417;--chip:#243136}}
:root[data-theme="dark"]{--bg:#121a1d;--card:#1b262a;--ink:#f1ede4;--soft:#a7b3b8;--line:#2c393e;--accent:#7ea2ff;--panel:#0d1417;--chip:#243136}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,"Segoe UI","Malgun Gothic","Apple SD Gothic Neo",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:30px;margin:0 0 6px;letter-spacing:-.02em}h2{font-size:22px;margin:40px 0 12px}h3{font-size:16px;margin:0 0 6px}
.lead{color:var(--soft);margin:0 0 18px;max-width:820px}
.status{display:inline-block;border:1px solid var(--line);border-radius:20px;padding:3px 12px;font-size:12px;color:var(--soft);margin-bottom:14px}
nav.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px}
nav.tabs button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:20px;padding:6px 14px;font:inherit;font-size:13px;cursor:pointer}
nav.tabs button[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card .k{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--soft)}
.film{display:none}.film.on{display:block}
.timeline{display:flex;height:34px;border-radius:8px;overflow:hidden;border:1px solid var(--line);margin:12px 0 4px;font-size:12px}
.timeline div{display:flex;align-items:center;justify-content:center;color:#fff;background:var(--accent);border-right:1px solid #fff4}
.timeline div:nth-child(even){filter:brightness(.88)}
.timeline .end{background:var(--panel);flex:0 0 6.67%}
.ticks{display:flex;justify-content:space-between;font-size:11px;color:var(--soft);margin-bottom:16px}
.clip{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
.clip header{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;justify-content:space-between}
.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:var(--chip);border-radius:6px;padding:2px 8px;font-size:12px}
.beat{margin:8px 0 10px}
details{border-top:1px dashed var(--line);padding-top:8px}summary{cursor:pointer;color:var(--accent);font-weight:600;font-size:13px}
pre{white-space:pre-wrap;word-break:break-word;background:var(--chip);border-radius:8px;padding:12px;font:12.5px/1.5 ui-monospace,Menlo,Consolas,monospace;margin:8px 0 0;overflow-x:auto}
.copy{float:right;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:6px;padding:3px 10px;font:inherit;font-size:12px;cursor:pointer}
.copy.ok{border-color:var(--accent);color:var(--accent)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--soft);font-weight:600}
.tablewrap{overflow-x:auto}
.panel{background:var(--panel);color:var(--panel-ink);border-radius:10px;padding:14px 18px;min-height:64px;display:flex;align-items:center;justify-content:center;text-align:center;font-weight:500;margin:10px 0}
.player{display:flex;gap:10px;align-items:center;margin:6px 0 4px;font-size:13px;color:var(--soft)}
input[type=range]{flex:1}
.lock li{margin:3px 0}
.foot{margin-top:40px;font-size:12px;color:var(--soft)}
@media(max-width:600px){h1{font-size:24px}.wrap{padding:18px 14px 60px}}
`;
const js=`
const D=${JSON.stringify({films,cast:data.cast,ingredients:data.ingredients,style:data.style.block})};
const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));
const castBlock=Object.values(D.cast).map(c=>c.prompt).join(' ');
const full=p=>D.style+'\\n\\nCAST (match the attached reference images): '+castBlock+'\\n\\n'+p;
function copy(btn,text){navigator.clipboard.writeText(text).then(()=>{btn.textContent='복사됨';btn.classList.add('ok');setTimeout(()=>{btn.textContent='프롬프트 복사';btn.classList.remove('ok')},1500)}).catch(()=>{btn.textContent='선택해서 복사하세요'})}
$$('.copy').forEach(b=>b.addEventListener('click',()=>{const f=D.films[+b.dataset.f],c=f.clips[+b.dataset.c];copy(b,full(c.prompt))}));
$$('.copy-ing').forEach(b=>b.addEventListener('click',()=>{copy(b,D.ingredients[+b.dataset.i].prompt)}));
$$('nav.tabs button').forEach(b=>b.addEventListener('click',()=>{$$('nav.tabs button').forEach(x=>x.setAttribute('aria-selected',x===b));$$('.film').forEach(x=>x.classList.toggle('on',x.id==='film-'+b.dataset.id));try{localStorage.setItem('ppel-v5-tab',b.dataset.id)}catch(e){}}));
let saved=null;try{saved=localStorage.getItem('ppel-v5-tab')}catch(e){}
const first=$$('nav.tabs button').find(b=>b.dataset.id===saved)||$$('nav.tabs button')[0];first.click();
$$('.player').forEach(p=>{const r=p.querySelector('input'),out=p.querySelector('output'),panel=p.parentElement.querySelector('.panel'),f=D.films[+p.dataset.f];const lang=p.querySelector('select');
 const show=()=>{const t=+r.value;out.textContent=t.toFixed(1)+' s';const cue=f.cues.find(c=>t>=c.start&&t<c.end);panel.textContent=cue?cue[lang.value]:'';};
 r.addEventListener('input',show);lang.addEventListener('change',show);show();});
`;
let html=`<title>PPEL v5 Storyboard</title>\n<style>${css}</style>\n<div class="wrap">\n<h1>PPEL+ 연구 단편 v5 스토리보드</h1>\n<span class="status">상태: ${esc(data.status)}</span>\n<p class="lead">같은 출연진, 소리 있는 실사, 다섯 편. 각 편은 Google Flow 8초 클립 4개(7초씩 사용)와 2초 논문 카드로 30초를 만든다. 원본은 <code>films.json</code>이며 이 페이지는 생성 파일이다.</p>\n`;
html+=`<h2>출연진</h2><div class="grid">`+Object.entries(data.cast).map(([k,c])=>`<div class="card"><div class="k">${esc(k)}</div><h3>${esc(c.ko)}</h3><p style="margin:0;color:var(--soft);font-size:13px">${esc(c.ko_note)}</p></div>`).join('')+`</div>`;
html+=`<h2>스타일 블록(모든 프롬프트 공통)</h2><pre>${esc(data.style.block)}</pre><p class="lead" style="margin-top:8px">${esc(data.style.whyKo)}</p>`;
html+=`<h2>재료 이미지 6장</h2><div class="grid">`+data.ingredients.map((ing,i)=>`<div class="card"><div class="k">${esc(ing.id)}</div><h3>${esc(ing.label)}</h3><button class="copy copy-ing" data-i="${i}" style="float:none;margin-bottom:6px">프롬프트 복사</button><pre style="font-size:11.5px">${esc(ing.prompt)}</pre></div>`).join('')+`</div>`;
html+=`<h2>다섯 편</h2><nav class="tabs">`+films.map(f=>`<button data-id="${f.id}" aria-selected="false">${esc(f.titleKo)}</button>`).join('')+`</nav>`;
films.forEach((f,fi)=>{
 html+=`<section class="film" id="film-${f.id}"><div class="card"><div class="k">${esc(f.id)} · ${esc(f.paper.journal)} ${f.paper.year} · DOI ${esc(f.paper.doi)}</div><h3 style="font-size:20px">${esc(f.titleKo)} <span style="color:var(--soft);font-weight:500">· ${esc(f.titleEn)}</span></h3><p style="margin:6px 0"><b>훅.</b> ${esc(f.hookKo)}</p><p style="margin:6px 0">${esc(f.loglineKo)}</p><p style="margin:6px 0;color:var(--soft);font-size:13px">구조: ${esc(f.structureKo)} · 포스터: 클립 ${f.posterClip}, ${f.posterTime}초</p></div>`;
 html+=`<div class="timeline">`+f.clips.map(c=>`<div style="flex:0 0 23.33%">클립 ${c.n} · ${c.timeline[0]}–${c.timeline[1]}s</div>`).join('')+`<div class="end">카드</div></div><div class="ticks"><span>0</span><span>7</span><span>14</span><span>21</span><span>28</span><span>30 s</span></div>`;
 f.clips.forEach((c,ci)=>{html+=`<article class="clip"><header><h3>클립 ${c.n} <span style="color:var(--soft);font-weight:500">완성본 ${c.timeline[0]}–${c.timeline[1]}초</span></h3><div class="chips">${c.ingredients.map(i=>`<span class="chip">${esc(i)}</span>`).join('')}</div></header><p class="beat">${esc(c.beatKo)}</p><details><summary>Flow 프롬프트(영문, 스타일·출연진 블록 포함)</summary><button class="copy" data-f="${fi}" data-c="${ci}">프롬프트 복사</button><pre>${esc(fullPrompt(c))}</pre></details></article>`;});
 html+=`<div class="card"><div class="k">자막 미리보기(홈페이지 하단 패널, 초안 시각)</div><div class="player" data-f="${fi}"><input type="range" min="0" max="30" step="0.1" value="0"><output>0.0 s</output><select><option value="ko">한국어</option><option value="en">English</option></select></div><div class="panel"></div><div class="tablewrap"><table><tr><th>시작</th><th>끝</th><th>한국어</th><th>English</th></tr>${f.cues.map(c=>`<tr><td>${c.start}</td><td>${c.end}</td><td>${esc(c.ko)}</td><td>${esc(c.en)}</td></tr>`).join('')}</table></div></div>`;
 html+=`<div class="card" style="margin-top:12px"><div class="k">과학 락</div><ul class="lock">${f.scienceLock.map(s=>`<li>${esc(s)}</li>`).join('')}</ul></div></section>`;
});
html+=`<p class="foot">생성: <code>node scripts/build-v5-storyboard.cjs</code> · 자막 시각은 클립 발화 시각에 맞춰 조정 예정 · 화면 안 글자 0, 자막은 하단 패널 전용</p></div>\n<script>${js}</script>\n`;
fs.writeFileSync(path.join(dir,'storyboard.html'),html);
console.log('storyboard.html and PROMPT_PACK.md written:',films.length,'films,',films.reduce((s,f)=>s+f.clips.length,0),'clips');
