#!/usr/bin/env python3
"""Assembles googlebot-world.html by inlining Three.js and the scene code."""
import os

THREE_JS_PATH = '/home/user/web5-10/node_modules/three/build/three.min.js'

with open(THREE_JS_PATH, 'r') as f:
    three_js = f.read()

HTML_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Googlebot World Explorer</title>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;overflow:hidden;background:#0a0a1a;font-family:Arial,sans-serif}
canvas{display:block}
#hud{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10}
#district-badge{
  position:absolute;top:20px;left:20px;
  background:rgba(0,0,0,.65);color:#fff;
  padding:8px 16px;border-radius:20px;font-size:15px;font-weight:700;
  border-left:4px solid #4285F4;backdrop-filter:blur(4px);
  transition:border-color .4s
}
#index-counter{
  position:absolute;top:20px;right:20px;
  background:rgba(0,0,0,.65);color:#fff;
  padding:10px 18px;border-radius:12px;font-size:13px;text-align:center;
  backdrop-filter:blur(4px)
}
#index-counter .num{font-size:30px;font-weight:700;color:#4285F4;line-height:1.1}
#controls-hint{
  position:absolute;bottom:18px;left:50%;transform:translateX(-50%);
  background:rgba(0,0,0,.5);color:rgba(255,255,255,.75);
  padding:7px 18px;border-radius:20px;font-size:13px;
  backdrop-filter:blur(4px);white-space:nowrap
}
#nearby-ind{
  position:absolute;bottom:58px;left:50%;transform:translateX(-50%);
  background:rgba(66,133,244,.88);color:#fff;
  padding:8px 20px;border-radius:20px;font-size:14px;font-weight:700;
  display:none;animation:pulse 1s infinite alternate;white-space:nowrap
}
@keyframes pulse{from{box-shadow:0 0 8px rgba(66,133,244,.5)}to{box-shadow:0 0 22px #4285F4}}
#toast{
  position:absolute;top:80px;left:50%;transform:translateX(-50%);
  background:rgba(52,168,83,.92);color:#fff;
  padding:10px 22px;border-radius:10px;font-size:14px;font-weight:700;
  display:none
}
#results-panel{
  position:absolute;right:20px;top:90px;width:270px;max-height:65vh;
  background:rgba(8,8,28,.92);color:#fff;border-radius:12px;
  padding:14px;border:1px solid rgba(66,133,244,.35);
  backdrop-filter:blur(8px);display:none;overflow-y:auto
}
#results-panel h3{margin:0 0 10px;color:#4285F4;font-size:13px;border-bottom:1px solid rgba(66,133,244,.3);padding-bottom:7px}
.ri{padding:7px;margin-bottom:5px;background:rgba(255,255,255,.05);border-radius:6px;font-size:11px;border-left:3px solid #34A853}
.ri .ru{color:#34A853;font-weight:700;font-size:12px}
.ri .rs{color:rgba(255,255,255,.55);margin-top:2px}
#minimap{
  position:absolute;bottom:18px;right:18px;width:140px;height:140px;
  background:rgba(0,0,0,.7);border-radius:8px;border:1px solid rgba(255,255,255,.2)
}
#minimap canvas{display:block;border-radius:8px}
#glogo{
  position:absolute;top:22px;left:50%;transform:translateX(-50%);
  font-size:20px;font-weight:700;letter-spacing:-1px;pointer-events:none;white-space:nowrap
}
.gb{color:#4285F4}.gr{color:#DB4437}.gy{color:#F4B400}.gg{color:#0F9D58}
#err{
  display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  background:rgba(200,0,0,.92);color:#fff;padding:20px;border-radius:8px;
  z-index:9999;font-family:monospace;max-width:80vw;word-break:break-all
}
</style>
</head>
<body>
<div id="canvas-container"></div>
<div id="hud">
  <div id="glogo">
    <span class="gb">G</span><span class="gr">o</span><span class="gy">o</span><span class="gb">g</span><span class="gg">l</span><span class="gr">e</span>
    <span style="color:#aaa;font-size:11px;margin-left:6px">World Explorer</span>
  </div>
  <div id="district-badge">Central Plaza</div>
  <div id="index-counter"><div class="num" id="icount">0</div><div>sites indexed</div></div>
  <div id="nearby-ind">Press <b>E</b> to index &nbsp;<span id="nearby-url"></span></div>
  <div id="toast" id="toast"></div>
  <div id="results-panel"><h3>&#128269; Search Index</h3><div id="rlist"></div></div>
  <div id="minimap"><canvas id="mm" width="140" height="140"></canvas></div>
  <div id="controls-hint">WASD / Arrow Keys &nbsp;&#8226;&nbsp; E = Index Site &nbsp;&#8226;&nbsp; R = Toggle Results</div>
</div>
<div id="err"></div>
'''

MAIN_JS = r'''
window.onerror = function(msg,src,line,col,err){
  var d=document.getElementById('err');
  if(d){d.style.display='block';d.textContent='ERROR: '+msg+' (line '+line+') src:'+src;}
  return false;
};

if(typeof THREE==='undefined'){throw new Error('three.js did not load');}

// =====================================================================
//  GLOBALS
// =====================================================================
var WORLD=180, MOVE_SPD=0.18, ROT_SPD=0.035;
var keys={};
var robotAngle=Math.PI;   // start facing south (toward camera)
var robotVel=0;
var time=0;
var indexedUrls=[];
var colliders=[];    // [{x,z,r}]
var buildings=[];
var npcs=[];
var npcData=[];
var particles=[];
var nearbyBuilding=null;
var showResults=false;
var roadPaths=[];    // arrays of {x,z} points for particle travel

// =====================================================================
//  RENDERER / SCENE / CAMERA
// =====================================================================
var renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
document.getElementById('canvas-container').appendChild(renderer.domElement);

var scene=new THREE.Scene();
scene.background=new THREE.Color(0x87CEEB);
scene.fog=new THREE.FogExp2(0x87CEEB,0.009);

var camera=new THREE.PerspectiveCamera(60,window.innerWidth/window.innerHeight,0.1,600);
camera.position.set(0,10,18);

// =====================================================================
//  LIGHTING
// =====================================================================
scene.add(new THREE.AmbientLight(0xffffff,0.45));

var sun=new THREE.DirectionalLight(0xfff9e8,1.1);
sun.position.set(60,90,40);
sun.castShadow=true;
sun.shadow.mapSize.width=2048;
sun.shadow.mapSize.height=2048;
sun.shadow.camera.near=1;
sun.shadow.camera.far=400;
sun.shadow.camera.left=-170;
sun.shadow.camera.right=170;
sun.shadow.camera.top=170;
sun.shadow.camera.bottom=-170;
scene.add(sun);

scene.add(new THREE.DirectionalLight(0x4499ff,0.25));

var hemi=new THREE.HemisphereLight(0x87CEEB,0x4a7c59,0.35);
scene.add(hemi);

// =====================================================================
//  MATERIAL FACTORY
// =====================================================================
function makeMat(hex,metal,rough,emHex,emInt,transp,opac){
  var m=new THREE.MeshStandardMaterial();
  m.color.setHex(hex);
  m.metalness =metal !==undefined?metal :0;
  m.roughness =rough !==undefined?rough :1;
  if(emHex  !==undefined){m.emissive.setHex(emHex);}
  if(emInt  !==undefined){m.emissiveIntensity=emInt;}
  if(transp !==undefined){m.transparent=transp;}
  if(opac   !==undefined){m.opacity=opac;}
  return m;
}

// =====================================================================
//  GEOMETRY HELPERS
// =====================================================================
function mkBox(w,h,d,mat){
  var m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);
  m.castShadow=true;m.receiveShadow=true;return m;
}
function mkSph(r,mat,s){
  s=s||16;
  var m=new THREE.Mesh(new THREE.SphereGeometry(r,s,s),mat);
  m.castShadow=true;m.receiveShadow=true;return m;
}
function mkCyl(rt,rb,h,mat,s){
  s=s||12;
  var m=new THREE.Mesh(new THREE.CylinderGeometry(rt,rb,h,s),mat);
  m.castShadow=true;m.receiveShadow=true;return m;
}
function mkCone(r,h,mat,s){
  s=s||8;
  var m=new THREE.Mesh(new THREE.ConeGeometry(r,h,s),mat);
  m.castShadow=true;return m;
}

// =====================================================================
//  CANVAS SIGN TEXTURE
// =====================================================================
function makeSign(text,bg,fg,w,h){
  bg=bg||'#0d1b2a';fg=fg||'#00e676';w=w||256;h=h||56;
  var c=document.createElement('canvas');c.width=w;c.height=h;
  var cx=c.getContext('2d');
  cx.fillStyle=bg;cx.fillRect(0,0,w,h);
  cx.strokeStyle=fg;cx.lineWidth=2;cx.strokeRect(2,2,w-4,h-4);
  cx.fillStyle=fg;cx.font='bold '+(h*0.35|0)+'px monospace';
  cx.textAlign='center';cx.textBaseline='middle';
  cx.fillText(text,w/2,h/2);
  var t=new THREE.CanvasTexture(c);return t;
}

// =====================================================================
//  GROUND
// =====================================================================
var groundMat=makeMat(0x4a7c59,0,0.95);
var groundMesh=new THREE.Mesh(new THREE.PlaneGeometry(400,400),groundMat);
groundMesh.rotation.x=-Math.PI/2;groundMesh.receiveShadow=true;
scene.add(groundMesh);

// =====================================================================
//  DISTRICT ZONES  (flat tinted overlays slightly above ground)
// =====================================================================
var DISTRICTS=[
  {name:'Library',     color:0x66BB6A, bdrColor:'#66BB6A', cx:-62,cz:-62,w:62,h:62},
  {name:'Market',      color:0xFFD54F, bdrColor:'#FFD54F', cx: 62,cz:-62,w:62,h:62},
  {name:'Tech Hub',    color:0x42A5F5, bdrColor:'#42A5F5', cx:-62,cz: 62,w:62,h:62},
  {name:'News',        color:0xEF5350, bdrColor:'#EF5350', cx: 62,cz: 62,w:62,h:62},
  {name:'Social Park', color:0xCE93D8, bdrColor:'#CE93D8', cx:  0,cz:-30,w:44,h:32},
  {name:'Central Plaza',color:0xFFFFFF,bdrColor:'#FFFFFF', cx:  0,cz:  5,w:38,h:38},
];

for(var di=0;di<DISTRICTS.length;di++){
  var dd=DISTRICTS[di];
  var dzMat=makeMat(dd.color,0,1,undefined,undefined,true,0.32);
  var dz=new THREE.Mesh(new THREE.PlaneGeometry(dd.w,dd.h),dzMat);
  dz.rotation.x=-Math.PI/2;dz.position.set(dd.cx,0.01,dd.cz);
  scene.add(dz);
}

// =====================================================================
//  ROADS
// =====================================================================
var roadMat=makeMat(0x444444,0,0.95);
var lineMat=makeMat(0xffff88,0,0.9);

function makeRoad(px,pz,rw,rl,horiz){
  var rg=new THREE.PlaneGeometry(horiz?rl:rw, horiz?rw:rl);
  var rm=new THREE.Mesh(rg,roadMat);
  rm.rotation.x=-Math.PI/2;rm.position.set(px,0.02,pz);
  rm.receiveShadow=true;scene.add(rm);
  // center dashes
  var steps=horiz?(rl/6|0):(rl/6|0);
  for(var si=0;si<steps;si++){
    var dashG=new THREE.PlaneGeometry(horiz?2.5:0.15,horiz?0.15:2.5);
    var dash=new THREE.Mesh(dashG,lineMat);
    dash.rotation.x=-Math.PI/2;
    var off=(si-(steps-1)/2)*6;
    dash.position.set(horiz?px+off:px, 0.03, horiz?pz:pz+off);
    scene.add(dash);
  }
}

// Main arteries
makeRoad( 0, 0,8,320,false);  // N-S
makeRoad( 0, 0,8,320,true);   // E-W
// District connectors
makeRoad(-62,-30,6,70,false);
makeRoad( 62,-30,6,70,false);
makeRoad(-62, 30,6,65,false);
makeRoad( 62, 30,6,65,false);
makeRoad(  0,-62,6,128,true);
makeRoad(  0, 62,6,128,true);
makeRoad(-62,  0,6,128,false);
makeRoad( 62,  0,6,128,false);

// Road paths for data particles
roadPaths=[
  [{x:-160,z:0},{x:160,z:0}],                            // E-W main
  [{x:0,z:-160},{x:0,z:160}],                            // N-S main
  [{x:-62,z:-62},{x:-62,z:0},{x:0,z:0}],                 // Library to center
  [{x:62,z:-62},{x:62,z:0},{x:0,z:0}],                   // Market to center
  [{x:-62,z:62},{x:-62,z:0},{x:0,z:0}],                  // Tech to center
  [{x:62,z:62},{x:62,z:0},{x:0,z:0}],                    // News to center
  [{x:0,z:-30},{x:0,z:0}],                               // Social to center
];

// =====================================================================
//  STREET LAMPS
// =====================================================================
function makeLamp(px,pz){
  var g=new THREE.Group();
  var pole=mkCyl(0.12,0.12,4.5,makeMat(0x555555,0.7,0.4),6);
  pole.position.y=2.25;g.add(pole);
  var arm=mkCyl(0.07,0.07,1.2,makeMat(0x555555,0.7,0.4),6);
  arm.rotation.z=Math.PI/2;arm.position.set(0.6,4.5,0);g.add(arm);
  var bulb=mkSph(0.18,makeMat(0xffffaa,0,0.1,0xffffaa,2.0),8);
  bulb.position.set(1.2,4.5,0);g.add(bulb);
  var pl=new THREE.PointLight(0xffe8a0,0.6,12);
  pl.position.set(1.2,4.4,0);g.add(pl);
  g.position.set(px,0,pz);
  scene.add(g);
}
// Lamps along main road intersections
var lampSpacing=18;
for(var li=-8;li<=8;li++){
  if(li===0)continue;
  makeLamp( 5,li*lampSpacing);
  makeLamp(-5,li*lampSpacing);
  makeLamp(li*lampSpacing, 5);
  makeLamp(li*lampSpacing,-5);
}

// =====================================================================
//  TREES
// =====================================================================
function makeTree(px,pz,scale){
  scale=scale||1;
  var g=new THREE.Group();
  var trunk=mkCyl(0.2*scale,0.25*scale,1.5*scale,makeMat(0x6B4226,0,0.9),6);
  trunk.position.y=0.75*scale;g.add(trunk);
  var foliage=mkCone(1.2*scale,2.5*scale,makeMat(0x2d5a1b,0,0.85),7);
  foliage.position.y=2.5*scale;g.add(foliage);
  var foliage2=mkCone(0.9*scale,2*scale,makeMat(0x2d6b20,0,0.85),7);
  foliage2.position.y=3.5*scale;g.add(foliage2);
  g.position.set(px,0,pz);
  scene.add(g);
}
// Scatter trees across districts
var treePos=[
  [-78,-48],[-68,-52],[-52,-78],[-80,-72],[-45,-62],
  [ 78,-48],[ 68,-52],[ 52,-78],[ 80,-72],[ 45,-62],
  [-78, 48],[-68, 52],[-52, 78],[-80, 72],[-45, 62],
  [ 78, 48],[ 68, 52],[ 52, 78],[ 80, 72],[ 45, 62],
  [-15,-50],[ 15,-50],[-15,-25],[ 15,-25],
  [-18, 18],[ 18, 18],[-18, 20],[ 18, 20],
  [-100,10],[100,10],[-100,-10],[100,-10],
];
for(var ti=0;ti<treePos.length;ti++){
  makeTree(treePos[ti][0],treePos[ti][1],0.8+Math.random()*0.5);
}

// =====================================================================
//  BUILDING FACTORY
// =====================================================================
var snippets={
  'wikipedia.org':'The free encyclopedia — 60M+ articles',
  'britannica.com':'Encyclopaedia Britannica online',
  'gutenberg.org':'Free ebooks — classic literature',
  'archive.org':'Internet Archive — Wayback Machine',
  'khanacademy.org':'Free world-class education',
  'amazon.com':'World largest online marketplace',
  'ebay.com':'Buy and sell electronics, collectibles',
  'etsy.com':'Handmade & vintage marketplace',
  'shopify.com':'Build your online store',
  'craigslist.org':'Local classifieds & community',
  'github.com':'Where the world builds software',
  'stackoverflow.com':'Where developers learn & share',
  'mozilla.org':'Building a better Internet',
  'npmjs.com':'The world JavaScript package registry',
  'w3.org':'World Wide Web standards',
  'cnn.com':'Breaking news, latest headlines',
  'bbc.com':'BBC — trusted news worldwide',
  'nytimes.com':'All the news that fits to print',
  'reddit.com':'The front page of the internet',
  'digg.com':'404 — site not found',
  'twitter.com':'What is happening right now',
  'facebook.com':'Connect with friends and family',
  'instagram.com':'Photo & video sharing app',
  'tiktok.com':'Short-form video entertainment',
  'google.com':'Search the world information',
  'maps.google.com':'Explore maps & get directions',
  'gmail.com':'Google email service',
  'geocities.com':'404 — Geocities shut down 2009',
  'myspace.com':'404 — Legacy social network',
};

function createBuilding(type,px,pz,floors,url,dc){
  floors=floors||3;
  var g=new THREE.Group();
  var signBg='#0d1b2a', signFg='#00e676';

  if(type==='office'){
    var bw=5+Math.floor(Math.random()*3),bd=5+Math.floor(Math.random()*3);
    var bh=floors*2.8;
    var body=mkBox(bw,bh,bd,makeMat(dc||0x607D8B,0.45,0.35));
    body.position.y=bh/2;g.add(body);
    // Windows grid
    for(var wf=0;wf<Math.min(floors,6);wf++){
      for(var wc=0;wc<3;wc++){
        var win=mkBox(0.7,0.9,0.06,makeMat(0xaaddff,0.1,0.1,0xaaddff,0.4));
        win.position.set((wc-1)*1.5, wf*2.8+1.2, bd/2+0.04);g.add(win);
      }
    }
    // Sign
    var sg=new THREE.PlaneGeometry(bw*0.85,0.9);
    var sm=new THREE.MeshBasicMaterial({map:makeSign(url,signBg,signFg),transparent:true});
    var sv=new THREE.Mesh(sg,sm);
    sv.position.set(0,bh+0.55,bd/2+0.08);g.add(sv);
    colliders.push({x:px,z:pz,r:Math.max(bw,bd)/2+1.2});

  }else if(type==='cottage'){
    var ch=3.2;
    var cb=mkBox(5,ch,5,makeMat(0xf5deb3,0,0.9));
    cb.position.y=ch/2;g.add(cb);
    var roof=mkCone(4.5,2.8,makeMat(0xb03030,0,0.8),4);
    roof.rotation.y=Math.PI/4;roof.position.y=ch+1.4;g.add(roof);
    var door=mkBox(1,2,0.1,makeMat(0x8B4513,0,0.8));
    door.position.set(0,1,2.55);g.add(door);
    var sg2=new THREE.PlaneGeometry(3,0.7);
    var sm2=new THREE.MeshBasicMaterial({map:makeSign(url,'#5a3010','#FFD700'),transparent:true});
    var sv2=new THREE.Mesh(sg2,sm2);sv2.position.set(0,ch+0.45,2.6);g.add(sv2);
    colliders.push({x:px,z:pz,r:4.2});

  }else if(type==='tower'){
    var tw=4,td=4,th=floors*4;
    var tb=mkBox(tw,th,td,makeMat(dc||0x607D8B,0.6,0.25,dc,0.08));
    tb.position.y=th/2;g.add(tb);
    // Setback at top
    var cap=mkBox(tw*0.7,th*0.15,td*0.7,makeMat(dc||0x90A4AE,0.7,0.2));
    cap.position.y=th+th*0.075;g.add(cap);
    // Spire
    var sp=mkCone(0.35,5,makeMat(0xffd700,0.9,0.1,0xffd700,0.6),8);
    sp.position.y=th+th*0.15+2.5;g.add(sp);
    var alight=new THREE.PointLight(0xff4444,0.8,16);
    alight.position.y=th+th*0.15+5.2;g.add(alight);
    // Windows
    for(var tf=0;tf<Math.min(floors,8);tf++){
      for(var tc=0;tc<2;tc++){
        var twin=mkBox(0.6,0.8,0.06,makeMat(0xaaddff,0.1,0.1,0xaaddff,0.5));
        twin.position.set((tc-0.5)*1.2,tf*4+1.5,td/2+0.04);g.add(twin);
      }
    }
    var sg3=new THREE.PlaneGeometry(tw*0.9,1.0);
    var sm3=new THREE.MeshBasicMaterial({map:makeSign(url,'#000022','#00ffff'),transparent:true});
    var sv3=new THREE.Mesh(sg3,sm3);sv3.position.set(0,th*0.65,td/2+0.08);g.add(sv3);
    colliders.push({x:px,z:pz,r:4.5});

  }else if(type==='ruin'){
    var rh=floors*2;
    var rb=mkBox(6,rh*0.55,6,makeMat(0x888880,0,0.95));
    rb.position.y=rh*0.275;g.add(rb);
    var chunk=mkBox(3,rh*0.35,2.5,makeMat(0x77776a,0,0.95));
    chunk.position.set(-1.5,rh*0.55+rh*0.175,-1.5);chunk.rotation.z=0.28;g.add(chunk);
    var rubble=mkBox(2,rh*0.2,2,makeMat(0x666660,0,0.95));
    rubble.position.set(1.8,rh*0.1,1.5);rubble.rotation.y=0.4;g.add(rubble);
    var sg4=new THREE.PlaneGeometry(4.5,1);
    var sm4=new THREE.MeshBasicMaterial({map:makeSign('404 '+url,'#2a0000','#ff4444'),transparent:true});
    var sv4=new THREE.Mesh(sg4,sm4);sv4.position.set(0,rh*0.55+0.6,3.1);g.add(sv4);
    colliders.push({x:px,z:pz,r:4.8});

  }else if(type==='shop'){
    var sh=3.5;
    var sb=mkBox(6,sh,5,makeMat(dc||0x795548,0,0.8));
    sb.position.y=sh/2;g.add(sb);
    var awning=mkBox(7.5,0.2,1.8,makeMat(dc||0xffcc00,0,0.7));
    awning.rotation.x=-0.28;awning.position.set(0,sh+0.1,3.2);g.add(awning);
    var sg5=new THREE.PlaneGeometry(4.5,0.85);
    var sm5=new THREE.MeshBasicMaterial({map:makeSign(url,'#1a0a00','#ffcc00'),transparent:true});
    var sv5=new THREE.Mesh(sg5,sm5);sv5.position.set(0,sh+0.55,2.7);g.add(sv5);
    colliders.push({x:px,z:pz,r:4.8});

  }else if(type==='dome'){
    var dh=3;
    var db=mkBox(7,dh,7,makeMat(dc||0x9C27B0,0,0.7));
    db.position.y=dh/2;g.add(db);
    var domeGeo=new THREE.SphereGeometry(4,16,8,0,Math.PI*2,0,Math.PI/2);
    var dome=new THREE.Mesh(domeGeo,makeMat(dc||0x9C27B0,0.3,0.45,dc,0.12,true,0.8));
    dome.position.y=dh;dome.castShadow=true;g.add(dome);
    var sg6=new THREE.PlaneGeometry(4.5,0.9);
    var sm6=new THREE.MeshBasicMaterial({map:makeSign(url,'#1a001a','#ff88ff'),transparent:true});
    var sv6=new THREE.Mesh(sg6,sm6);sv6.position.set(0,dh*0.65,3.6);g.add(sv6);
    colliders.push({x:px,z:pz,r:5.5});
  }

  g.position.set(px,0,pz);g.userData.url=url;g.userData.indexed=false;g.userData.type=type;
  scene.add(g);
  buildings.push(g);
  return g;
}

// =====================================================================
//  BUILDING INSTANCES
// =====================================================================
var BDATA=[
  // Library District
  {t:'tower', x:-72,z:-75,f:5,u:'wikipedia.org',   dc:0x66BB6A},
  {t:'office',x:-56,z:-70,f:3,u:'britannica.com',  dc:0x66BB6A},
  {t:'cottage',x:-76,z:-56,f:2,u:'gutenberg.org',  dc:0xA5D6A7},
  {t:'shop',  x:-50,z:-56,f:2,u:'archive.org',     dc:0x66BB6A},
  {t:'office',x:-65,z:-48,f:3,u:'khanacademy.org', dc:0x4CAF50},
  // Market District
  {t:'tower', x: 74,z:-73,f:6,u:'amazon.com',      dc:0xFFD54F},
  {t:'shop',  x: 56,z:-68,f:2,u:'ebay.com',        dc:0xFFD54F},
  {t:'shop',  x: 70,z:-55,f:2,u:'etsy.com',        dc:0xFFD54F},
  {t:'office',x: 52,z:-52,f:4,u:'shopify.com',     dc:0xFFC107},
  {t:'cottage',x:78,z:-50,f:2,u:'craigslist.org',  dc:0xFFE082},
  // Tech Hub
  {t:'tower', x:-70,z: 73,f:7,u:'github.com',      dc:0x42A5F5},
  {t:'office',x:-54,z: 68,f:5,u:'stackoverflow.com',dc:0x42A5F5},
  {t:'office',x:-75,z: 52,f:4,u:'mozilla.org',     dc:0x42A5F5},
  {t:'dome',  x:-56,z: 56,f:3,u:'npmjs.com',       dc:0x1E88E5},
  {t:'office',x:-48,z: 78,f:4,u:'w3.org',          dc:0x42A5F5},
  // News District
  {t:'tower', x: 72,z: 72,f:6,u:'cnn.com',         dc:0xEF5350},
  {t:'office',x: 55,z: 68,f:4,u:'bbc.com',         dc:0xEF5350},
  {t:'office',x: 74,z: 56,f:3,u:'nytimes.com',     dc:0xEF5350},
  {t:'shop',  x: 52,z: 52,f:2,u:'reddit.com',      dc:0xFF7043},
  {t:'ruin',  x: 80,z: 48,f:3,u:'digg.com',        dc:0x888880},
  // Social Park
  {t:'dome',  x: 14,z:-40,f:3,u:'twitter.com',     dc:0xCE93D8},
  {t:'dome',  x:-14,z:-40,f:3,u:'facebook.com',    dc:0xCE93D8},
  {t:'office',x:  0,z:-50,f:3,u:'instagram.com',   dc:0xBA68C8},
  {t:'shop',  x: 18,z:-26,f:2,u:'tiktok.com',      dc:0xAB47BC},
  // Central Plaza
  {t:'tower', x:  0,z: -8,f:10,u:'google.com',     dc:0xFFFFFF},
  {t:'cottage',x:-16,z: 14,f:2,u:'maps.google.com',dc:0xE0E0E0},
  {t:'office',x: 16,z: 14,f:3,u:'gmail.com',       dc:0xBDBDBD},
  // Ruins in the wilderness
  {t:'ruin',  x:-90,z: 22,f:3,u:'geocities.com',   dc:0x888880},
  {t:'ruin',  x: 90,z:-22,f:2,u:'myspace.com',     dc:0x888880},
];

for(var bi=0;bi<BDATA.length;bi++){
  var bd=BDATA[bi];
  createBuilding(bd.t,bd.x,bd.z,bd.f,bd.u,bd.dc);
}

// =====================================================================
//  GOOGLE HQ SPECIAL — rainbow beacon on top of Central tower
// =====================================================================
// Find google.com building (last tower in Central)
var gHQ=null;
for(var gi=0;gi<buildings.length;gi++){
  if(buildings[gi].userData.url==='google.com'){gHQ=buildings[gi];break;}
}
if(gHQ){
  // Rainbow ring at top of tower (floors=10 → h=40)
  var hqH=10*4+10*0.15+2.5; // approx top of spire
  var rColors=[0x4285F4,0xDB4437,0xF4B400,0x0F9D58];
  for(var ri=0;ri<4;ri++){
    var ring=new THREE.Mesh(
      new THREE.TorusGeometry(2.5-ri*0.35,0.18,8,24),
      makeMat(rColors[ri],0.6,0.2,rColors[ri],0.5)
    );
    ring.position.set(0,hqH-ri*1.2,0);
    ring.rotation.x=Math.PI/2;
    gHQ.add(ring);
    gHQ.userData['ring'+ri]=ring;
  }
  // Big Google sign on building face
  var gSign=new THREE.Mesh(
    new THREE.PlaneGeometry(3.5,1.2),
    new THREE.MeshBasicMaterial({map:makeSign('google.com','#ffffff','#4285F4',256,80),transparent:true})
  );
  gSign.position.set(0,25,2.1);gHQ.add(gSign);
}

// Central Plaza fountain
(function(){
  var f=new THREE.Group();
  var base=mkCyl(3,3.2,0.4,makeMat(0xBDBDBD,0.3,0.7),16);
  base.position.y=0.2;f.add(base);
  var pillar=mkCyl(0.25,0.25,2,makeMat(0xBDBDBD,0.3,0.7),8);
  pillar.position.y=1.2;f.add(pillar);
  var bowl=mkSph(0.8,makeMat(0xB0BEC5,0.4,0.5),12);
  bowl.position.y=2.5;f.add(bowl);
  var water=new THREE.Mesh(new THREE.CircleGeometry(2.8,24),makeMat(0x29B6F6,0,0.4,0x29B6F6,0.5,true,0.7));
  water.rotation.x=-Math.PI/2;water.position.y=0.42;f.add(water);
  f.position.set(0,0,20);scene.add(f);
  colliders.push({x:0,z:20,r:3.8});
})();

// =====================================================================
//  ROBOT BUILDER
// =====================================================================
function buildRobot(){
  var r=new THREE.Group();

  var treadMat =makeMat(0x2b2b2b,0.5,0.75);
  var wheelMat =makeMat(0x1a1a1a,0.8,0.45);
  var legMat   =makeMat(0x9e9e9e,0.55,0.45);
  var torsoMat =makeMat(0x1565C0,0.35,0.55);
  var headMat  =makeMat(0x1a1a2e,0.3,0.4);
  var eyeMatL  =makeMat(0x4285F4,0.1,0.1,0x4285F4,2.0);
  var eyeMatR  =makeMat(0xDB4437,0.1,0.1,0xDB4437,2.0);
  var antMat   =makeMat(0x888888,0.8,0.35);
  var panMatR  =makeMat(0xDB4437,0.2,0.5);
  var panMatY  =makeMat(0xF4B400,0.2,0.5);
  var panMatG  =makeMat(0x0F9D58,0.2,0.5);
  var panMatB  =makeMat(0x4285F4,0.2,0.5);

  // Treads
  function makeTread(side){
    var tg=new THREE.Group();
    var hull=mkBox(1.3,1.4,3.8,treadMat);hull.position.y=0.7;tg.add(hull);
    for(var wi=0;wi<4;wi++){
      var wz=(wi-1.5)*0.95;
      var wh=mkCyl(0.62,0.62,0.28,wheelMat,10);
      wh.rotation.z=Math.PI/2;wh.position.set(0,0.58,wz);
      tg.add(wh);tg.userData['w'+wi]=wh;
    }
    tg.position.x=side*2.0;
    return tg;
  }
  var treadL=makeTread(-1);
  var treadR=makeTread( 1);
  r.add(treadL);r.add(treadR);

  // Legs
  var lL=mkBox(0.7,1.6,0.7,legMat);lL.position.set(-0.8,1.5,0);r.add(lL);
  var lR=mkBox(0.7,1.6,0.7,legMat);lR.position.set( 0.8,1.5,0);r.add(lR);

  // Torso
  var torso=mkBox(3.6,2.6,2.6,torsoMat);torso.position.set(0,3.5,0);r.add(torso);

  // Google color panels on chest
  var pR=mkBox(0.75,0.75,0.1,panMatR);pR.position.set(-1.0,3.85,1.35);r.add(pR);
  var pY=mkBox(0.75,0.75,0.1,panMatY);pY.position.set(-0.2,3.85,1.35);r.add(pY);
  var pG=mkBox(0.75,0.75,0.1,panMatG);pG.position.set( 0.6,3.85,1.35);r.add(pG);
  var pB=mkBox(0.75,0.75,0.1,panMatB);pB.position.set( 0.6,2.95,1.35);r.add(pB);

  // Arm stubs
  var aL=mkBox(0.5,0.4,0.45,legMat);aL.position.set(-2.15,3.7,0);r.add(aL);
  var aR=mkBox(0.5,0.4,0.45,legMat);aR.position.set( 2.15,3.7,0);r.add(aR);

  // Head
  var head=mkSph(1.25,headMat,16);head.position.set(0,5.6,0);r.add(head);

  // Eyes
  var eL=mkSph(0.3,eyeMatL,8);eL.position.set(-0.52,5.7,1.1);r.add(eL);
  var eR=mkSph(0.3,eyeMatR,8);eR.position.set( 0.52,5.7,1.1);r.add(eR);

  // Eye glow
  var glL=new THREE.PointLight(0x4285F4,0.55,4);glL.position.set(-0.52,5.7,1.5);r.add(glL);
  var glR=new THREE.PointLight(0xDB4437,0.55,4);glR.position.set( 0.52,5.7,1.5);r.add(glR);

  // Antenna
  var antStem=mkCyl(0.08,0.08,1.6,antMat,6);antStem.position.set(0,7.1,0);r.add(antStem);
  var antBall=mkSph(0.26,makeMat(0xffd700,0.9,0.1,0xffd700,1.2),8);
  antBall.position.set(0,8.0,0);r.add(antBall);

  r.userData.treadL=treadL;r.userData.treadR=treadR;
  r.userData.antBall=antBall;
  r.userData.eL=eL;r.userData.eR=eR;
  r.userData.glL=glL;r.userData.glR=glR;
  r.userData.lL=lL;r.userData.lR=lR;

  return r;
}

var robot=buildRobot();
robot.position.set(0,0,12);  // start in Central Plaza
robot.rotation.y=Math.PI;     // face north
scene.add(robot);

// Robot shadow
robot.traverse(function(o){if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});

// =====================================================================
//  NPC BUILDER
// =====================================================================
function buildNPC(color, skinTone){
  skinTone=skinTone||0xffcc99;
  var n=new THREE.Group();
  var bMat=makeMat(color,0,0.8);
  var sMat=makeMat(skinTone,0,0.9);
  var pMat=makeMat(0x37474F,0,0.9);

  // Legs
  var ll=mkCyl(0.12,0.12,0.9,pMat,6);ll.position.set(-0.15,0.45,0);n.add(ll);
  var lr=mkCyl(0.12,0.12,0.9,pMat,6);lr.position.set( 0.15,0.45,0);n.add(lr);
  // Body
  var body=mkCyl(0.38,0.42,1.2,bMat,8);body.position.y=1.2;n.add(body);
  // Arms
  var al=mkCyl(0.1,0.1,0.75,bMat,6);al.rotation.z= 0.55;al.position.set(-0.55,1.55,0);n.add(al);
  var ar=mkCyl(0.1,0.1,0.75,bMat,6);ar.rotation.z=-0.55;ar.position.set( 0.55,1.55,0);n.add(ar);
  // Head
  var head=mkSph(0.35,sMat,8);head.position.y=2.15;n.add(head);

  n.userData.ll=ll;n.userData.lr=lr;
  n.traverse(function(o){if(o.isMesh){o.castShadow=true;}});
  return n;
}

// NPC spawn data: color, district center range, skin tone
var NPC_DEFS=[
  // Library
  {color:0x2E7D32,cx:-62,cz:-62,range:22,skin:0xffe0bd},
  {color:0x388E3C,cx:-62,cz:-62,range:22,skin:0xd4a574},
  {color:0x43A047,cx:-62,cz:-62,range:22,skin:0xffcc99},
  // Market
  {color:0xF57F17,cx:62,cz:-62,range:22,skin:0xffe0bd},
  {color:0x9E9E9E,cx:62,cz:-62,range:22,skin:0xd4a574},
  {color:0xFFA000,cx:62,cz:-62,range:22,skin:0xffcc99},
  // Tech Hub
  {color:0x0D47A1,cx:-62,cz:62,range:22,skin:0xffe0bd},
  {color:0x1565C0,cx:-62,cz:62,range:22,skin:0xffcc99},
  {color:0x1976D2,cx:-62,cz:62,range:22,skin:0xd4a574},
  // News
  {color:0xB71C1C,cx:62,cz:62,range:22,skin:0xffe0bd},
  {color:0xC62828,cx:62,cz:62,range:22,skin:0xffcc99},
  // Social Park
  {color:0x7B1FA2,cx:0,cz:-30,range:15,skin:0xffe0bd},
  {color:0x8E24AA,cx:0,cz:-30,range:15,skin:0xd4a574},
  // Central
  {color:0x455A64,cx:0,cz:5,range:14,skin:0xffe0bd},
  {color:0x546E7A,cx:0,cz:5,range:14,skin:0xffcc99},
];

function randWaypoints(cx,cz,range,count){
  var wps=[];
  for(var i=0;i<count;i++){
    wps.push(new THREE.Vector3(
      cx+(Math.random()-0.5)*range*2,
      0,
      cz+(Math.random()-0.5)*range*2
    ));
  }
  return wps;
}

for(var ni=0;ni<NPC_DEFS.length;ni++){
  var nd=NPC_DEFS[ni];
  var npc=buildNPC(nd.color,nd.skin);
  npc.position.set(nd.cx+(Math.random()-0.5)*nd.range*1.5,0,nd.cz+(Math.random()-0.5)*nd.range*1.5);
  scene.add(npc);
  npcs.push(npc);
  npcData.push({
    waypoints:randWaypoints(nd.cx,nd.cz,nd.range,5),
    currentWaypoint:0,
    walkTime:Math.random()*10,
    speed:0.025+Math.random()*0.025
  });
}

// =====================================================================
//  DATA PARTICLES (packets traveling along roads)
// =====================================================================
var PCOLORS=[0x4285F4,0xDB4437,0xF4B400,0x0F9D58,0x00BCD4,0xE040FB];
var partMat=[];
for(var pi=0;pi<PCOLORS.length;pi++){
  partMat.push(makeMat(PCOLORS[pi],0.1,0.1,PCOLORS[pi],1.5));
}

function makeParticle(pathIdx){
  var path=roadPaths[pathIdx];
  var pmesh=mkSph(0.22,partMat[Math.floor(Math.random()*partMat.length)],6);
  pmesh.position.set(path[0].x,0.5,path[0].z);
  scene.add(pmesh);
  particles.push({mesh:pmesh,path:path,t:0,speed:0.002+Math.random()*0.004,pathIdx:pathIdx,forward:Math.random()>0.5});
}

for(var pii=0;pii<28;pii++){
  var pathIdx=pii%roadPaths.length;
  var p=makeParticle(pathIdx);
  // Stagger start positions
  particles[particles.length-1].t=Math.random();
}

// =====================================================================
//  INPUT HANDLING
// =====================================================================
window.addEventListener('keydown',function(e){
  keys[e.code]=true;
  if(e.code==='KeyR'){
    showResults=!showResults;
    document.getElementById('results-panel').style.display=showResults?'block':'none';
  }
  if(e.code==='KeyE'&&nearbyBuilding&&!nearbyBuilding.userData.indexed){
    indexBuilding(nearbyBuilding);
  }
  if(e.code==='Space'){e.preventDefault();}
},false);
window.addEventListener('keyup',function(e){keys[e.code]=false;},false);

// Prevent arrow key scroll
window.addEventListener('keydown',function(e){
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].indexOf(e.code)>-1){e.preventDefault();}
},false);

// =====================================================================
//  INDEXING SYSTEM
// =====================================================================
var indexRing=new THREE.Mesh(
  new THREE.RingGeometry(4,4.4,32),
  makeMat(0x4285F4,0,0.1,0x4285F4,1.5,true,0.8)
);
indexRing.rotation.x=-Math.PI/2;
indexRing.position.y=0.1;
indexRing.visible=false;
scene.add(indexRing);

function indexBuilding(b){
  b.userData.indexed=true;
  indexedUrls.push({url:b.userData.url,snippet:snippets[b.userData.url]||'A site on the World Wide Web',type:b.userData.type});

  // Glow effect on building
  b.traverse(function(o){
    if(o.isMesh&&o.material&&o.material.emissive){
      o.material.emissive.setHex(0x4285F4);
      o.material.emissiveIntensity=0.4;
    }
  });

  // Add blue glow ring to building
  var glowRing=new THREE.Mesh(
    new THREE.RingGeometry(3.5,3.8,24),
    makeMat(0x4285F4,0,0.1,0x4285F4,1.2,true,0.7)
  );
  glowRing.rotation.x=-Math.PI/2;
  glowRing.position.y=0.08;
  b.add(glowRing);

  // Update HUD
  document.getElementById('icount').textContent=indexedUrls.length;

  // Toast
  var toast=document.getElementById('toast');
  toast.textContent='Indexed: '+b.userData.url;
  toast.style.display='block';
  setTimeout(function(){toast.style.display='none';},2200);

  // Add to results panel
  var li=document.createElement('div');
  li.className='ri';
  li.innerHTML='<div class="ru">'+b.userData.url+'</div><div class="rs">'+(snippets[b.userData.url]||'Web page')+'</div>';
  document.getElementById('rlist').appendChild(li);

  // Auto-show results panel briefly
  var rp=document.getElementById('results-panel');
  rp.style.display='block';
  showResults=true;
}

// =====================================================================
//  MINIMAP RENDERER
// =====================================================================
var mmCtx=document.getElementById('mm').getContext('2d');

function updateMinimap(){
  var W=140,S=WORLD;
  mmCtx.fillStyle='#111';mmCtx.fillRect(0,0,W,W);
  // District zones
  var dColors=['#2E7D32','#F57F17','#0D47A1','#B71C1C','#7B1FA2','#555555'];
  for(var mi=0;mi<DISTRICTS.length;mi++){
    var md=DISTRICTS[mi];
    var mx=(md.cx+S/2)/S*W-(md.w/S*W)/2;
    var mz=(md.cz+S/2)/S*W-(md.h/S*W)/2;
    mmCtx.fillStyle=dColors[mi];mmCtx.globalAlpha=0.4;
    mmCtx.fillRect(mx,mz,md.w/S*W,md.h/S*W);
  }
  mmCtx.globalAlpha=1;
  // Roads
  mmCtx.strokeStyle='#555';mmCtx.lineWidth=1.5;
  mmCtx.beginPath();mmCtx.moveTo(W/2,0);mmCtx.lineTo(W/2,W);mmCtx.stroke();
  mmCtx.beginPath();mmCtx.moveTo(0,W/2);mmCtx.lineTo(W,W/2);mmCtx.stroke();
  // Buildings
  for(var mbi=0;mbi<buildings.length;mbi++){
    var mb=buildings[mbi];
    var bx=(mb.position.x+S/2)/S*W;
    var bz=(mb.position.z+S/2)/S*W;
    mmCtx.fillStyle=mb.userData.indexed?'#4285F4':'#888';
    mmCtx.fillRect(bx-1.5,bz-1.5,3,3);
  }
  // Robot (yellow dot)
  var rx=(robot.position.x+S/2)/S*W;
  var rz=(robot.position.z+S/2)/S*W;
  mmCtx.fillStyle='#FFD700';
  mmCtx.beginPath();mmCtx.arc(rx,rz,3.5,0,Math.PI*2);mmCtx.fill();
  // Robot direction indicator
  mmCtx.strokeStyle='#FFD700';mmCtx.lineWidth=1.5;
  mmCtx.beginPath();
  mmCtx.moveTo(rx,rz);
  mmCtx.lineTo(rx-Math.sin(robotAngle)*8,rz-Math.cos(robotAngle)*8);
  mmCtx.stroke();
}

// =====================================================================
//  DISTRICT DETECTION
// =====================================================================
function getDistrictName(){
  var rx=robot.position.x, rz=robot.position.z;
  for(var i=0;i<DISTRICTS.length;i++){
    var d=DISTRICTS[i];
    if(Math.abs(rx-d.cx)<d.w/2&&Math.abs(rz-d.cz)<d.h/2)return i;
  }
  return -1;
}
var lastDistrict=-1;
function updateDistrictLabel(){
  var idx=getDistrictName();
  if(idx!==lastDistrict){
    lastDistrict=idx;
    var badge=document.getElementById('district-badge');
    if(idx>=0){
      badge.textContent=DISTRICTS[idx].name;
      badge.style.borderColor=DISTRICTS[idx].bdrColor;
    }else{
      badge.textContent='Wilderness';
      badge.style.borderColor='#888';
    }
  }
}

// =====================================================================
//  LERP PATH HELPER (for particles)
// =====================================================================
function lerpPath(path,t,forward){
  if(path.length<2)return{x:path[0].x,z:path[0].z};
  var segs=path.length-1;
  var totalT=forward?t:(1-t);
  var segT=totalT*segs;
  var segIdx=Math.min(segs-1,Math.floor(segT));
  var local=segT-segIdx;
  var a=path[segIdx], b=path[segIdx+1];
  return{x:a.x+(b.x-a.x)*local,z:a.z+(b.z-a.z)*local};
}

// =====================================================================
//  ANIMATION LOOP
// =====================================================================
var clock=new THREE.Clock();
var walkCycle=0;

function animate(){
  requestAnimationFrame(animate);
  var delta=Math.min(clock.getDelta(),0.05);
  time+=delta;

  // --- ROBOT MOVEMENT ---
  var turning=false;
  if(keys['KeyA']||keys['ArrowLeft']){robotAngle+=ROT_SPD;turning=true;}
  if(keys['KeyD']||keys['ArrowRight']){robotAngle-=ROT_SPD;turning=true;}

  var accel=0;
  if(keys['KeyW']||keys['ArrowUp'])  accel= MOVE_SPD;
  if(keys['KeyS']||keys['ArrowDown'])accel=-MOVE_SPD*0.6;

  robotVel=robotVel*0.82+accel*0.18;
  if(Math.abs(robotVel)<0.001)robotVel=0;

  var newX=robot.position.x+Math.sin(robotAngle)*robotVel;
  var newZ=robot.position.z+Math.cos(robotAngle)*robotVel;

  // World bounds
  newX=Math.max(-WORLD/2,Math.min(WORLD/2,newX));
  newZ=Math.max(-WORLD/2,Math.min(WORLD/2,newZ));

  // Collision check
  var blocked=false;
  for(var ci=0;ci<colliders.length;ci++){
    var col=colliders[ci];
    var cdx=newX-col.x, cdz=newZ-col.z;
    if(cdx*cdx+cdz*cdz<col.r*col.r){blocked=true;break;}
  }
  if(!blocked){robot.position.x=newX;robot.position.z=newZ;}
  robot.rotation.y=robotAngle;

  // Walking animation
  if(Math.abs(robotVel)>0.005||turning){
    walkCycle+=delta*6*Math.abs(robotVel)/MOVE_SPD+delta*2*(turning?1:0);
    // Tread wheels spin
    var tL=robot.userData.treadL, tR=robot.userData.treadR;
    if(tL){for(var k in tL.userData){if(tL.userData[k]&&tL.userData[k].rotation)tL.userData[k].rotation.x+=robotVel*0.5;}}
    if(tR){for(var k in tR.userData){if(tR.userData[k]&&tR.userData[k].rotation)tR.userData[k].rotation.x+=robotVel*0.5;}}
    // Leg bob
    var lL=robot.userData.lL, lR=robot.userData.lR;
    if(lL)lL.position.y=1.5+Math.sin(walkCycle)*0.08;
    if(lR)lR.position.y=1.5+Math.sin(walkCycle+Math.PI)*0.08;
  }

  // Antenna sway
  var ab=robot.userData.antBall;
  if(ab){ab.position.y=8.0+Math.sin(time*2.8)*0.1;ab.position.x=Math.sin(time*1.9)*0.05;}

  // Eye blink
  var blink=Math.sin(time*1.7)>0.94;
  var eL=robot.userData.eL, eR=robot.userData.eR;
  if(eL)eL.scale.y=blink?0.08:1;
  if(eR)eR.scale.y=blink?0.08:1;

  // Eye glow pulse
  var gl=robot.userData.glL, gr=robot.userData.glR;
  var gp=0.45+Math.sin(time*3)*0.15;
  if(gl)gl.intensity=blink?0:gp;
  if(gr)gr.intensity=blink?0:gp;

  // --- CAMERA FOLLOW ---
  var camOffX=Math.sin(robotAngle)*13;
  var camOffZ=Math.cos(robotAngle)*13;
  var camTX=robot.position.x+camOffX;
  var camTY=robot.position.y+7.5;
  var camTZ=robot.position.z+camOffZ;
  camera.position.x+=(camTX-camera.position.x)*0.09;
  camera.position.y+=(camTY-camera.position.y)*0.09;
  camera.position.z+=(camTZ-camera.position.z)*0.09;
  camera.lookAt(robot.position.x,robot.position.y+3,robot.position.z);

  // --- NPC MOVEMENT ---
  for(var ni=0;ni<npcs.length;ni++){
    var npc=npcs[ni];
    var nd=npcData[ni];
    var wp=nd.waypoints[nd.currentWaypoint];
    var dx=wp.x-npc.position.x, dz=wp.z-npc.position.z;
    var dist2D=Math.sqrt(dx*dx+dz*dz);
    if(dist2D<0.8){
      nd.currentWaypoint=(nd.currentWaypoint+1)%nd.waypoints.length;
    }else{
      var ns=nd.speed;
      npc.position.x+=dx/dist2D*ns;
      npc.position.z+=dz/dist2D*ns;
      npc.rotation.y=Math.atan2(dx,dz);
      nd.walkTime+=delta*4;
      var nll=npc.userData.ll, nlr=npc.userData.lr;
      if(nll)nll.rotation.x=Math.sin(nd.walkTime)*0.35;
      if(nlr)nlr.rotation.x=-Math.sin(nd.walkTime)*0.35;
    }
    // Face robot if nearby
    var rdx=robot.position.x-npc.position.x;
    var rdz=robot.position.z-npc.position.z;
    var rdist=Math.sqrt(rdx*rdx+rdz*rdz);
    if(rdist<7){npc.rotation.y=Math.atan2(rdx,rdz);}
  }

  // --- DATA PARTICLES ---
  for(var pi=0;pi<particles.length;pi++){
    var part=particles[pi];
    part.t+=part.speed;
    if(part.t>1){part.t=0;part.forward=!part.forward;}
    var pos=lerpPath(part.path,part.t,part.forward);
    part.mesh.position.x=pos.x;
    part.mesh.position.z=pos.z;
    part.mesh.position.y=0.4+Math.sin(time*5+pi*0.8)*0.12;
    part.mesh.rotation.y+=0.05;
  }

  // --- GOOGLE HQ RING SPIN ---
  if(gHQ){
    for(var ri=0;ri<4;ri++){
      var ring=gHQ.userData['ring'+ri];
      if(ring){ring.rotation.z+=0.008*(ri%2===0?1:-1);}
    }
  }

  // --- SUN SLOW CYCLE (day atmosphere) ---
  var sunCy=Math.sin(time*0.01)*0.15+0.85;
  sun.intensity=sunCy;

  // --- PROXIMITY CHECK FOR INDEXING ---
  nearbyBuilding=null;
  var bestDist=8.5;
  for(var ii=0;ii<buildings.length;ii++){
    var ib=buildings[ii];
    if(!ib.userData.indexed){
      var ibdx=robot.position.x-ib.position.x;
      var ibdz=robot.position.z-ib.position.z;
      var ibdist=Math.sqrt(ibdx*ibdx+ibdz*ibdz);
      if(ibdist<bestDist){bestDist=ibdist;nearbyBuilding=ib;}
    }
  }
  var nInd=document.getElementById('nearby-ind');
  if(nearbyBuilding){
    indexRing.position.x=nearbyBuilding.position.x;
    indexRing.position.z=nearbyBuilding.position.z;
    indexRing.visible=true;
    indexRing.rotation.z+=0.03;
    indexRing.material.opacity=0.6+Math.sin(time*4)*0.3;
    nInd.style.display='block';
    document.getElementById('nearby-url').textContent=nearbyBuilding.userData.url;
  }else{
    indexRing.visible=false;
    nInd.style.display='none';
  }

  // --- HUD ---
  updateDistrictLabel();
  updateMinimap();

  renderer.render(scene,camera);
}

animate();

// =====================================================================
//  RESIZE
// =====================================================================
window.addEventListener('resize',function(){
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth,window.innerHeight);
},false);
'''

HTML_CLOSE = '''</body>
</html>
'''

print("Assembling googlebot-world.html ...")
output = (
    HTML_HEAD
    + '<script>\n' + three_js + '\n</script>\n'
    + '<script>\n' + MAIN_JS + '\n</script>\n'
    + HTML_CLOSE
)

out_path = '/home/user/web5-10/googlebot-world.html'
with open(out_path, 'w') as f:
    f.write(output)

size = os.path.getsize(out_path)
print("Done! File: {} ({:.1f} KB)".format(out_path, size/1024))
