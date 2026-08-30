#!/usr/bin/env python3
"""Generate 200 self-contained playable HTML5 games + SVG thumbnails + catalog entries.
Mirrors the existing BlazerGames structure: games/<slug>/index.html, images/<slug>.svg,
and an <a href><img></a> row inside #games in index.html.
Uses placeholder substitution (no f-strings) to avoid brace-escaping issues in JS.
"""
import os, re, html, random

random.seed(2026)
ROOT = os.path.dirname(os.path.abspath(__file__))

# ---- color schemes (bg, panel, accent, text) ----
SCHEMES = [
    ("#1a1a2e", "#16213e", "#e94560", "#f5f5f5"),
    ("#0f3460", "#164d80", "#f5a623", "#ffffff"),
    ("#2d0a31", "#3d0e44", "#e0aaff", "#f8f8f8"),
    ("#0b3d2e", "#0f5132", "#39ff14", "#eaffea"),
    ("#3a0ca3", "#4361ee", "#4cc9f0", "#ffffff"),
    ("#5a189a", "#7b2cbf", "#ff9e00", "#ffffff"),
    ("#6a040f", "#9d0208", "#ffba08", "#fff5f5"),
    ("#003049", "#0353a4", "#fb8500", "#ffffff"),
    ("#240046", "#3c096c", "#ff6d00", "#ffffff"),
    ("#1d3557", "#457b9d", "#e63946", "#f1faee"),
    ("#231942", "#5f4bb6", "#ff7b00", "#ffffff"),
    ("#03071e", "#370617", "#dc2f02", "#ffffff"),
]
DARK_SCHEMES = SCHEMES[10:]  # for horror titles

def esc(s):
    return html.escape(s, quote=True)

def fill(tpl, title, c):
    bg, panel, accent, text = c
    return (tpl.replace("«T»", esc(title))
              .replace("«BG»", bg).replace("«PANEL»", panel)
              .replace("«ACCENT»", accent).replace("«TEXT»", text))

WRAP = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>«T»</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;overflow:hidden;background:«BG»;color:«TEXT»;font-family:'Segoe UI',system-ui,sans-serif}
#wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;padding:8px}
h1{font-size:5vw;margin-bottom:6px;color:«ACCENT»;text-align:center}
#score{font-size:4vw;margin-bottom:6px;color:«TEXT»}
canvas{background:«PANEL»;border:3px solid «ACCENT»;border-radius:8px;touch-action:none;max-width:96vw;max-height:70vh}
#msg{font-size:5vw;color:«ACCENT»;text-align:center;min-height:1em}
button{margin-top:8px;padding:10px 22px;font-size:4vw;background:«ACCENT»;color:«BG»;border:none;border-radius:8px;cursor:pointer}
</style>
</head>
<body>
<div id="wrap">
<h1>«T»</h1>
«BODY»
<script>
«SCRIPT»
</script>
</div>
</body>
</html>
"""

def page(title, c, body, script):
    return fill(WRAP, title, c).replace("«BODY»", body).replace("«SCRIPT»", script)

# ============ GAME TEMPLATES ============
SNAKE = """let cv=document.querySelector('canvas'),x=cv.getContext('2d'),G=20,N=cv.width=cv.height=400;
let snake=[{x:10,y:10}],dir={x:1,y:0},food={x:5,y:5},sc=0,over=false,timer=null;
function rnd(){food={x:Math.floor(Math.random()*G),y:Math.floor(Math.random()*G)}}
function step(){if(over)return;let h={x:snake[0].x+dir.x,y:snake[0].y+dir.y};
if(h.x<0||h.y<0||h.x>=G||h.y>=G||snake.some(s=>s.x==h.x&&s.y==h.y)){over=true;document.getElementById('msg').textContent='Game Over! Score '+sc;return;}
snake.unshift(h);if(h.x==food.x&&h.y==food.y){sc++;document.getElementById('score').textContent='Score: '+sc;rnd()}else snake.pop();draw();}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,400,400);x.fillStyle='«ACCENT»';x.fillRect(food.x*N,food.y*N,N-1,N-1);x.fillStyle='«TEXT»';snake.forEach(s=>x.fillRect(s.x*N,s.y*N,N-1,N-1));}
function turn(dx,dy){if(dx==-dir.x&&dy==-dir.y)return;dir={x:dx,y:dy}}
addEventListener('keydown',e=>{if(e.key=='ArrowUp')turn(0,-1);if(e.key=='ArrowDown')turn(0,1);if(e.key=='ArrowLeft')turn(-1,0);if(e.key=='ArrowRight')turn(1,0)});
cv.addEventListener('touchstart',e=>{let t=e.touches[0],dx=t.clientX-cv.width/2,dy=t.clientY-cv.height/2;if(Math.abs(dx)>Math.abs(dy))turn(dx>0?1:-1,0);else turn(0,dy>0?1:-1)},{passive:true});
function start(){snake=[{x:10,y:10}];dir={x:1,y:0};sc=0;over=false;document.getElementById('score').textContent='Score: 0';document.getElementById('msg').textContent='';rnd();clearInterval(timer);timer=setInterval(step,110)}
document.querySelector('button').onclick=start;start();"""

BREAKOUT = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=360;cv.height=440;
let px=150,pw=80,b={x:180,y:300,dx:3,dy:-3},bricks=[],sc=0,over=false,lives=3;
for(let r=0;r<5;r++)for(let cI=0;cI<8;cI++)bricks.push({x:cI*45+5,y:r*22+30,a:1});
function move(){if(over)return;b.x+=b.dx;b.y+=b.dy;if(b.x<8||b.x>cv.width-8)b.dx*=-1;if(b.y<8)b.dy*=-1;
if(b.y>cv.height){lives--;if(lives<=0){over=true;document.getElementById('msg').textContent='Game Over! Score '+sc;return}b={x:180,y:300,dx:3,dy:-3}}
if(b.y>cv.height-20&&b.x>px&&b.x<px+pw)b.dy=-Math.abs(b.dy);
bricks.forEach(bk=>{if(bk.a&&b.x>bk.x&&b.x<bk.x+40&&b.y>bk.y&&b.y<bk.y+18){bk.a=0;sc++;document.getElementById('score').textContent='Score: '+sc;b.dy*=-1}});draw();}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='«ACCENT»';x.fillRect(px,cv.height-15,pw,10);x.beginPath();x.arc(b.x,b.y,7,0,7);x.fill();x.fillStyle='«TEXT»';bricks.forEach(bk=>{if(bk.a)x.fillRect(bk.x,bk.y,40,16)})}
function mv(p){px=Math.max(0,Math.min(cv.width-pw,p-cv.getBoundingClientRect().left-pw/2))}
addEventListener('mousemove',e=>mv(e.clientX));addEventListener('touchmove',e=>mv(e.touches[0].clientX),{passive:true});
addEventListener('keydown',e=>{if(e.key=='ArrowLeft')px-=20;if(e.key=='ArrowRight')px+=20});
setInterval(move,16);"""

MEMORY = """let syms=['A','B','C','D','E','F','G','H'];
let cards=[...syms,...syms].sort(()=>Math.random()-.5),flipped=[],matched=[],lock=false,sc=0;
let grid=document.getElementById('grid');grid.innerHTML='';
cards.forEach((v,i)=>{let d=document.createElement('div');d.className='c';d.dataset.v=v;d.textContent='?';d.onclick=()=>flip(d);grid.appendChild(d)});
function flip(d){if(lock||flipped.includes(d)||matched.includes(d))return;d.textContent=d.dataset.v;d.style.background='«ACCENT»';flipped.push(d);
if(flipped.length==2){lock=true;if(flipped[0].dataset.v==flipped[1].dataset.v){matched.push(...flipped);sc++;document.getElementById('score').textContent='Pairs: '+sc+' / 8';flipped=[];lock=false;if(matched.length==16)document.getElementById('msg').textContent='You Win!'}else{setTimeout(()=>{flipped.forEach(f=>{f.textContent='?';f.style.background='«PANEL»'});flipped=[];lock=false},700)}}}}"""

TICTACTOE = """let board=Array(9).fill(''),human='X',ai='O',over=false;
let g=document.getElementById('grid');g.innerHTML='';
for(let i=0;i<9;i++){let d=document.createElement('div');d.className='c';d.dataset.i=i;d.onclick=()=>play(d);g.appendChild(d)}
function play(d){if(over||board[d.dataset.i])return;board[d.dataset.i]=human;d.textContent=human;d.style.color='«ACCENT»';if(check(human))return end('You Win!');
let m=board.findIndex(v=>!v);if(m<0)return end('Draw!');board[m]=ai;let cell=g.children[m];cell.textContent=ai;cell.style.color='«TEXT»';if(check(ai))return end('AI Wins!');if(!board.includes(''))end('Draw!')}
function check(p){let w=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];return w.some(l=>l.every(i=>board[i]==p))}
function end(m){over=true;document.getElementById('msg').textContent=m}
function reset(){board=Array(9).fill('');over=false;document.getElementById('msg').textContent='';[...g.children].forEach(c=>c.textContent='')}
document.querySelector('button').onclick=reset;"""

FLAPPY = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=320;cv.height=420;
let by=200,vy=0,pipes=[],sc=0,over=false,tmr=null;
function tap(){if(over)return;vy=-7}
addEventListener('keydown',e=>{if(e.code=='Space')tap()});cv.addEventListener('touchstart',tap,{passive:true});cv.addEventListener('mousedown',tap);
function loop(){if(over)return;vy+=0.4;by+=vy;if(by>cv.height||by<0)return lose();
if(pipes.length==0||pipes[pipes.length-1].x<cv.width-160)pipes.push({x:cv.width,y:Math.random()*200+60});
pipes.forEach(p=>{p.x-=2.5;if(p.x==80){sc++;document.getElementById('score').textContent='Score: '+sc}if(80>p.x&&80<p.x+50&&(by<p.y||by>p.y+120))return lose()});pipes=pipes.filter(p=>p.x>-60);draw()}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='«ACCENT»';pipes.forEach(p=>{x.fillRect(p.x,0,50,p.y);x.fillRect(p.x,p.y+120,50,cv.height)});x.fillStyle='«TEXT»';x.beginPath();x.arc(80,by,12,0,7);x.fill()}
function lose(){over=true;document.getElementById('msg').textContent='Game Over! Score '+sc}
function start(){by=200;vy=0;pipes=[];sc=0;over=false;document.getElementById('score').textContent='Score: 0';document.getElementById('msg').textContent='';clearInterval(tmr);tmr=setInterval(loop,22)}
document.querySelector('button').onclick=start;start();"""

PONG = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=360;cv.height=300;
let py=120,ay=120,b={x:180,y:150,dx:3,dy:2},sc=0,as=0,over=false;
function loop(){if(over)return;b.x+=b.dx;b.y+=b.dy;if(b.y<6||b.y>cv.height-6)b.dy*=-1;
if(b.x<24&&b.y>py&&b.y<py+70)b.dx=Math.abs(b.dx);if(b.x>cv.width-24&&b.y>ay&&b.y<ay+70)b.dx=-Math.abs(b.dx);
if(b.x<0){as++;reset(-1)}if(b.x>cv.width){sc++;reset(1)}ay+=(b.y-ay-35)*0.06;if(sc==7||as==7){over=true;document.getElementById('msg').textContent=(sc==7?'You Win!':'AI Wins!')}draw()}
function reset(d){b={x:180,y:150,dx:3*d,dy:2};document.getElementById('score').textContent='You '+sc+' - '+as+' AI'}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='«ACCENT»';x.fillRect(10,py,10,70);x.fillRect(cv.width-20,ay,10,70);x.fillStyle='«TEXT»';x.fillRect(b.x-5,b.y-5,10,10)}
function mv(p){py=Math.max(0,Math.min(cv.height-70,p-cv.getBoundingClientRect().top-35))}
addEventListener('mousemove',e=>mv(e.clientY));addEventListener('touchmove',e=>mv(e.touches[0].clientY),{passive:true});
addEventListener('keydown',e=>{if(e.key=='ArrowUp')py-=20;if(e.key=='ArrowDown')py+=20});
setInterval(loop,16);"""

WHACK = """let sc=0,tmr=null,time=30,active=-1,over=false;let holes=document.getElementById('holes');
holes.innerHTML='';for(let i=0;i<9;i++){let d=document.createElement('div');d.className='h';d.dataset.i=i;d.onclick=()=>hit(i);holes.appendChild(d)}
function hit(i){if(over)return;if(i==active){sc++;document.getElementById('score').textContent='Score: '+sc;active=-1}}
function pop(){if(over)return;active=Math.floor(Math.random()*9);[...holes.children].forEach((h,k)=>h.classList.toggle('up',k==active));setTimeout(()=>{if(active!=-1){active=-1;[...holes.children].forEach(h=>h.classList.remove('up'))}},700)}
function tick(){time--;document.getElementById('time').textContent='Time: '+time;if(time<=0){over=true;document.getElementById('msg').textContent='Time! Score '+sc;clearInterval(tmr);clearInterval(pp)}}
let pp;function start(){sc=0;time=30;over=false;document.getElementById('score').textContent='Score: 0';document.getElementById('time').textContent='Time: 30';document.getElementById('msg').textContent='';clearInterval(tmr);clearInterval(pp);tmr=setInterval(tick,1000);pp=setInterval(pop,800)}
document.querySelector('button').onclick=start;start();"""

REACTION = """let state='wait',startT=0,tmr=null;let box=document.getElementById('box');
box.onclick=function(){if(state=='wait'){state='ready';box.textContent='Wait...';box.style.background='«PANEL»';tmr=setTimeout(function(){state='go';box.textContent='CLICK!';box.style.background='«ACCENT»';startT=Date.now()},1000+Math.random()*2500)}
else if(state=='ready'){state='wait';box.textContent='Too Soon! Click to try again';box.style.background='«TEXT»'}
else if(state=='go'){let ms=Date.now()-startT;state='wait';box.textContent=ms+'ms! Click again';box.style.background='«PANEL»'}}};
box.textContent='Click to Start';"""

SLIDING = """let n=3,tiles=[];let grid=document.getElementById('grid');
function init(){tiles=[...Array(n*n-1).keys(),-1].sort(()=>Math.random()-.5);render()}
function render(){grid.innerHTML='';tiles.forEach((v,i)=>{let d=document.createElement('div');d.className='c';if(v==-1)d.classList.add('e');else d.textContent=v+1;d.onclick=()=>move(i);grid.appendChild(d)})}
function move(i){let e=tiles.indexOf(-1),r=Math.floor(i/n),c=i%n,re=Math.floor(e/n),ce=e%n;
if((r==re&&Math.abs(c-ce)==1)||(c==ce&&Math.abs(r-re)==1)){[tiles[i],tiles[e]]=[tiles[e],tiles[i]];render();if(won())document.getElementById('msg').textContent='Solved!'}}
function won(){for(let i=0;i<tiles.length-1;i++)if(tiles[i]!=i)return false;return true}
document.querySelector('button').onclick=init;init();"""

CLICKER = """let sc=0,per=1,auto=0;let btn=document.getElementById('c'),st=document.getElementById('s');
btn.onclick=function(){sc+=per;st.textContent=sc};
function buy(p,cst){if(sc>=cst){sc-=cst;if(p=='per')per++;else auto++;st.textContent=sc}}
document.getElementById('b1').onclick=function(){buy('per',10*per)};
document.getElementById('b2').onclick=function(){buy('auto',25*(auto+1))};
setInterval(function(){sc+=auto;st.textContent=sc},1000);"""

DODGE = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=320;cv.height=400;
let px=140,blocks=[],sc=0,over=false,tmr=null;
addEventListener('keydown',e=>{if(e.key=='ArrowLeft')px-=20;if(e.key=='ArrowRight')px+=20});
cv.addEventListener('touchmove',e=>{px=Math.max(0,Math.min(cv.width-30,e.touches[0].clientX-cv.getBoundingClientRect().left-15))},{passive:true});
function loop(){if(over)return;if(Math.random()<.08)blocks.push({x:Math.random()*290,y:0});blocks.forEach(b=>b.y+=4);
if(blocks.some(b=>b.x>px-5&&b.x<px+35&&b.y>cv.height-40&&b.y<cv.height-10))return lose();
blocks=blocks.filter(b=>b.y<cv.height);sc++;document.getElementById('score').textContent='Score: '+sc;draw()}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='«ACCENT»';blocks.forEach(b=>x.fillRect(b.x,b.y,30,20));x.fillStyle='«TEXT»';x.fillRect(px,cv.height-30,30,30)}
function lose(){over=true;document.getElementById('msg').textContent='Game Over! Score '+sc}
function start(){px=140;blocks=[];sc=0;over=false;document.getElementById('score').textContent='Score: 0';document.getElementById('msg').textContent='';clearInterval(tmr);tmr=setInterval(loop,30)}
document.querySelector('button').onclick=start;start();"""

SHOOTER = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=320;cv.height=400;
let px=145,enemies=[],bullets=[],sc=0,over=false,tmr=null;
addEventListener('keydown',e=>{if(e.key=='ArrowLeft')px-=15;if(e.key=='ArrowRight')px+=15;if(e.key==' ')bullets.push({x:px+15,y:cv.height-30})});
cv.addEventListener('touchstart',e=>{bullets.push({x:px+15,y:cv.height-30});px=Math.max(0,Math.min(cv.width-30,e.touches[0].clientX-cv.getBoundingClientRect().left-15))},{passive:true});
function loop(){if(over)return;if(Math.random()<.05)enemies.push({x:Math.random()*290,y:0});enemies.forEach(e=>e.y+=2.5);bullets.forEach(b=>b.y-=6);
bullets.forEach(b=>{enemies=enemies.filter(e=>!(Math.abs(e.x-b.x)<30&&Math.abs(e.y-b.y)<20))});enemies=enemies.filter(e=>e.y<cv.height);
if(enemies.some(e=>e.y>cv.height-40))return lose();draw()}
function draw(){x.fillStyle='«PANEL»';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='«ACCENT»';enemies.forEach(e=>x.fillRect(e.x,e.y,30,20));x.fillStyle='«TEXT»';bullets.forEach(b=>x.fillRect(b.x,b.y,4,10));x.fillRect(px,cv.height-30,30,30)}
function lose(){over=true;document.getElementById('msg').textContent='Game Over! Score '+sc}
setInterval(function(){sc++;document.getElementById('score').textContent='Score: '+sc},1000);
function start(){px=145;enemies=[];bullets=[];sc=0;over=false;document.getElementById('score').textContent='Score: 0';document.getElementById('msg').textContent='';clearInterval(tmr);tmr=setInterval(loop,30)}
document.querySelector('button').onclick=start;start();"""

HORRORMAZE = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=360;cv.height=360;
let G=12,S=cv.width/G,maze=[],px=0.5,py=0.5,mx=11.5,my=11.5,sc=0,over=false,tmr=null;
function gen(){maze=[];for(let r=0;r<G;r++){maze[r]=[];for(let cI=0;cI<G;cI++)maze[r][cI]=1}carve(1,1)}
function carve(r,cI){maze[r][cI]=0;let d=[[0,2],[2,0],[0,-2],[-2,0]].sort(()=>Math.random()-.5);d.forEach(dr=>{let nr=r+dr[0],nc=cI+dr[1];if(nr>0&&nr<G&&nc>0&&nc<G&&maze[nr][nc]==1){maze[r+dr[0]/2][cI+dr[1]/2]=0;carve(nr,nc)}})}
addEventListener('keydown',e=>{let nx=px,ny=py;if(e.key=='ArrowUp')ny-=.5;if(e.key=='ArrowDown')ny+=.5;if(e.key=='ArrowLeft')nx-=.5;if(e.key=='ArrowRight')nx+=.5;if(maze[Math.floor(ny)]&&maze[Math.floor(ny)][Math.floor(nx)]==0){px=nx;py=ny}});
function loop(){if(over)return;let dx=px-mx,dy=py-my,d=Math.hypot(dx,dy)||1;mx+=dx/d*0.02;my+=dy/d*0.02;
if(Math.abs(px-mx)<.4&&Math.abs(py-my)<.4)return caught();
if(Math.floor(px)==G-2&&Math.floor(py)==G-2){sc++;document.getElementById('score').textContent='Escapes: '+sc;gen();px=0.5;py=0.5;mx=11.5;my=11.5}draw()}
function draw(){x.fillStyle='#000';x.fillRect(0,0,cv.width,cv.height);x.fillStyle='#1a1a1a';for(let r=0;r<G;r++)for(let cI=0;cI<G;cI++)if(maze[r][cI]==1)x.fillRect(cI*S,r*S,S,S);x.fillStyle='«ACCENT»';x.beginPath();x.arc(px*S,py*S,8,0,7);x.fill();x.fillStyle='#dc143c';x.beginPath();x.arc(mx*S,my*S,8,0,7);x.fill()}
function caught(){over=true;document.getElementById('msg').textContent='CAUGHT! Escapes: '+sc}
function start(){gen();px=0.5;py=0.5;mx=11.5;my=11.5;sc=0;over=false;document.getElementById('score').textContent='Escapes: 0';document.getElementById('msg').textContent='';clearInterval(tmr);tmr=setInterval(loop,40)}
document.querySelector('button').onclick=start;start();"""

HORRORFLASH = """let cv=document.querySelector('canvas'),x=cv.getContext('2d');cv.width=360;cv.height=360;
let bat=100,ghosts=[],sc=0,over=false,tmr=null,mx=180,my=180;
cv.addEventListener('mousemove',e=>{let r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top});
cv.addEventListener('touchmove',e=>{let r=cv.getBoundingClientRect();mx=e.touches[0].clientX-r.left;my=e.touches[0].clientY-r.top},{passive:true});
function loop(){if(over)return;bat-=0.15;if(bat<0)bat=0;if(Math.random()<.04)ghosts.push({x:Math.random()*340,y:Math.random()*340,h:30});
ghosts.forEach(g=>{let gx=g.x-mx,gy=g.y-my,d=Math.hypot(gx,gy)||1;g.x-=gx/d*1.2;g.y-=gy/d*1.2});sc++;document.getElementById('score').textContent='Survived: '+sc;draw()}
function draw(){x.fillStyle='#000';x.fillRect(0,0,cv.width,cv.height);if(bat>0){let g=x.createRadialGradient(mx,my,10,mx,my,120);g.addColorStop(0,'rgba(255,255,220,'+(bat/100)+')');g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(0,0,cv.width,cv.height)}x.fillStyle='rgba(200,200,220,0.85)';ghosts.forEach(g=>{x.beginPath();x.arc(g.x,g.y,12,0,7);x.fill()})}
function lose(){over=true;document.getElementById('msg').textContent='A ghost got you! Survived '+sc}
setInterval(function(){if(ghosts.some(g=>Math.hypot(g.x-mx,g.y-my)<14))lose()},100);
cv.addEventListener('click',function(){bat=Math.min(100,bat+25)});
function start(){bat=100;ghosts=[];sc=0;over=false;document.getElementById('score').textContent='Survived: 0';document.getElementById('msg').textContent='';clearInterval(tmr);tmr=setInterval(loop,40)}
document.querySelector('button').onclick=start;start();"""

JUMPSCARE = """let sc=0,eyes=true,blink=0,over=false;let face=document.getElementById('face');
function loop(){if(over)return;blink++;if(blink>60+Math.random()*120){eyes=false;blink=0;setTimeout(function(){if(!over){eyes=true;sc++;document.getElementById('score').textContent='Survived: '+sc}},300)}face.textContent=eyes?'\\u{1F440}':'- -'}
function check(){if(!eyes&&!over){over=true;document.getElementById('msg').textContent='JUMPSCARE! Survived '+sc;face.textContent='\\u{1F631}'}}
face.onclick=check;let tmr=setInterval(loop,200);
function start(){sc=0;eyes=true;blink=0;over=false;document.getElementById('score').textContent='Survived: 0';document.getElementById('msg').textContent='';face.textContent='\\u{1F440}';clearInterval(tmr);tmr=setInterval(loop,200)}
document.querySelector('button').onclick=start;start();"""

TEMPLATES = {
 'snake':SNAKE,'breakout':BREAKOUT,'memory':MEMORY,'tictactoe':TICTACTOE,'flappy':FLAPPY,
 'pong':PONG,'whack':WHACK,'reaction':REACTION,'sliding':SLIDING,'clicker':CLICKER,
 'dodge':DODGE,'shooter':SHOOTER,'horrormaze':HORRORMAZE,'horrorflash':HORRORFLASH,'jumpscare':JUMPSCARE,
}

# body markup per template
BODY = {
 'snake':'<div id="score">Score: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'breakout':'<div id="score">Score: 0</div><canvas></canvas><div id="msg"></div>',
 'memory':'<div id="score">Pairs: 0 / 8</div><div id="grid" style="display:grid;grid-template-columns:repeat(4,70px);gap:8px"></div><div id="msg"></div><style>#grid .c{width:70px;height:70px;display:flex;align-items:center;justify-content:center;font-size:34px;background:«PANEL»;border:2px solid «ACCENT»;border-radius:8px;cursor:pointer;color:«TEXT»;user-select:none}</style>',
 'tictactoe':'<div id="grid" style="display:grid;grid-template-columns:repeat(3,80px);gap:6px"></div><div id="msg" style="font-size:5vw;color:«ACCENT»;min-height:1em"></div><button>Reset</button><style>#grid .c{width:80px;height:80px;display:flex;align-items:center;justify-content:center;font-size:42px;background:«PANEL»;border:2px solid «ACCENT»;border-radius:8px;cursor:pointer;font-weight:bold;color:«TEXT»}</style>',
 'flappy':'<div id="score">Score: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'pong':'<div id="score">You 0 - 0 AI</div><canvas></canvas><div id="msg"></div>',
 'whack':'<div><span id="score">Score: 0</span> | <span id="time">Time: 30</span></div><div id="holes" style="display:grid;grid-template-columns:repeat(3,80px);gap:10px;margin:10px"></div><div id="msg"></div><button>Start</button><style>.h{width:80px;height:80px;border-radius:50%;background:«PANEL»;border:3px solid «ACCENT»;position:relative;overflow:hidden;cursor:pointer}.h.up::after{content:"";position:absolute;bottom:0;left:10%;width:60%;height:70%;background:«TEXT»;border-radius:50% 50% 0 0}</style>',
 'reaction':'<div id="box" style="width:260px;height:260px;display:flex;align-items:center;justify-content:center;font-size:22px;text-align:center;background:«PANEL»;border:3px solid «ACCENT»;border-radius:14px;cursor:pointer;color:«TEXT»;user-select:none"></div><div id="msg"></div>',
 'sliding':'<div id="grid" style="display:grid;grid-template-columns:repeat(3,70px);gap:4px"></div><div id="msg" style="color:«ACCENT»;font-size:5vw"></div><button>Shuffle</button><style>.c{width:70px;height:70px;display:flex;align-items:center;justify-content:center;font-size:30px;background:«PANEL»;border:2px solid «ACCENT»;border-radius:6px;cursor:pointer;color:«TEXT»}.c.e{visibility:hidden}</style>',
 'clicker':'<div>Score: <span id="s">0</span></div><button id="c" style="width:140px;height:140px;border-radius:50%;font-size:24px;background:«ACCENT»;color:«BG»;border:none;cursor:pointer;margin:12px">CLICK</button><div style="display:flex;gap:8px"><button id="b1" style="background:«PANEL»;color:«TEXT»;border:2px solid «ACCENT»;padding:8px">+1/click (10)</button><button id="b2" style="background:«PANEL»;color:«TEXT»;border:2px solid «ACCENT»;padding:8px">Auto +1/s (25)</button></div>',
 'dodge':'<div id="score">Score: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'shooter':'<div id="score">Score: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'horrormaze':'<div id="score">Escapes: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'horrorflash':'<div id="score">Survived: 0</div><canvas></canvas><div id="msg"></div><button>Restart</button>',
 'jumpscare':'<div id="score">Survived: 0</div><div id="face" style="font-size:90px;cursor:pointer;user-select:none">\\u{1F440}</div><div id="msg" style="color:«ACCENT»;font-size:5vw">Don\'t click while it blinks!</div><button>Restart</button>',
}

# icon path per template (drawn in thumbnail SVG)
ICONS = {
 'snake':'M20,55 Q35,55 35,40 T50,40 T65,40 T80,55','breakout':'M30,30 h40 v12 h-40z M48,48 v14',
 'memory':'M30,30 h18 v18 h-18z M54,30 h18 v18 h-18z M30,54 h18 v18 h-18z M54,54 h18 v18 h-18z',
 'tictactoe':'M40,30 v40 M60,30 v40 M30,40 h40 M30,60 h40','flappy':'M50,40 a10,10 0 1 0 0.1,0 M50,50 l20,0',
 'pong':'M20,35 v30 M80,35 v30 M50,50 h0','whack':'M35,35 a15,15 0 1 0 0.1,0 M65,40 l10,-10',
 'reaction':'M50,50 m-22,0 a22,22 0 1 0 44,0 a22,22 0 1 0 -44,0','sliding':'M30,30 h16 v16 h-16z M52,30 h16 v16 h-16z M30,52 h16 v16 h-16z',
 'clicker':'M50,50 m-20,0 a20,20 0 1 0 40,0 a20,20 0 1 0 -40,0','dodge':'M30,30 h10 v10 h-10z M55,55 h10 v10 h-10z M45,75 h10',
 'shooter':'M40,60 l20,-10 M50,40 a8,8 0 1 0 0.1,0','horrormaze':'M30,30 h40 v40 h-40z M45,45 l10,10 M55,45 l-10,10',
 'horrorflash':'M35,40 a6,6 0 1 0 0.1,0 M65,40 a6,6 0 1 0 0.1,0 M50,60 l-8,12 h16z','jumpscare':'M35,40 a7,7 0 1 0 0.1,0 M65,40 a7,7 0 1 0 0.1,0 M40,62 q10,8 20,0',
}

def thumb(title, c, tmpl):
    icon = ICONS.get(tmpl,'M50,50 m-15,0 a15,15 0 1 0 30,0 a15,15 0 1 0 -30,0')
    safe = esc(title)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 100 100">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[0]}"/></linearGradient></defs>'
            f'<rect width="100" height="100" rx="14" fill="url(#g)"/>'
            f'<path d="{icon}" stroke="{c[2]}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text x="50" y="92" font-family="Segoe UI,Arial,sans-serif" font-size="11" font-weight="bold" fill="{c[3]}" text-anchor="middle">{safe[:18]}</text>'
            '</svg>')

# ============ GAME LIST (200) ============
RAW = [
 # Horror (40)
 ("Backrooms Escape","horrormaze"),("Haunted Hallway","horrormaze"),("Nightmare Maze","horrormaze"),
 ("Graveyard Shift","horrormaze"),("The Asylum","horrormaze"),("Dark Corners","horrormaze"),
 ("Cursed Catacombs","horrormaze"),("Shadow Labyrinth","horrormaze"),("Phantom Pursuit","horrormaze"),
 ("Dread Dungeon","horrormaze"),("Maze of the Damned","horrormaze"),("Hellfire Halls","horrormaze"),
 ("Flashlight Fright","horrorflash"),("Midnight Manor","horrorflash"),("Ghost Hunter","horrorflash"),
 ("Lantern of Fear","horrorflash"),("Spectral Survivors","horrorflash"),("The Hollow","horrorflash"),
 ("Don't Blink","jumpscare"),("Stare Down","jumpscare"),("Eyes in the Dark","jumpscare"),
 ("The Watcher","jumpscare"),("Creepy Gaze","jumpscare"),("Blink and Die","jumpscare"),
 ("Zombie Outbreak","shooter"),("Undead Siege","shooter"),("Monster Mash","shooter"),
 ("Slender Woods","horrormaze"),("Cabin Fever","horrorflash"),("Scream Street","jumpscare"),
 ("Possessed","jumpscare"),("The Ritual","horrormaze"),("Blood Moon","horrorflash"),
 ("Cursed Doll","jumpscare"),("Haunted Hospital","horrormaze"),("Terror Tower","horrormaze"),
 ("Fog of Fear","horrorflash"),("The Whispering","jumpscare"),("Night Terrors","horrorflash"),
 ("Doomsday Dungeon","horrormaze"),
 # Action / Arcade (40)
 ("Neon Runner","dodge"),("Rush Hour","dodge"),("Falling Sky","dodge"),("Asteroid Storm","dodge"),
 ("Lava Leap","flappy"),("Sky Hopper","flappy"),("Cloud Jumper","flappy"),("Pipe Dreamer","flappy"),
 ("Galaxy Blaster","shooter"),("Star Defender","shooter"),("Comet Strike","shooter"),("Void Raider","shooter"),
 ("Pixel Pong","pong"),("Retro Rally","pong"),("Ball Brawl","pong"),("Net Smash","pong"),
 ("Brick Buster","breakout"),("Wall Smasher","breakout"),("Block Break","breakout"),("Stone Cracker","breakout"),
 ("Snake Classic","snake"),("Pixel Serpent","snake"),("Cobra Craze","snake"),("Slither Snake","snake"),
 # Puzzle (40)
 ("Brain Twist","sliding"),("Tile Shuffle","sliding"),("Slide It","sliding"),("Order Up","sliding"),
 ("Memory Lane","memory"),("Match Mania","memory"),("Pair Up","memory"),("Recall","memory"),
 ("Logic Grid","tictactoe"),("Cross Battle","tictactoe"),("Noughts","tictactoe"),("Triple Threat","tictactoe"),
 ("Tap Master","reaction"),("Quick Reflex","reaction"),("Speed Test","reaction"),("Insta Click","reaction"),
 ("Cookie Craze","clicker"),("Idle Empire","clicker"),("Tap Tycoon","clicker"),("Click Quest","clicker"),
 ("Mole Mash","whack"),("Bonk Bonk","whack"),("Garden Pests","whack"),("Hammer Time","whack"),
 # Sports / Racing (40)
 ("Turbo Drift","dodge"),("Speed Demon","dodge"),("Highway Hero","dodge"),("Road Rage","dodge"),
 ("Goal Master","tictactoe"),("Penalty Shoot","reaction"),("Free Kick","reaction"),("Slam Dunk","reaction"),
 ("Racing Rivals","pong"),("Drift King","dodge"),("Nitro Rush","dodge"),("Burnout","dodge"),
 # More variety (40)
 ("Cosmic Snake","snake"),("Rainbow Serpent","snake"),("Mini Munch","snake"),("Snake Quest","snake"),
 ("Bubble Pop","breakout"),("Orbit Breaker","breakout"),("Sphere Smash","breakout"),("Crack It","breakout"),
 ("Flap Attack","flappy"),("Wing It","flappy"),("Hover Bird","flappy"),("Jet Pack","flappy"),
 ("Alien Invasion","shooter"),("Space Patrol","shooter"),("Laser Wars","shooter"),("Blast Off","shooter"),
 ("Mind Match","memory"),("Twin Cards","memory"),("Find Twins","memory"),("Spot It","memory"),
 ("Puzzle Box","sliding"),("Number Slide","sliding"),("Fifteen","sliding"),("Shift Puzzle","sliding"),
 ("Click Frenzy","clicker"),("Mega Clicker","clicker"),("Tap Tap Tap","clicker"),("Coin Clicker","clicker"),
 ("Whack Fest","whack"),("Mole Madness","whack"),("Smash Mole","whack"),("Bop It","whack"),
 ("Reflex Rush","reaction"),("Lightning Tap","reaction"),("Fast Finger","reaction"),("Snap Decision","reaction"),
 ("Grid Wars","tictactoe"),("Tic Tac Clash","tictactoe"),("X and O","tictactoe"),("Line Three","tictactoe"),
 # Extra horror (20)
 ("Creepy Cabin","horrormaze"),("The Cellar","horrormaze"),("Witching Hour","horrorflash"),("Dead of Night","horrorflash"),
 ("Soul Eater","jumpscare"),("The Staring","jumpscare"),("Cursed Mirror","jumpscare"),("Blackout","horrorflash"),
 ("Dungeon of Doom","horrormaze"),("Forsaken","horrormaze"),("Howling Halls","horrormaze"),("Poltergeist","jumpscare"),
 ("Restless Dead","shooter"),("Grave Robber","horrormaze"),("The Undertaker","horrormaze"),("Shadows Bite","horrorflash"),
 ("Panic Room","jumpscare"),("Last Breath","horrorflash"),("Tomb Raider","horrormaze"),("Evil Eye","jumpscare"),
 # Extra arcade/puzzle (40)
 ("Hyper Snake","snake"),("Mega Serpent","snake"),("Turbo Snake","snake"),("Neon Serpent","snake"),
 ("Power Breaker","breakout"),("Mega Bricks","breakout"),("Hyper Break","breakout"),("Color Cracker","breakout"),
 ("Flappy Birdie","flappy"),("Sky Dash","flappy"),("Hover Hop","flappy"),("Float Flyer","flappy"),
 ("Plasma Pong","pong"),("Ultra Pong","pong"),("Pong Wars","pong"),("Double Pong","pong"),
 ("Mole Bop","whack"),("Whack Attack","whack"),("Gopher Game","whack"),("Critter Catch","whack"),
 ("Brain Box","sliding"),("Slide Master","sliding"),("Puzzle Slide","sliding"),("Tile Master","sliding"),
 ("Match Three","memory"),("Memory Test","memory"),("Twin Hunt","memory"),("Recall Rush","memory"),
 ("Click Storm","clicker"),("Power Clicker","clicker"),("Idle Clicker","clicker"),("Mega Tap","clicker"),
 ("Reflex King","reaction"),("Quick Tap","reaction"),("Speed Click","reaction"),("Reaction Rush","reaction"),
 ("Galaxy Snake","snake"),("Brick Storm","breakout"),("Sky Flapper","flappy"),("Pong Classic","pong"),
]

def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def main():
    existing = set(os.listdir(os.path.join(ROOT, 'games')))
    created = 0
    entries = []
    used = set()
    for i, (title, tmpl) in enumerate(RAW):
        slug = slugify(title)
        while slug in existing or slug in used:
            slug = slug + "-x"
        used.add(slug)
        c = SCHEMES[i % len(SCHEMES)]
        if tmpl.startswith('horror') or tmpl == 'jumpscare':
            c = DARK_SCHEMES[i % len(DARK_SCHEMES)]
        gdir = os.path.join(ROOT, 'games', slug)
        os.makedirs(gdir, exist_ok=True)
        body = fill(BODY[tmpl], title, c)
        script = fill(TEMPLATES[tmpl], title, c)
        with open(os.path.join(gdir, 'index.html'), 'w') as f:
            f.write(page(title, c, body, script))
        with open(os.path.join(ROOT, 'images', slug + '.svg'), 'w') as f:
            f.write(thumb(title, c, tmpl))
        entries.append(f'        <a href="games/{slug}/"><img src="images/{slug}.svg" alt="{esc(title)}"></a>')
        created += 1
    idx = os.path.join(ROOT, 'index.html')
    with open(idx) as f:
        txt = f.read()
    block = "\n".join(entries) + "\n"
    new = txt.replace("    </div>\n    </div>\n</body>", block + "    </div>\n    </div>\n</body>", 1)
    with open(idx, 'w') as f:
        f.write(new)
    print(f"Created {created} games")

if __name__ == '__main__':
    main()
