// Render original motion graphics and assemble Gemini footage into 30-second films.
// Usage: NODE_PATH=<bundled node_modules> node scripts/render-research-films.cjs [id]
const fs = require('fs');
const path = require('path');
const {spawn, spawnSync} = require('child_process');
const {createCanvas, GlobalFonts} = require('@napi-rs/canvas');
const root = path.resolve(__dirname, '..');
const work = path.join(root,'.video-work');
const out = path.join(root,'Video','research');
fs.mkdirSync(out,{recursive:true});
fs.mkdirSync(path.join(work,'render'),{recursive:true});
const ffmpeg = process.env.FFMPEG_PATH || path.join(work,'tools','imageio_ffmpeg','binaries','ffmpeg-win-x86_64-v7.1.exe');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arial.ttf','Arial');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arialbd.ttf','Arial Bold');
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun');
const data = JSON.parse(fs.readFileSync(path.join(__dirname,'research-video-data.json'),'utf8'));
const W=1920,H=1080,FPS=24;
const canvas=createCanvas(W,H),ctx=canvas.getContext('2d');
const ink='#223036',paper='#F7F4EB',muted='#68716D';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
function rounded(x,y,w,h,r,fill,stroke){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=3;ctx.stroke()}}
function line(x1,y1,x2,y2,color=ink,width=5){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.lineWidth=width;ctx.lineCap='round';ctx.strokeStyle=color;ctx.stroke()}
function text(s,x,y,size=32,color=ink,align='left',bold=false){const font=n=>`${bold?'700':'400'} ${n}px ${bold?'Arial Bold':'Arial'}`;ctx.font=font(size);ctx.fillStyle=color;ctx.textAlign=align;if(!s.includes('₂')){ctx.fillText(s,x,y);return}const runs=s.split(/(₂)/).map(v=>{ctx.font=font(v==='₂'?size*.7:size);return {v,w:ctx.measureText(v==='₂'?'2':v).width}}),width=runs.reduce((a,r)=>a+r.w,0);let xx=x-(align==='center'?width/2:align==='right'?width:0);ctx.textAlign='left';for(const r of runs){ctx.font=font(r.v==='₂'?size*.7:size);ctx.fillText(r.v==='₂'?'2':r.v,xx,y+(r.v==='₂'?size*.18:0));xx+=r.w}ctx.font=font(size);ctx.textAlign=align}
function circle(x,y,r,fill,stroke){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=3;ctx.stroke()}}
function shadow(x,y,rx,ry){ctx.save();ctx.filter='blur(12px)';ctx.fillStyle='#1e29391a';ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();ctx.restore()}
function eye(x,y,r=8,dx=0){circle(x,y,r+7,'#fff');circle(x+dx,y,r,ink)}
function particle(x,y,color='#EF826A',r=22,face=true){shadow(x,y+r+13,r*.8,8);circle(x,y,r,color);if(face){eye(x-r*.3,y-2,3);eye(x+r*.3,y-2,3);ctx.beginPath();ctx.arc(x,y+4,r*.32,0,Math.PI);ctx.strokeStyle=ink;ctx.lineWidth=2;ctx.stroke()}}
function pill(s,x,y,color,w=250){rounded(x-w/2,y-34,w,56,28,color);text(s,x,y+3,24,'#fff','center',true)}
function arrow(x,y,dx,color){line(x,y,x+dx,y,color,5);line(x+dx,y,x+dx-16,y-13,color,5);line(x+dx,y,x+dx-16,y+13,color,5)}
function header(d,t){ctx.fillStyle=paper;ctx.fillRect(0,0,W,H);ctx.fillStyle=d.soft;ctx.beginPath();ctx.ellipse(1300,350,690,450,-.2,0,Math.PI*2);ctx.fill();for(let i=0;i<90;i++){ctx.globalAlpha=.08;circle((i*317)%W,(i*157)%H,2,ink)}ctx.globalAlpha=1;text('PPEL+',92,90,40,ink,'left',true);text('TINY MATERIALS. BIG IDEAS.',270,88,21,muted);text(`${d.index} / RESEARCH SHORTS`,W-92,88,24,muted,'right');text(d.scienceEn,92,192,53,ink,'left',true);text('ANIMATED RESEARCH CONCEPT',92,H-67,20,muted);text(d.journal,W-92,H-67,20,muted,'right');rounded(92,H-32,W-184,5,3,'#D8DAD0');rounded(92,H-32,(W-184)*clamp((t+8)/30),5,3,d.color)}
function wave(x,y,w,h,t,color){rounded(x,y,w,h,24,'#fff', '#DBDED6');ctx.save();ctx.beginPath();ctx.rect(x+20,y+20,w-40,h-40);ctx.clip();ctx.strokeStyle=color;ctx.lineWidth=5;ctx.beginPath();for(let i=0;i<w-40;i++){let phase=((i/90-t*1.7)%5+5)%5;let v=Math.exp(-Math.pow((phase-2)*4,2))-.35*Math.exp(-Math.pow((phase-2.35)*6,2));let yy=y+h/2-v*h*.35;if(i===0)ctx.moveTo(x+20+i,yy);else ctx.lineTo(x+20+i,yy)}ctx.stroke();ctx.restore()}
function tiltedCard(x,y,w,h,color,angle=0){ctx.save();ctx.translate(x,y);ctx.rotate(angle);shadow(0,h/2+18,w*.45,18);rounded(-w/2,-h/2,w,h,25,color,'#BAC6BE');ctx.restore()}
function energy(d,t){
  const plateX=610,plateY=535;
  for(let i=4;i>=0;i--){shadow(plateX,plateY+i*28+94,210,16);rounded(plateX-225,plateY-74+i*28,450,100,18,i%2?'#4E5C61':'#34434A')}
  text('MXene',plateX,770,40,ink,'center',true);
  for(let i=0;i<5;i++){let yy=405+i*59;circle(980,yy,32,'#8CC8B1');if(i===2){eye(971,yy-4,4);eye(989,yy-4,4);line(965,yy-23,976,yy-18,ink,5);line(985,yy-18,997,yy-23,ink,5)}}
  pill('MnO₂',980,815,'#458E74',180);
  for(let i=0;i<4;i++){let u=(t*.20+i*.24)%1;let x=1530-u*540,y=420+i*92+Math.sin(t*3+i)*9;const stop=u>.91;if(stop)x=1026+(u-.91)*170;particle(x,y,'#EA826E',25);particle(x+40,y,'#EA826E',25);line(x+14,y,x+25,y,'#DA725F',12)}
  text('O₂',1470,815,35,ink,'center',true);
  arrow(890,520,43,'#809890');
  const reveal=smooth((t-7)/1.0);ctx.globalAlpha=reveal;rounded(1130,865,605,61,20,'#fff');text('Less oxidation. More stable ink.',1432,905,27,d.color,'center',true);ctx.globalAlpha=1;
}
function cherry(d,t){
 const tap=Math.pow(Math.max(0,Math.sin(t*3.4)),8),top=468+tap*70;
 shadow(596,745,305,30);rounded(345,625,500,42,12,'#9CAFB2');rounded(345,590,500,37,11,'#FCFCF5','#CBD7D1');
 rounded(345,top,500,32,12,'#DADFDA','#AAB9B4');
 for(let i=0;i<14;i++){ctx.save();ctx.translate(382+(i%7)*66,top+48+Math.floor(i/7)*32);ctx.rotate(Math.sin(i)*.6);ctx.fillStyle=i%2?'#EBAABC':'#DC83A1';ctx.beginPath();ctx.ellipse(0,0,23,12,0,0,Math.PI*2);ctx.fill();ctx.restore()}
 line(845,608,960,608,'#CD7796',6);line(960,608,960,505,'#CD7796',6);line(960,505,1130,505,'#CD7796',6);
 pill('PETAL LAYER',595,358,d.color,250);text('touch / release',596,806,34,ink,'center');
 const n=Math.floor(t/3)%2+1;
 rounded(1120,374,600,260,24,'#fff','#DBDED6');
 ctx.beginPath();ctx.lineWidth=5;ctx.strokeStyle=d.color;
 for(let i=0;i<550;i++){const p=i/550,centers=n===1?[.5]:[.36,.65];let value=0;for(const c of centers)value+=Math.exp(-Math.pow((p-c)*30,2))-.34*Math.exp(-Math.pow((p-c-.045)*36,2));const xx=1145+i,yy=517-value*82;if(i===0)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy)}ctx.stroke();
 circle(1150+(t%3)/3*540,605,5,d.color);
 text('electrical signal',1420,703,34,ink,'center');
 for(let i=0;i<8;i++){let p=(t*.43+i/8)%1;circle(858+p*256,608-Math.min(p*6,1)*103,6,d.color)}
 pill(n===1?'ONE TAP':'TWO TAPS',1420,815,d.color,240);
}
function ai(d,t){
 shadow(520,695,280,30);ctx.save();ctx.translate(520,552);ctx.rotate(-.07);rounded(-245,-110,490,245,14,'#F3EDD7','#CFC7AE');for(let i=0;i<90;i++){let x=(i*79)%420-210,y=(i*53)%185-90;line(x,y,x+22,y+3,'#D4CDB9',1)}ctx.restore();
 const step=Math.max(0,Math.sin(t*2.6));ctx.save();ctx.translate(520,358+step*132);ctx.rotate(-.15+step*.15);rounded(-135,-60,290,94,30,'#4E6E87');rounded(-145,10,316,38,18,'#F5FAFA','#C3D0CE');for(let i=0;i<4;i++)line(-75+i*32,-28,-45+i*32,0,'#fff',6);ctx.restore();
 text('mulberry paper',520,803,34,ink,'center');arrow(805,555,120,d.color);wave(1010,352,640,185,t,d.color);rounded(1117,610,440,164,24,d.color);text('AI',1337,704,65,'#fff','center',true);
 for(let i=0;i<3;i++){let y=824+i*23;rounded(1100,y,360,10,5,'#DCE3E5');rounded(1100,y,80+250*smooth((t-4-i*.3)/2),10,5,i===1?d.color:'#A3B1BE')}
 text('pattern analysis',1337,948,28,d.color,'center',true);
}
function dna(x,y,scale,t){for(let i=0;i<16;i++){let yy=y+i*22*scale,xx=Math.sin(i*.58+t)*60*scale;line(x-xx,yy,x+xx,yy,'#BACDC8',4*scale);circle(x-xx,yy,9*scale,i%4===0?'#E08BA5':'#59A893');circle(x+xx,yy,9*scale,'#96B9C7')}}
function bio(d,t){
 ctx.save();ctx.translate(370,553);ctx.rotate(-.2);rounded(-45,-174,90,330,10,'#EFC35F');ctx.fillStyle='#CCAC83';ctx.beginPath();ctx.moveTo(-45,155);ctx.lineTo(45,155);ctx.lineTo(0,226);ctx.closePath();ctx.fill();ctx.fillStyle='#3E494C';ctx.beginPath();ctx.moveTo(-17,200);ctx.lineTo(17,200);ctx.lineTo(0,226);ctx.closePath();ctx.fill();ctx.restore();text('graphite',370,845,33,ink,'center');
 arrow(480,540,100,d.color);
 for(let i=0;i<10;i++){const a=-Math.PI/2+i*.67;let x=760+Math.cos(a)*98,y=520+Math.sin(a)*115;line(760,600,x,y,'#3C5753',11);for(let j=0;j<3;j++){let xx=x+Math.cos(a+j*.5)*50,yy=y+Math.sin(a+j*.5)*50;line(x,y,xx,yy,'#3C5753',5)}}
 text('tree-like graphene',760,845,30,ink,'center');arrow(920,540,96,d.color);dna(1160,370,1,t*.5);pill('5hmC',1160,815,d.color,170);
 rounded(1470,359,195,365,32,'#2D4144');rounded(1484,377,167,309,19,'#D6EBDF');wave(1498,440,139,129,t,d.color);text('wireless',1567,845,31,ink,'center');
 for(let i=0;i<3;i++){ctx.beginPath();ctx.arc(1400,530,30+i*25,-.85,.85);ctx.strokeStyle=d.color;ctx.globalAlpha=.3+.6*((t+i*.25)%1);ctx.lineWidth=5;ctx.stroke()}ctx.globalAlpha=1;
}
function memory(d,t){
 for(let row=0;row<2;row++){let y=420+row*268;rounded(370,y-52,280,130,22,row?'#9C83C3':'#D9D2E4');text(row?'LOW R':'HIGH R',510,y+27,34,ink,'center',true);line(650,y+12,1510,y+12,row?'#8D72B8':'#C8BBD8',row?14:6);
   const n=row?12:3;for(let i=0;i<n;i++){let p=(t*(row?.17:.07)+i/n)%1;particle(704+p*730,y+10+Math.sin(p*8)*2,row?'#A186C7':'#C5B5D9',21)}
 }
 text('two states',510,891,34,ink,'center');text('information',1230,891,34,ink,'center');
 pill('A RESEARCH REVIEW',960,314,d.color,340);
}
function result(d,t){const k=smooth((t-8)/.8);ctx.globalAlpha=k;rounded(110,870,760,74,25,'#fff');text(d.id==='memory'?'A review of materials and mechanisms.':d.id==='biosensor'?'A DNA marker, measured wirelessly.':d.id==='ai-paper'?'Sensor data → machine learning.':d.id==='cherry-blossom'?'Single and double taps, classified.':'Printed, flexible energy storage.',490,920,27,d.color,'center',true);ctx.globalAlpha=1}
function graphic(d,t){header(d,t);({ 'energy-storage':energy,'cherry-blossom':cherry,'ai-paper':ai,biosensor:bio,memory})[d.id](d,t);if(t>8)result(d,t)}
function endcard(d,t){ctx.fillStyle=ink;ctx.fillRect(0,0,W,H);ctx.globalAlpha=.10;circle(W-230,110,490,d.color);ctx.globalAlpha=1;text('PPEL+',100,150,76,'#fff','left',true);text('SMALL MATERIALS. BIG POSSIBILITIES.',100,225,26,'#B4C2BC');text(d.paperShort,100,510,50,'#fff','left',true);text(d.journal,100,600,32,'#BACBC3');text('doi.org/'+d.doi,100,680,29,'#BACBC3');rounded(100,810,280,68,34,d.color);text('READ THE PAPER',240,855,24,'#fff','center',true);particle(1600+Math.sin(t*4)*35,795-Math.abs(Math.sin(t*3))*42,d.color,70);text('30 SECOND SCIENCE',W-100,H-85,23,'#B4C2BC','right')}
const comedy=require('./research-comedy-scenes.cjs')({ctx,W,H,rounded,line,text,circle,eye,shadow,particle,smooth,clamp});
function nativeFrame(d,t){if(t<8)comedy(d,t,'setup');else if(t<20)graphic(d,t-8);else if(t<28)comedy(d,t-20,'punch');else endcard(d,t-28)}
function run(args){const r=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y',...args],{stdio:'inherit'});if(r.status!==0)throw new Error(`ffmpeg failed ${r.status}`)}
async function rawRender(file,d,seconds,draw){const enc=spawn(ffmpeg,['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size',`${W}x${H}`,'-framerate',String(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p',file],{stdio:['pipe','inherit','inherit']});const done=new Promise((res,rej)=>{enc.on('close',c=>c===0?res():rej(new Error('render failed '+c)));enc.on('error',rej)});for(let f=0;f<seconds*FPS;f++){draw(d,f/FPS);const bytes=ctx.getImageData(0,0,W,H).data;if(!enc.stdin.write(bytes))await new Promise(r=>enc.stdin.once('drain',r))}enc.stdin.end();await done}
function wav(file,seconds){const sr=48000,n=sr*seconds,buf=Buffer.alloc(44+n*2);buf.write('RIFF');buf.writeUInt32LE(36+n*2,4);buf.write('WAVE',8);buf.write('fmt ',12);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(1,22);buf.writeUInt32LE(sr,24);buf.writeUInt32LE(sr*2,28);buf.writeUInt16LE(2,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(n*2,40);const notes=[196,246.94,293.66,392,329.63,293.66,246.94,220];for(let i=0;i<n;i++){const t=i/sr,beat=t%.5,j=Math.floor(t/.5)%notes.length;let v=(Math.sin(2*Math.PI*notes[j]*t)+.23*Math.sin(2*Math.PI*notes[j]*2*t))*Math.exp(-beat*9)*.065;v+=Math.sin(2*Math.PI*62*t)*Math.exp(-(t%1)*28)*.05;v*=Math.min(t*2,1,(seconds-t)*2);buf.writeInt16LE(Math.round(clamp(v,-1,1)*32767),44+i*2)}fs.writeFileSync(file,buf)}
function stamp(s){let m=Math.floor(s/60),sec=s%60;return `00:${String(m).padStart(2,'0')}:${sec.toFixed(3).padStart(6,'0')}`}
async function build(d){
 const src=path.join(work,'sources',d.id+'.mp4');if(!fs.existsSync(src))throw new Error('Missing source '+src);
 const dir=path.join(work,'render',d.id);fs.mkdirSync(dir,{recursive:true});
 console.log('Rendering graphics: '+d.id);
 await rawRender(path.join(dir,'graphic.mp4'),d,14,graphic);
 await rawRender(path.join(dir,'end.mp4'),d,2,endcard);
 const music=path.join(work,'render','music.wav');if(!fs.existsSync(music))wav(music,30);
 // Story 0–8, original explanatory animation 8–22, callback 22–28, reference 28–30.
 const vf='scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0xF7F4EB,setsar=1,fps=24';
 const fc=`[0:v]trim=0:8,setpts=PTS-STARTPTS,${vf}[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=4:10,setpts=PTS-STARTPTS,${vf}[c];[2:v]setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0[v];[0:a]atrim=0:8,asetpts=PTS-STARTPTS[a0];[3:a]atrim=8:22,asetpts=PTS-STARTPTS[a1];[0:a]atrim=4:10,asetpts=PTS-STARTPTS[a2];[3:a]atrim=28:30,asetpts=PTS-STARTPTS,afade=t=out:st=1:d=1[a3];[a0][a1][a2][a3]concat=n=4:v=0:a=1[audio]`;
 run(['-i',src,'-i',path.join(dir,'graphic.mp4'),'-i',path.join(dir,'end.mp4'),'-i',music,'-filter_complex',fc,'-map','[v]','-map','[audio]','-t','30','-c:v','libx264','-preset','slow','-crf','24','-maxrate','3500k','-bufsize','7000k','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,d.id+'.mp4')]);
 run(['-ss','1.8','-i',src,'-frames:v','1','-vf','scale=960:-2','-q:v','3',path.join(out,d.id+'.jpg')]);
 for(const [lang,col] of [['en',2],['ko',3]]){let vtt='WEBVTT\n\n';d.captions.forEach((c,i)=>{vtt+=`${i+1}\n${stamp(c[0])} --> ${stamp(c[1])}\n${c[col]}\n\n`});fs.writeFileSync(path.join(out,`${d.id}.${lang}.vtt`),vtt)}
 console.log('Completed: '+d.id);
}
function captions(d){for(const [lang,col] of [['en',2],['ko',3]]){let vtt='WEBVTT\n\n';d.captions.forEach((c,i)=>{vtt+=`${i+1}\n${stamp(c[0])} --> ${stamp(c[1])}\n${c[col]}\n\n`});fs.writeFileSync(path.join(out,`${d.id}.${lang}.vtt`),vtt)}}
async function nativeBuild(d){
 const dir=path.join(work,'render',d.id);fs.mkdirSync(dir,{recursive:true});
 console.log('Rendering complete original film: '+d.id);
 const movie=path.join(dir,'native.mp4'),music=path.join(work,'render','music.wav');
 await rawRender(movie,d,30,nativeFrame);if(!fs.existsSync(music))wav(music,30);
 run(['-i',movie,'-i',music,'-t','30','-c:v','libx264','-preset','slow','-crf','23','-maxrate','2600k','-bufsize','5200k','-af','volume=2.3,afade=t=out:st=28:d=2','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,d.id+'.mp4')]);
 nativeFrame(d,d.id==='biosensor'?5.6:d.id==='cherry-blossom'?1.8:5.7);
 const thumb=createCanvas(960,540);thumb.getContext('2d').drawImage(canvas,0,0,960,540);fs.writeFileSync(path.join(out,d.id+'.jpg'),thumb.toBuffer('image/jpeg'));
 captions(d);console.log('Completed: '+d.id);
}
(async()=>{
 const args=process.argv.slice(2),selected=data.filter(d=>!args.some(a=>!a.startsWith('--'))||args.includes(d.id));
 if(args.includes('--frames')){for(const d of selected){for(const t of [1,3,6,12,18,22,26,29]){nativeFrame(d,t);fs.writeFileSync(path.join(work,'render',`${d.id}-${t}.png`),canvas.toBuffer('image/png'))}}return}
 for(const d of selected)await (args.includes('--native')?nativeBuild(d):build(d));
})().catch(e=>{console.error(e);process.exit(1)});
