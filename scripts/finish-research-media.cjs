// Finish captions and mix original synthesized comic sound effects into the films.
const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const data=require('./research-video-data.json'),root=path.resolve(__dirname,'..'),work=path.join(root,'.video-work'),out=path.join(root,'Video','research');
const ffmpeg=process.env.FFMPEG_PATH||path.join(work,'tools','imageio_ffmpeg','binaries','ffmpeg-win-x86_64-v7.1.exe');
function stamp(t){return '00:'+String(Math.floor(t/60)).padStart(2,'0')+':'+(t%60).toFixed(3).padStart(6,'0')}
const sounds={
 'ai-paper':[[1.7,140,.2],[2.1,730,.4],[4.5,320,.2],[5,440,.2],[5.5,660,.2],[20.3,320,.2],[21,440,.2],[21.7,660,.2],[22.4,880,.2],[24.2,210,.5]],
 biosensor:[[.7,160,.1],[1.4,160,.1],[2.1,160,.1],[3.5,460,.24],[4.1,640,.25],[5.2,850,.3],[22.3,530,.2],[23.8,230,.45],[25.5,165,.5]],
 memory:[[1,175,.12],[2.5,175,.12],[4.7,560,.35],[5.4,900,.2],[6.2,1050,.2],[20.2,900,.2],[21.4,1100,.2],[22.6,1300,.2],[25,220,.4]],
 'energy-storage':[[1.6,120,.25],[3.2,430,.2],[4.6,750,.15],[6.4,140,.2],[21,430,.3],[22.3,660,.25],[24,195,.45],[26.3,280,.2]],
 'cherry-blossom':[[1.3,230,.13],[4.1,280,.13],[4.5,310,.13],...Array.from({length:28},(_,i)=>[20+i*.25,i%4===0?130:i%2?420:290,.12])]
};
function soundtrack(d,file){const sr=48000,n=sr*30,buf=Buffer.alloc(44+n*2),notes=[196,246.94,293.66,392,329.63,293.66,246.94,220],events=sounds[d.id];buf.write('RIFF');buf.writeUInt32LE(36+n*2,4);buf.write('WAVE',8);buf.write('fmt ',12);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(1,22);buf.writeUInt32LE(sr,24);buf.writeUInt32LE(sr*2,28);buf.writeUInt16LE(2,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(n*2,40);
 for(let i=0;i<n;i++){let t=i/sr,beat=t%.5,j=Math.floor(t/.5)%8,v=(Math.sin(2*Math.PI*notes[j]*t)+.24*Math.sin(4*Math.PI*notes[j]*t))*Math.exp(-beat*10)*.11;v+=Math.sin(2*Math.PI*65*t)*Math.exp(-(t%1)*35)*.09;for(const [start,hz,dur] of events){let dt=t-start;if(dt>=0&&dt<dur)v+=Math.sin(2*Math.PI*(hz*dt-70*dt*dt))*Math.exp(-dt*12)*.34}v*=Math.max(0,Math.min(1,t*10,(30-t)/1.7));buf.writeInt16LE(Math.round(Math.max(-.95,Math.min(.95,v))*32767),44+i*2)}fs.writeFileSync(file,buf)
}
for(const d of data){const movie=path.join(out,d.id+'.mp4');if(!fs.existsSync(movie))throw new Error('Render missing: '+d.id);
 const sound=path.join(work,'render',d.id,'sound.wav'),temp=path.join(work,'render',d.id,'finished.mp4');soundtrack(d,sound);
 const r=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y','-i',movie,'-i',sound,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-t','30','-movflags','+faststart',temp],{stdio:'inherit'});if(r.status)throw new Error('Audio mix failed');fs.copyFileSync(temp,movie);
 for(const [lang,col] of [['en',2],['ko',3]]){let vtt='WEBVTT\n\n';d.captions.forEach((c,i)=>vtt+=`${i+1}\n${stamp(c[0])} --> ${stamp(c[1])} position:50% align:center size:92%\n${c[col]}\n\n`);fs.writeFileSync(path.join(out,`${d.id}.${lang}.vtt`),vtt.trimEnd()+'\n')}
 console.log('Sound and captions finished: '+d.id);
}
