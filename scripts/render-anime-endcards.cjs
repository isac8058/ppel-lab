// Exact, editable paper cards for the final two seconds of the v2 films.
// These are end cards, not replacement animation footage.
const fs=require('node:fs'),path=require('node:path');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const papers=require('./research-video-data.json');
const out=path.resolve(__dirname,'../Video/research/v2');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arial.ttf','Arial');
GlobalFonts.registerFromPath('C:/Windows/Fonts/arialbd.ttf','Arial Bold');
fs.mkdirSync(out,{recursive:true});
for(const paper of papers){
 const canvas=createCanvas(1920,1080),ctx=canvas.getContext('2d');
 ctx.fillStyle='#151b25';ctx.fillRect(0,0,1920,1080);
 ctx.fillStyle='#e6c8ae';ctx.fillRect(110,128,64,4);
 ctx.font='28px Arial';ctx.fillText(paper.id==='memory'?'THE REAL REVIEW':'THE REAL RESEARCH',110,206);
 ctx.font='54px Arial Bold';ctx.fillStyle='#f7f1e8';
 const words=paper.paperTitle.split(' '),lines=[];let line='';
 for(const word of words){const next=line?`${line} ${word}`:word;if(ctx.measureText(next).width>1660&&line){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);
 lines.forEach((line,index)=>{
  let x=110;const y=340+index*74;
  for(const run of line.split(/(₂)/)){
   ctx.font=run==='₂'?'38px Arial Bold':'54px Arial Bold';
   const text=run==='₂'?'2':run;ctx.fillText(text,x,y+(run==='₂'?10:0));x+=ctx.measureText(text).width;
  }
 });
 ctx.fillStyle='#c0a99b';ctx.font='34px Arial';ctx.fillText(paper.journal,110,802);
 ctx.fillStyle='#f7f1e8';ctx.font='32px Arial';ctx.fillText(`doi.org/${paper.doi}`,110,868);
 ctx.fillStyle='#e6c8ae';ctx.font='bold 37px Arial Bold';ctx.fillText('PPEL+',110,970);
 ctx.font='24px Arial';ctx.textAlign='right';ctx.fillText('FICTIONAL STORY / REAL PAPER',1810,970);
 fs.writeFileSync(path.join(out,`${paper.id}-endcard.png`),canvas.toBuffer('image/png'));
}
console.log('Five v2 paper end cards exported.');
