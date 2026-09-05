// Original, editable 2D acting for the five research films. No external artwork.
module.exports=function({ctx,W,H,rounded,line,text,circle,eye,shadow,particle,smooth,clamp}){
 const ink='#223036',cream='#F7F4EB',mint='#7CBDAB',red='#EA826E';
 const mix=(a,b,t)=>a+(b-a)*clamp(t),ease=(a,b,t)=>mix(a,b,smooth(t));
 function stage(d){ctx.fillStyle=cream;ctx.fillRect(0,0,W,H);ctx.fillStyle=d.soft;ctx.beginPath();ctx.ellipse(1030,550,820,460,0,0,Math.PI*2);ctx.fill();line(100,848,1820,848,'#D1D5CB',3);text('PPEL+  /  MATERIAL MISCHIEF',90,85,25,ink,'left',true);text(d.index+'   ·   30 SEC',1830,85,25,ink,'right');text('FICTIONAL COMEDY · REAL RESEARCH',90,1020,19,'#6C7773');}
 function speech(s,x,y,w=420){rounded(x-w/2,y-63,w,90,35,'#fff',ink);ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(x-50,y+26);ctx.lineTo(x-70,y+62);ctx.lineTo(x-8,y+26);ctx.fill();line(x-50,y+26,x-70,y+62,ink,3);line(x-70,y+62,x-8,y+26,ink,3);text(s,x,y-7,32,ink,'center',true)}
 function blink(t){return Math.sin(t*1.9)>.995}
 function face(x,y,s,t,look=0,mood='happy'){ctx.save();ctx.translate(x,y);ctx.scale(s,s);if(blink(t)){line(-27,-4,-9,-4,ink,4);line(10,-4,28,-4,ink,4)}else{eye(-19,-6,7,look);eye(19,-6,7,look)}ctx.strokeStyle=ink;ctx.lineWidth=5;ctx.beginPath();if(mood==='shock'){ctx.ellipse(0,34,13,19,0,0,Math.PI*2);ctx.stroke()}else if(mood==='flat'){line(-12,28,12,28,ink,4)}else if(mood==='sad'){ctx.arc(0,43,16,Math.PI,Math.PI*2);ctx.stroke()}else{ctx.arc(0,17,18,.2,Math.PI-.2);ctx.stroke()}ctx.restore()}
 function mitt(x,y,rot=0,s=1){ctx.save();ctx.translate(x,y);ctx.rotate(rot);ctx.scale(s,s);rounded(-30,-20,60,48,20,'#fff',ink);circle(25,-18,13,'#fff',ink);ctx.restore()}
 function moustache(x,y,s=1){ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.fillStyle=ink;ctx.beginPath();ctx.moveTo(0,0);ctx.bezierCurveTo(-28,-38,-47,22,-74,-14);ctx.bezierCurveTo(-66,40,-22,42,0,18);ctx.bezierCurveTo(22,42,66,40,74,-14);ctx.bezierCurveTo(47,22,28,-38,0,0);ctx.fill();ctx.restore()}
 function glasses(x,y,s=1){ctx.save();ctx.translate(x,y);ctx.scale(s,s);rounded(-58,-18,48,33,11,ink);rounded(10,-18,48,33,11,ink);line(-10,-7,10,-7,ink,7);ctx.restore()}
 function oxygen(x,y,t,{disguise=false,squash=0,sad=false}={}){shadow(x+30,841,98,16);ctx.save();ctx.translate(x,y);ctx.scale(1+squash*.5,1-squash*.4);line(-35,90,-49+Math.sin(t*14)*16,133,ink,10);line(53,90,69-Math.sin(t*14)*16,133,ink,10);line(-75,22,-118,9+Math.sin(t*8)*12,ink,8);line(83,31,119,54,ink,8);circle(-34,12,65,red,ink);circle(48,12,65,red,ink);face(5,4,.85,t,0,sad?'sad':'happy');if(disguise){glasses(7,-3,.75);moustache(5,44,.73)}ctx.restore()}
 function club(d,t,phase){stage(d);for(let i=0;i<5;i++)rounded(220-i*8,252+i*19,425+i*16,565-i*17,19,i%2?'#425355':'#314247',ink);rounded(289,333,276,505,130,'#16262A');rounded(255,214,379,95,20,'#fff',ink);text('MXene CLUB',445,276,37,ink,'center',true);let bounce=phase==='setup'&&t>1.45&&t<2.3?Math.sin((t-1.45)*Math.PI/.85)*.6:0;
 const gb=phase==='punch'?Math.sin(t*4)*5:Math.sin(t*2)*3;shadow(818,836,130,22);line(765,735,738,827,ink,23);line(866,735,891,827,ink,23);rounded(690,410+gb,248,342,85,mint,ink);rounded(710,575+gb,208,127,24,'#E7F1E8');text('MnO₂',814,653+gb,47,ink,'center',true);face(814,498+gb,1.42,t,7,'flat');line(767,455,798,465,ink,9);line(831,465,861,455,ink,9);
 let x=phase==='setup'?t<1.6?ease(1610,1038,t/1.6):t<2.5?ease(1038,1360,(t-1.6)/.9):t<4.2?1360: ease(1360,1080,(t-4.2)/3):1270;
 let y=phase==='setup'?700-Math.abs(Math.sin(t*8))*11:726;
 let disguise=phase==='setup'?t>3.1: t<1.9;
 oxygen(x,y,t,{disguise,squash:bounce,sad:phase==='punch'&&t>2});
 line(934,576,1015,680,ink,20);mitt(1030,683,-.08,1.6);
 if(phase==='setup'&&t>2.6&&t<4.1){speech('NEW LOOK.',1400,352,330)}
 if(phase==='punch'){
   const lift=smooth((t-.9)/1.2);const mx=mix(1275,810,lift),my=700-Math.sin(lift*Math.PI)*255-lift*166;
   line(933,574,t>2.3?980:mx,t>2.3?560:my-35,ink,15);mitt(t>2.3?980:mx+7,t>2.3?555:my-40,0,.85);if(t>.9)moustache(mx,my,.95);
   if(t>3.5){speech('NICE TRY.',1410,405,360);circle(1485,795,51,'#EEC979',ink);for(let n=0;n<8;n++)circle(1452+(n%4)*21,766-Math.floor(n/4)*22,14,'#fff5d4',ink)}
 }
 }
 function sensor(x,y,t){rounded(x-195,y+53,390,24,10,'#9BABAC',ink);rounded(x-195,y+18,390,35,10,'#EBADC4',ink);for(let i=0;i<7;i++){ctx.fillStyle='#D380A1';ctx.beginPath();ctx.ellipse(x-148+i*47,y+32,19,9,.3,0,Math.PI*2);ctx.fill()}rounded(x-195,y,390,21,10,'#F5FAF5',ink)}
 function caretaker(d,t,phase){stage(d);let beat=phase==='punch'?Math.sin(t*11):t>4?Math.sin(t*8):0;let surprise=phase==='setup'?Math.sin(clamp((t-1.2)/1.2)*Math.PI):0;const cx=648,cy=560-surprise*75+beat*9;
 rounded(230,684,1440,68,24,'#506165',ink);line(350,752,320,927,'#506165',33);line(1550,752,1580,927,'#506165',33);shadow(cx,936,155,23);
 line(cx-69,cy+175,cx-106,913,ink,20);line(cx+76,cy+175,cx+107,913,ink,20);rounded(cx-151,cy-107,302,280,110,mint,ink);face(cx,cy-35,1.65,t,10,surprise>.5?'shock':'happy');
 ctx.strokeStyle='#5A7981';ctx.lineWidth=12;ctx.beginPath();ctx.arc(cx-38,cy-55,45,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.arc(cx+38,cy-55,45,0,Math.PI*2);ctx.stroke();line(cx-3,cy-57,cx+3,cy-57,'#5A7981',14);
 sensor(1055,638+Math.abs(beat)*5,t);line(1250,665,1402,665,'#C5688B',5);line(1402,665,1402,569,'#C5688B',5);rounded(1390,450,230,163,21,'#314C53',ink);rounded(1410,470,190,110,10,'#DBECD8');for(let i=0;i<90;i++){let xx=1425+i*1.72,yy=530-Math.exp(-Math.pow((i-40-beat*7)/7,2))*45;if(i)line(xx-1.72,530-Math.exp(-Math.pow((i-1-40-beat*7)/7,2))*45,xx,yy,'#59927B',3)}
 let handY=phase==='punch'?584+Math.sin(t*11)*42:t<1.3?620:t<3.7?mix(500,610,clamp((t-2)/1.5)):602+beat*26;
 line(cx+122,cy+20,975,handY,ink,20);mitt(985,handY,-.2,1.4);line(cx-120,cy+34,phase==='punch'?1117:cx-211,phase==='punch'?602-beat*35:cy+95,ink,19);mitt(phase==='punch'?1125:cx-211,phase==='punch'?598-beat*35:cy+95,.2,1.35);
 if(phase==='setup'){ctx.save();ctx.translate(phase==='setup'&&t<4?430:256,625);ctx.rotate(t<4?-.35:.13);line(0,-227,0,177,'#B58C53',17);rounded(-51,154,102,66,12,'#E3C478',ink);for(let i=0;i<8;i++)line(-40+i*12,180,-46+i*14,219,'#AD925F',4);ctx.restore();if(surprise>.1)speech('?!',928,338,160);if(t>4.5)speech('ONE MORE.',1020,317,360)}
 else {ctx.save();ctx.translate(292,825);ctx.rotate(ease(0,1.1,(t-5)/1.5));rounded(-81,-27,162,45,12,'#D8AC61',ink);line(0,-27,0,-223,'#BB995C',14);ctx.restore();if(t>1){for(let n=0;n<4;n++){let u=(t*.45+n*.23)%1;const nx=880+n*142,ny=425-u*220;text('♪',nx,ny,55+n*3,d.color,'center',true)}}if(t>5.5)speech('NEW CAREER.',615,294,400)}
 }
 function shoe(x,y,t,s=1,shocked=false){ctx.save();ctx.translate(x,y);ctx.scale(s,s);ctx.rotate(Math.sin(t*7)*.035);shadow(30,117,160,18);rounded(-140,-43,294,135,43,'#718CA6',ink);rounded(25,11,203,83,40,'#718CA6',ink);rounded(-153,80,390,40,18,'#fff',ink);for(let i=0;i<4;i++)line(-96+i*37,-5,-61+i*35,29,'#fff',9);face(123,22,.77,t,0,shocked?'shock':'happy');ctx.restore()}
 function paperScene(d,t,phase){stage(d);const px=620,py=717;shadow(px,874,322,24);ctx.save();ctx.translate(px,py);ctx.rotate(-.035);rounded(-303,-41,610,183,18,'#EEE5CC','#9D9886');for(let i=0;i<120;i++){let xx=(i*79)%545-274,yy=(i*57)%130-12;line(xx,yy,xx+18,yy+2,'#D1C7AC',1)}face(21,35,1.2,t,4,phase==='setup'&&t<1.9?'flat':'happy');ctx.restore();
 if(phase==='setup'){let x=t<2?ease(1170,626,t/2):t<3.2?626:ease(626,1160,(t-3.2)/1.4);let y=t<2?mix(509,576,t/2):t<3.2?576:600;shoe(x,y,t,.87,t>2);if(t>2.0&&t<3.6)speech('HELLO, DATA.',675,357,410);if(t>4.5){const length=ease(0,560,(t-4.5)/2.2);rounded(1010,709,length,104,20,'#fff',ink);for(let i=0;i<length/45;i++)line(1030+i*43,737,1030+i*43,782,d.color,4);circle(1020,762,53,'#fff',ink);circle(1020,762,21,'#E6E7DF',ink);text('?',1265,406,82,d.color,'center',true)}}
 else {let rise=smooth(t/4);shoe(1180,600-rise*110,t,.93,true);for(let i=0;i<6;i++){let start=i*.55,k=smooth((t-start)/1.5);if(k>0){rounded(904+i*23,803-i*47,525*k,70,27,'#fff',ink);for(let j=0;j<k*8;j++)line(960+j*45,829-i*47,960+j*45,848-i*47,d.color,3)}}if(t>3.7)speech('I WAS JUST WALKING.',985,315,570);}
 }
 function pencil(x,y,t,detective=false){ctx.save();ctx.translate(x,y);ctx.rotate(Math.sin(t*3)*.07);shadow(0,274,90,16);line(-40,193,-72,265,ink,10);line(40,193,73,265,ink,10);rounded(-56,-198,112,365,14,'#E7B950',ink);rounded(-56,-225,112,70,17,'#D9A0A4',ink);rounded(-56,-167,112,33,3,'#C8D2CC',ink);ctx.beginPath();ctx.moveTo(-56,165);ctx.lineTo(56,165);ctx.lineTo(0,239);ctx.closePath();ctx.fillStyle='#D4B38D';ctx.fill();ctx.strokeStyle=ink;ctx.lineWidth=4;ctx.stroke();ctx.beginPath();ctx.moveTo(-22,208);ctx.lineTo(22,208);ctx.lineTo(0,239);ctx.fillStyle=ink;ctx.fill();face(0,-48,1.05,t,5,detective?'happy':'flat');if(detective){rounded(-101,-248,202,35,15,'#7C705F',ink);rounded(-57,-302,114,82,23,'#9C8A6E',ink);rounded(-56,-258,112,20,3,ink)}ctx.restore()}
 function pencilScene(d,t,phase){stage(d);let detective=phase==='punch'||t>3.4;pencil(568,577,t,detective);rounded(780,749,678,87,16,'#fff',ink);for(let i=0;i<8;i++)line(825,770+i*6,1378-i*13,770+i*6,'#C7CCC4',1);if(phase==='setup'){
  if(t<3.5){line(625,532,825,725,ink,10);mitt(827,725,0,1.0);if(t>1)speech('PAPERWORK. AGAIN.',1115,308,540)}
  else{let lensX=ease(1360,1175,(t-3.5)/2.2);line(624,540,lensX-62,651,ink,11);line(lensX-46,597,lensX-115,716,'#806D53',22);circle(lensX,538,122,'#E0EEF0',ink);circle(lensX,538,100,'#F7FBF4');for(let i=0;i<9;i++){const yy=464+i*18,dx=Math.sin(i*.7+t*.2)*47;line(lensX-dx,yy,lensX+dx,yy,'#AECCC1',4);circle(lensX-dx,yy,7,i===4?'#D68CA1':mint);circle(lensX+dx,yy,7,'#789CB4')}if(t>5)speech('A CLUE!',1155,312,300)}
 }else{const u=smooth(t/3.3),lx=mix(1250,630,u),ly=mix(540,530,u);line(626,548,lx-20,ly+136,ink,13);line(lx-30,ly+88,lx-80,ly+174,'#806D53',18);circle(lx,ly,132,'#C7E4E0',ink);circle(lx,ly,110,'#F7FBF4');if(u>.7){face(lx,ly-14,2.1,t,0,'shock');if(t>4)speech('VERY SUSPICIOUS.',1150,345,510)}else{circle(lx,ly,28,mint);circle(lx+50,ly-28,15,'#D781A2')}}
 }
 function electron(x,y,t,color,mood='happy'){ctx.save();ctx.translate(x,y);shadow(0,61,53,10);circle(0,0,52,color,ink);face(0,-4,.65,t,5,mood);line(-20,47,-33+Math.sin(t*13)*10,70,ink,7);line(20,47,33-Math.sin(t*13)*10,70,ink,7);ctx.restore()}
 function trafficScene(d,t,phase){stage(d);rounded(250,700,1430,117,58,'#E0D6ED');line(294,757,1646,757,'#BAA8D0',6);for(let i=0;i<15;i++)line(310+i*89,793,354+i*89,793,'#fff',6);
 let open=phase==='punch'||t>4.7;rounded(1104,391,37,317,12,'#F1D590',ink);ctx.save();ctx.translate(1123,471);ctx.rotate(open?Math.PI*.48:0);rounded(-388,-22,409,44,13,'#E9B984',ink);for(let i=0;i<7;i++)line(-354+i*50,-17,-334+i*50,17,'#9269A5',12);ctx.restore();
 let clock=t,rate=open?235:17;for(let i=0;i<5;i++){let xx=phase==='setup'?t<4.7?960-i*139+t*3:((960-i*139+(t-4.7)*290-290)%1350)+290:((t*rate+i*223)%1350)+290;electron(xx,681-Math.abs(Math.sin(t*5+i))*10,t+i,d.color,!open?'flat':'happy')}
 rounded(1230,455,352,99,20,'#fff',ink);text(open?'LOW RESISTANCE':'HIGH RESISTANCE',1406,516,25,ink,'center',true);
 if(phase==='setup'&&t>1.5&&t<4.5)speech('STILL HERE?',687,373,400);
 if(phase==='punch'){ctx.save();ctx.translate(1140,283);ctx.rotate(t>4?Math.sin(t*9)*.09:0);rounded(-130,-62,260,110,18,'#fff',ink);text('MEMORY',0,-11,37,ink,'center',true);text('0  /  1',0,24,24,d.color,'center',true);ctx.restore();if(t>4.8)speech('THAT WAS QUICK.',602,362,510);}
 }
 return function(d,t,phase){({'energy-storage':club,'cherry-blossom':caretaker,'ai-paper':paperScene,biosensor:pencilScene,memory:trafficScene})[d.id](d,t,phase)};
};
