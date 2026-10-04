(async function(){
'use strict';
const B=window.FILM_BRIEF,c=document.getElementById('film'),ctx=c.getContext('2d',{alpha:false}),W=1920,H=1080;
const C={ink:'#12141B',blue:'#154CFF',muted:'#747D8D',line:'#DDE5F1',soft:'#F5F8FF',white:'#FFFFFF'};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),lerp=(a,b,t)=>a+(b-a)*t,smooth=x=>{x=clamp(x);return x*x*(3-2*x)},out=x=>1-Math.pow(1-clamp(x),3),ease=x=>{x=clamp(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2};
const assets={};for(let [id,path] of Object.entries({logo:'assets/brand/edge-lockup.svg',scout:'assets/brand/scout/scout-neutral.svg',search:'assets/brand/scout/scout-search.svg',found:'assets/brand/scout/scout-found.svg',celebrate:'assets/brand/scout/scout-celebrate.svg',word:'assets/brand/wordmark/edge-pixel-ink.svg'})){let img=new Image();img.src=path;await img.decode();assets[id]=img;}
await document.fonts.ready;
const orbit=window.makeOrbit();
function rr(x,y,w,h,r=16){ctx.beginPath();ctx.roundRect(x,y,w,h,r)}
function box(x,y,w,h,{fill=C.white,stroke=C.line,r=16,shadow=false}={}){ctx.save();if(shadow){ctx.shadowColor='#12141b08';ctx.shadowBlur=32;ctx.shadowOffsetY=15;}rr(x,y,w,h,r);ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.lineWidth=1.6;ctx.strokeStyle=stroke;ctx.stroke();}ctx.restore()}
function text(t,x,y,size=40,weight=500,color=C.ink,align='left',spacing=-1){ctx.fillStyle=color;ctx.font=`${weight} ${size}px Inter, Arial, sans-serif`;ctx.textAlign=align;ctx.textBaseline='top';ctx.letterSpacing=spacing+'px';ctx.fillText(t,x,y);ctx.letterSpacing='0px'}
function lines(ls,x,y,size=90,weight=600,color=C.ink,leading=1.075,align='left',spacing=-3){ls.forEach((t,i)=>text(t,x,y+i*size*leading,size,weight,color,align,spacing))}
function image(id,x,y,w,h){ctx.drawImage(assets[id],x,y,w,h)}
function logo(x=116,y=67,w=158){const im=assets.logo;ctx.drawImage(im,x,y,w,w*im.naturalHeight/im.naturalWidth)}
function line(x1,y1,x2,y2,color=C.line,width=2){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke()}
function pill(t,x,y,w=260,color=C.muted,bg=C.soft){box(x,y,w,42,{fill:bg,stroke:null,r:6});text(t,x+14,y+10,22,500,color,'left',0)}
function note(t){text(t,1804,1010,25,450,C.muted,'right',0)}
function small(t,x=116,y=220,color=C.blue){text(t,x,y,23,550,color,'left',2.2)}
function label(n,t){logo();text(n+' / '+t,1804,80,23,500,C.muted,'right',1.5)}
function safeText(t,x,y,size,w){while(size>20){ctx.font=`500 ${size}px Inter`;if(ctx.measureText(t).width<w)break;size-=1}text(t,x,y,size)}
function tinyClouds(time){ctx.fillStyle='#EAF2FF';const pat=[[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]];[[1510,170,15],[235,790,11],[1670,770,8]].forEach(([x,y,u],i)=>{ctx.globalAlpha=.4;pat.forEach((row,j)=>row.forEach((v,k)=>{if(v)ctx.fillRect(x+k*u+Math.sin(time*.12+i)*9,y+j*u,u,u)}));ctx.globalAlpha=1;});}
function skillIcon(x,y,size=68){box(x,y,size,size,{fill:'#EDF3FF',stroke:null,r:12});ctx.strokeStyle=C.blue;ctx.lineWidth=2.6;const cx=x+size/2,cy=y+size/2,r=size*.30;ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.ellipse(cx,cy,r*.48,r,0,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.ellipse(cx,cy,r,r*.39,0,0,Math.PI*2);ctx.stroke();}
function skillCard(x,y,w,h,alpha=1,compact=false){ctx.save();ctx.globalAlpha=alpha;box(x,y,w,h,{r:18,shadow:true});skillIcon(x+32,y+31,compact?60:72);text('SKILL',x+126,y+39,20,550,C.muted,'left',2);text('Published expertise',x+126,y+67,25,450,C.muted,'left',0);if(compact){text(B.skill,x+31,y+124,36,600,C.ink,'left',-1);text(B.creator,x+31,y+178,24,450,C.muted,'left',0)}else{lines(B.skillLines||[B.skill],x+36,y+152,72,550,C.ink,1.04);line(x+36,y+h-108,x+w-36,y+h-108);text('By '+B.creator,x+36,y+h-75,28,500,C.muted,'left',0);image('scout',x+w-92,y+h-90,52,52);}ctx.restore()}
function sourceCard(x,y,w,h,community=false,alpha=1){ctx.save();ctx.globalAlpha=alpha;box(x,y,w,h,{r:18,shadow:true});box(x+30,y+30,55,55,{fill:community?'#FFF1EB':C.ink,stroke:null,r:10});text(community?B.communityMark:B.sourceMark,x+57.5,y+41,community?25:31,600,community?'#CF4C18':C.white,'center',0);text(community?B.communityName:B.sourceAuthor,x+105,y+27,30,600,C.ink,'left',-.5);text(community?B.communityAuthor:B.sourceHandle,x+105,y+66,23,450,C.muted,'left',0);lines(community?B.communityQuote:B.sourceQuote,x+33,y+128,35,500,C.ink,1.24,'left',-.6);text(community?'Community discussion • title excerpt':B.sourceDate+' • source excerpt',x+33,y+h-43,21,450,C.muted,'left',0);ctx.restore()}
function shadow(x,y,w,h,alpha=.12){let g=ctx.createRadialGradient(x,y,3,x,y,w);g.addColorStop(0,`rgba(54,84,137,${alpha})`);g.addColorStop(.4,`rgba(100,127,180,${alpha*.5})`);g.addColorStop(1,'rgba(100,127,180,0)');ctx.save();ctx.translate(x,y);ctx.scale(1,h/w);ctx.fillStyle=g;ctx.translate(-x,-y);ctx.fillRect(x-w,y-w,w*2,w*2);ctx.restore()}
function artifact(t,p,rect={x:0,y:0,w:W,h:H},chapter=0){
ctx.save();rr(rect.x,rect.y,rect.w,rect.h,rect.x?18:0);ctx.clip();ctx.translate(rect.x,rect.y);ctx.scale(rect.w/W,rect.h/H);ctx.fillStyle='#F4F7FD';ctx.fillRect(0,0,W,H);
// Quiet architectural guides and editorial typography belong to this original output.
line(105,144,1815,144,'#DCE4F0',1.3);text('ORBIT',105,78,30,650,C.ink,'left',5);text('A SPATIAL MOTION STUDY',1815,84,20,450,'#5D6B80','right',3);
text('ORBIT',980,205,300,600,'#DDE5F2','center',-13);
for(let i=0;i<4;i++){ctx.beginPath();ctx.ellipse(1230,784,250+i*96,27+i*13,0,0,Math.PI*2);ctx.strokeStyle='#E3EAF5';ctx.lineWidth=1.2;ctx.stroke();}
shadow(1230,854,530,65,.1);
const surface=orbit.render(t,p);ctx.drawImage(surface,460,85,1480,833);
const words=[['A new','perspective.'],['Move through','the idea.'],['A world,','not a page.'],['Built to','be explored.']];
if(chapter>=0){small('EXPLORATION / 0'+(chapter+1),112,430,'#526581');lines(words[chapter],108,478,91,550,C.ink,1.05,'left',-4.5);text(['SPACE','MOVEMENT','CONNECTION','PERSPECTIVE'][chapter],113,755,23,500,'#77869D','left',4);}
if(chapter>=0){for(let i=0;i<4;i++){box(114+i*59,932,42,4,{fill:i===chapter?C.blue:'#CDD8E9',stroke:null,r:0});}
text('Scroll to explore',112,967,23,450,'#738099','left',0);text('Original motion demo',1810,981,24,450,'#738099','right',0);}
ctx.restore();}
function drawHook(t){artifact(t,.08,{x:0,y:0,w:W,h:H},-1);ctx.fillStyle='#F4F7FD';ctx.fillRect(80,412,703,508);small('IMAGINE YOUR NEXT TASK',113,431);lines(B.hook,110,489,85,600,C.ink,1.12,'left',-3.6);text('One idea. A different kind of output.',115,727,29,450,C.muted,'left',-.3);logo(112,923,158);note('Original motion demo');}
function drawSources(t){const local=t-3.75,a=out(local/.6);label('01','THE SOURCE');tinyClouds(t);ctx.save();ctx.globalAlpha=a;ctx.translate(0,35*(1-a));small('PUBLISHED EXPERTISE',116,289);lines(B.sources,111,347,89,550);text(B.sourcesLine,116,585,29,450,C.muted,'left',-.2);ctx.restore();sourceCard(1015+60*(1-a),177,755,370,false,a);sourceCard(1100+90*(1-a),590,670,330,true,a);note('Source excerpts • no ingestion event shown');}
function drawLibrary(t){const local=t-7.5,a=out(local/.64);label('02','THE LIBRARY');tinyClouds(t);small(B.brandName,116,293);lines(B.library,111,351,91,550);text('Expertise, ready for the next task.',116,595,29,450,C.muted,'left',-.2);
ctx.save();ctx.globalAlpha=.50*a;box(1080,144,690,134,{r:14});text(B.relatedSkills[0].name,1113,177,29,550);text(B.relatedSkills[0].creator,1113,220,21,450,C.muted,'left',0);box(1010,815,690,130,{r:14});text(B.relatedSkills[1].name,1043,847,29,550);text(B.relatedSkills[1].creator,1043,888,21,450,C.muted,'left',0);ctx.restore();
skillCard(964+80*(1-a),315,805,437,a);line(743,745,875,745,'#BCD0FD',2);image(local<1?'search':'found',811+Math.sin(local)*5,652,106,106);note('Workflow visualization');}
function drawHandoff(t){const local=t-11.25,a=out(local/.6);label('03','THE HANDOFF');small('FOR THE TASK IN FRONT OF YOU',116,291);lines(B.handoff,111,349,86,550);text('The same agent. The relevant expertise.',116,589,29,450,C.muted,'left',-.5);
box(980,229,790,597,{r:20,shadow:true});pill('Workflow visualization',1015,262,287,C.blue,'#EDF3FF');text('YOUR REQUEST',1015,342,21,550,C.muted,'left',2);lines(B.request,1015,387,35,500,C.ink,1.35,'left',-.5);
const enter=out((local-.6)/.75);ctx.save();ctx.globalAlpha=enter;ctx.translate(0,(1-enter)*80);box(1014,551,720,220,{r:12});skillIcon(1041,581,63);text(B.skill,1128,584,31,600,C.ink,'left',-1);text('By '+B.creator,1128,631,23,450,C.muted,'left',0);text(B.skillLine,1042,707,26,450,C.muted,'left',-.2);image('found',1650,684,53,53);ctx.restore();note('Illustrative request and handoff • not a live agent recording');}
function drawPayoff(t){const local=t-15,p=clamp(local/11.25),chapter=Math.min(2,Math.floor(local/3.75));artifact(local+4,p,{x:0,y:0,w:W,h:H},chapter+1);}
function drawEnd(t){let local=t-26.25,a=out(local/.7);tinyClouds(t);const im=assets.logo;ctx.save();ctx.globalAlpha=a;ctx.translate(0,25*(1-a));image('celebrate',757,217,110,110);image('word',897,242,265,265*7/23);lines(B.callback,W/2,403,97,550,C.ink,1.10,'center',-4);text(B.destination,935,695,42,550,C.blue,'center',-.7);text('↗',1080,693,39,450,C.blue,'center',0);ctx.restore();text(B.tagline,W/2,868,28,450,C.muted,'center',-.4);note('First cut • original demo + workflow visualization');}
window.frameKey=t=>t>=4.6&&t<7.5?'source-hold':t>=8.7&&t<11.25?'library-hold':t>=12.8&&t<15?'handoff-hold':t>=27.2?'end-hold':null;
window.renderAt=function(t){t=clamp(t,0,29.9999);ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;ctx.fillStyle=C.white;ctx.fillRect(0,0,W,H);if(t<3.75)drawHook(t);else if(t<7.5)drawSources(t);else if(t<11.25)drawLibrary(t);else if(t<15)drawHandoff(t);else if(t<26.25)drawPayoff(t);else drawEnd(t);};
window.renderArtifact=(t,p)=>{ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=1;artifact(t,p,{x:0,y:0,w:W,h:H},Math.min(3,Math.floor(p*4)))};window.__ready=true;window.renderAt(0);
if(new URLSearchParams(location.search).has('capture'))document.body.classList.add('capture');
let playing=false,start=0,offset=0,raf;const play=document.getElementById('play'),seek=document.getElementById('seek'),music=document.getElementById('music'),time=document.getElementById('time');
function tick(now){if(!playing)return;let t=(now-start)/1000+offset;if(t>=30){playing=false;music.pause();play.textContent='Replay';offset=0;return}window.renderAt(t);seek.value=t;time.textContent='0:'+String(Math.floor(t)).padStart(2,'0')+' / 0:30';raf=requestAnimationFrame(tick)}
play.onclick=async()=>{if(playing){playing=false;offset=Number(seek.value);music.pause();play.textContent='Play';cancelAnimationFrame(raf)}else{playing=true;music.currentTime=offset;await music.play().catch(()=>{});start=performance.now();play.textContent='Pause';raf=requestAnimationFrame(tick)}};
seek.oninput=()=>{offset=Number(seek.value);start=performance.now();music.currentTime=offset;window.renderAt(offset);time.textContent='0:'+String(Math.floor(offset)).padStart(2,'0')+' / 0:30'};
})();
