// Assemble the v5 research films: four reviewed Flow clips (7 s each) plus a two-second paper card.
// Usage: node scripts/assemble-v5.cjs [film-id ...]   (requires FFmpeg and @napi-rs/canvas, like the v3 script)
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas}=require('@napi-rs/canvas');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'Video/research/v5');
const data=JSON.parse(fs.readFileSync(path.join(dir,'films.json'),'utf8').replace(/^﻿/,''));
const ffmpeg=process.env.FFMPEG_PATH||path.join(root,'.video-work/tools/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe');
const work=path.join(root,'.video-work/v5');fs.mkdirSync(work,{recursive:true});
const {width:W,height:H,fps:FPS,durationSeconds:TOTAL,footageSeconds:FOOTAGE,endCardSeconds:CARD}=data.output;
const wanted=process.argv.slice(2);
const films=data.films.filter(f=>!wanted.length||wanted.includes(f.id));
if(!films.length)throw Error('No matching film id. Known: '+data.films.map(f=>f.id).join(', '));

function paperCard(film){
 const c=createCanvas(W,H),ctx=c.getContext('2d');
 ctx.fillStyle='#172226';ctx.fillRect(0,0,W,H);
 ctx.fillStyle='#eddbb0';ctx.font='bold 26px Arial';ctx.fillText('PPEL+ RESEARCH SHORT',100,170);
 ctx.fillStyle='#fffaf0';ctx.font='bold 64px Arial';ctx.fillText(film.paper.cardEn,100,300);
 ctx.fillStyle='#dbcdd0';ctx.font='28px Arial';ctx.fillText(`${film.paper.journal} · ${film.paper.year}`,100,390);
 ctx.font='24px Arial';ctx.fillText(film.paper.doi,100,435);
 ctx.fillStyle='#eddbb0';ctx.font='bold 24px Arial';ctx.fillText('READ THE PAPER  →',100,550);
 const file=path.join(work,`${film.id}-card.png`);fs.writeFileSync(file,c.toBuffer('image/png'));return file;
}
const stamp=t=>`00:00:${t.toFixed(3).padStart(6,'0')}`;
const normalize=`fps=${FPS},scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2,setsar=1`;

for(const film of films){
 const folder=path.join(dir,film.id);
 const plan=fs.existsSync(path.join(folder,'clips.json'))?JSON.parse(fs.readFileSync(path.join(folder,'clips.json'),'utf8').replace(/^﻿/,'')).clips:[];
 const clips=film.clips.map(spec=>{
  const p=plan.find(x=>x.n===spec.n)||{};
  const file=path.join(folder,p.file||`clip-${spec.n}.mp4`);
  if(!fs.existsSync(file))throw Error(`Missing clip: ${path.relative(root,file)} (generate it in Flow first, see ASTRA_FLOW_RUNBOOK.md)`);
  const sourceStart=Number.isFinite(p.sourceStart)?p.sourceStart:data.clipPlan.defaultSourceStart;
  const useDuration=Number.isFinite(p.useDuration)?p.useDuration:data.clipPlan.useSeconds;
  return {n:spec.n,file,sourceStart,useDuration};
 });
 const total=clips.reduce((s,c)=>s+c.useDuration,0);
 if(Math.abs(total-FOOTAGE)>0.01)throw Error(`${film.id}: clip durations sum to ${total}s, expected ${FOOTAGE}s (adjust useDuration in clips.json)`);
 const filters=[],loudness=[];
 clips.forEach((clip,i)=>{
  const measured=spawnSync(ffmpeg,['-hide_banner','-ss',String(clip.sourceStart),'-t',String(clip.useDuration),'-i',clip.file,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],{encoding:'utf8'});
  if(measured.status)throw Error(`Audio analysis failed: ${clip.file}`);
  const stats=JSON.parse(measured.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)?.[0]||'null');
  if(!stats||!Number.isFinite(Number(stats.input_i)))throw Error(`Missing loudness data: ${clip.file}`);
  loudness.push({file:path.basename(clip.file),...stats});
  const audio=`loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${stats.input_i}:measured_TP=${stats.input_tp}:measured_LRA=${stats.input_lra}:measured_thresh=${stats.input_thresh}:offset=${stats.target_offset}:linear=true`;
  filters.push(`[${i}:v]trim=start=${clip.sourceStart}:duration=${clip.useDuration},setpts=PTS-STARTPTS,${normalize}[v${i}]`);
  filters.push(`[${i}:a]atrim=start=${clip.sourceStart}:duration=${clip.useDuration},asetpts=PTS-STARTPTS,${audio},aresample=48000,aformat=channel_layouts=stereo[a${i}]`);
 });
 fs.writeFileSync(path.join(work,`${film.id}-loudness.json`),JSON.stringify(loudness,null,2)+'\n');
 const n=clips.length;
 filters.push(clips.map((_,i)=>`[v${i}][a${i}]`).join('')+`concat=n=${n}:v=1:a=1[body][sound]`);
 filters.push(`[sound]afade=t=out:st=${(FOOTAGE-0.35).toFixed(2)}:d=0.35,apad=whole_dur=${TOTAL}[a]`);
 filters.push(`[${n}:v]trim=duration=${CARD},setpts=PTS-STARTPTS,setsar=1[card]`);
 filters.push(`[body][card]concat=n=2:v=1:a=0,setpts=N/(${FPS}*TB)[v]`);
 const card=paperCard(film);
 const movie=path.join(dir,`${film.stem}.mp4`);
 const args=['-hide_banner','-loglevel','error','-y',...clips.flatMap(c=>['-i',c.file]),'-loop','1','-framerate',String(FPS),'-i',card,'-filter_complex',filters.join(';'),'-map','[v]','-map','[a]','-t',String(TOTAL),'-r',String(FPS),'-fps_mode','cfr','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',movie];
 let result=spawnSync(ffmpeg,args,{stdio:'inherit'});if(result.status)process.exit(result.status);
 result=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y','-ss',String(film.posterTime),'-i',movie,'-frames:v','1','-q:v','3',path.join(dir,`${film.stem}.jpg`)],{stdio:'inherit'});if(result.status)process.exit(result.status);
 for(const language of ['ko','en'])fs.writeFileSync(path.join(dir,`${film.stem}.${language}.vtt`),'WEBVTT\n\n'+film.cues.map((cue,i)=>`${i+1}\n${stamp(cue.start)} --> ${stamp(cue.end)}\n${cue[language]}\n`).join('\n'));
 console.log(`${film.id}: ${FOOTAGE}s of Flow footage + ${CARD}s paper card -> ${path.relative(root,movie)}`);
}
