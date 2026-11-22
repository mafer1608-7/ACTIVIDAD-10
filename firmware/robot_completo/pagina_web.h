// Aplicacion web del robot (servida por el ESP32, no necesita internet)
#pragma once

const char PAGINA_WEB[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Robot móvil – Panel de control</title>
<style>
:root{
 --papel:#e6e0cc;--cara:#f4f0e2;--tinta:#1a1a17;--tinta2:#5b574b;
 --azul:#1d3f73;--naranja:#d4501b;--ambar:#ffb000;--verde:#2f7a3a;--rojo:#b3261e;
 --cond:Bahnschrift,"Arial Narrow","Roboto Condensed","Franklin Gothic Medium",sans-serif;
 --mono:Consolas,"SF Mono",Menlo,"Liberation Mono","Courier New",monospace;
}
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;touch-action:manipulation}
body{margin:0;background:var(--papel);color:var(--tinta);font-family:var(--mono);font-size:14px;
 background-image:linear-gradient(rgba(26,26,23,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(26,26,23,.05) 1px,transparent 1px);
 background-size:24px 24px}

/* ---------- cabecera ---------- */
header{background:var(--tinta);color:var(--papel);display:flex;align-items:center;justify-content:space-between;
 gap:12px;flex-wrap:wrap;padding:10px 16px;border-bottom:4px solid var(--naranja)}
.titulo{font-family:var(--cond);font-size:24px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;line-height:1}
.titulo small{display:block;font-family:var(--mono);font-size:11px;font-weight:400;letter-spacing:.12em;color:#9a9484;margin-top:5px}
.lamps{display:flex;gap:14px;flex-wrap:wrap}
.lamp{font-family:var(--cond);font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:#7d786a}
.lamp::before{content:"";display:inline-block;width:10px;height:10px;border:2px solid currentColor;margin-right:6px;vertical-align:-1px}
.lamp.on{color:var(--ambar)}.lamp.on::before{background:var(--ambar)}
.lamp.enlace.on{color:#7ddc6e}.lamp.enlace.on::before{background:#7ddc6e}

/* ---------- distribucion ---------- */
main{display:grid;gap:14px;padding:14px;max-width:1280px;margin:auto;
 grid-template-columns:1fr;
 grid-template-areas:"ctrl" "rumbo" "mision" "bit" "sens" "cal" "reg"}
@media(min-width:700px){main{grid-template-columns:1fr 1fr;
 grid-template-areas:"rumbo rumbo" "ctrl mision" "bit sens" "cal reg"}}
@media(min-width:1050px){main{grid-template-columns:1.1fr 1.1fr 1fr;
 grid-template-areas:"rumbo rumbo ctrl" "rumbo rumbo mision" "bit sens cal" "reg reg reg"}}
.mod{background:var(--cara);border:2px solid var(--tinta);box-shadow:5px 5px 0 var(--tinta);padding:0 14px 14px;min-width:0}
.mod>h2{margin:0 -14px 12px;padding:6px 14px;background:var(--tinta);color:var(--papel);
 font-family:var(--cond);font-size:14px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;display:flex;gap:10px}
.mod>h2 b{color:var(--ambar);font-weight:700}
#m-ctrl{grid-area:ctrl}#m-rumbo{grid-area:rumbo}#m-mision{grid-area:mision}
#m-bit{grid-area:bit}#m-sens{grid-area:sens}#m-cal{grid-area:cal}#m-reg{grid-area:reg}

/* ---------- controles ---------- */
.btn{font-family:var(--cond);font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--tinta);
 background:var(--cara);border:2px solid var(--tinta);box-shadow:3px 3px 0 var(--tinta);padding:8px 12px;cursor:pointer;border-radius:0}
.btn:active,.btn.on{transform:translate(3px,3px);box-shadow:0 0 0 var(--tinta);background:var(--tinta);color:var(--papel)}
.btn.go{background:var(--naranja);color:#fff}
.btn.go:active{background:var(--tinta)}
.btn.parar{background:var(--rojo);color:#fff;width:100%;padding:12px;font-size:16px;margin-top:12px}
.teclas{display:grid;grid-template-columns:repeat(3,64px);grid-template-rows:repeat(2,64px);gap:8px;justify-content:center;margin-top:4px}
.tecla{font-family:var(--mono);font-size:22px;font-weight:700;padding:0;line-height:1;display:flex;flex-direction:column;
 align-items:center;justify-content:center;gap:3px}
.tecla small{font-size:11px;font-weight:400;letter-spacing:.1em;opacity:.7}
.tecla.w{grid-column:2}
.fila{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}
.fila>label{font-family:var(--cond);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--tinta2)}
input[type=number]{width:86px;padding:7px 8px;border:2px solid var(--tinta);border-radius:0;background:#fff;color:var(--tinta);
 font-family:var(--mono);font-size:16px;font-weight:700;-webkit-user-select:text;user-select:text}
input[type=range]{flex:1;min-width:100px;accent-color:var(--tinta);height:26px}
.val{font-family:var(--mono);font-weight:700;min-width:44px;text-align:right}
.nota{font-size:12px;color:var(--tinta2);margin-top:10px;line-height:1.4}
.rosa{display:flex;gap:8px;margin-top:12px}.rosa .btn{flex:1;padding:7px 0}

/* ---------- lecturas ---------- */
.dato{display:flex;align-items:baseline;gap:6px;padding:5px 0;font-size:13px}
.dato span{font-family:var(--cond);letter-spacing:.06em;text-transform:uppercase;color:var(--tinta2);white-space:nowrap}
.dato i{flex:1;border-bottom:2px dotted #9b967f;transform:translateY(-3px);min-width:10px}
.dato b{font-weight:700;text-align:right}
.barra{height:14px;border:2px solid var(--tinta);background:#fff;position:relative;margin:6px 0 4px}
.barra div{height:100%;width:0;background:var(--azul);transition:width .15s}
.barra::after{content:"";position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 8px,var(--cara) 8px 10px)}
.rojo{color:var(--rojo)}

/* ---------- brujula ---------- */
#brujula{display:block;margin:6px auto 0;width:100%;max-width:400px;height:auto}
.lecturas{display:grid;grid-template-columns:repeat(3,1fr);border:2px solid var(--tinta);margin-top:12px;background:#fff}
.lecturas div{padding:8px 6px;text-align:center;border-right:2px solid var(--tinta)}
.lecturas div:last-child{border-right:0}
.lecturas span{display:block;font-family:var(--cond);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--tinta2)}
.lecturas b{display:block;font-size:34px;line-height:1.1;font-variant-numeric:tabular-nums}
#nAct{color:var(--azul)}#nObj{color:var(--naranja)}

/* ---------- bitacora ---------- */
#ev{list-style:none;margin:0;padding:0;font-size:12.5px;line-height:1.35}
#ev li{padding:5px 0 5px 16px;border-bottom:1px dotted #9b967f;position:relative}
#ev li::before{content:"›";position:absolute;left:2px;color:var(--tinta2)}
#ev li:first-child{font-weight:700}
#ev li:first-child::before{color:var(--naranja)}
#grafica{display:block;width:100%;height:auto;border:2px solid var(--tinta);background:#fbf9f0}
canvas{max-width:100%}
</style></head><body>

<header>
 <div class="titulo">Robot móvil de coordenadas polares<small>ESP32-S3 · MICROS · PROYECTO FINAL</small></div>
 <div class="lamps">
  <span class="lamp" data-m="MANUAL">Manual</span>
  <span class="lamp" data-m="AUTONOMO">Auto</span>
  <span class="lamp" data-m="GIRO">Giro</span>
  <span class="lamp" data-m="CALIBRANDO">Calib.</span>
  <span class="lamp" data-m="PRUEBA">Prueba</span>
  <span class="lamp enlace" id="con">Enlace</span>
 </div>
</header>

<main>
 <section class="mod" id="m-ctrl"><h2><b>01</b>Control manual</h2>
  <div class="teclas">
   <button class="btn tecla w" data-d="w">▲<small>W</small></button>
   <button class="btn tecla" data-d="a" style="grid-row:2;grid-column:1">◀<small>A</small></button>
   <button class="btn tecla" data-d="s" style="grid-row:2;grid-column:2">▼<small>S</small></button>
   <button class="btn tecla" data-d="d" style="grid-row:2;grid-column:3">▶<small>D</small></button>
  </div>
  <button class="btn parar" id="bStop">Parar · espacio</button>
  <div class="fila"><label>Velocidad</label><input id="vel" type="range" min="30" max="100" value="70"><span class="val" id="velTxt">70%</span></div>
  <div class="dato"><span>Motor izq / der</span><i></i><b id="mot">0 / 0</b></div>
  <p class="nota">También con las teclas W A S D o las flechas. Mover el robot a mano cancela el modo autónomo.</p>
 </section>

 <section class="mod" id="m-rumbo"><h2><b>02</b>Dirección polar · respecto al norte</h2>
  <canvas id="brujula" width="400" height="400"></canvas>
  <div class="lecturas">
   <div><span>Actual</span><b id="nAct">---°</b></div>
   <div><span>Deseada</span><b id="nObj">---°</b></div>
   <div><span>Error</span><b id="nErr">---°</b></div>
  </div>
  <p class="nota">Toque la carta para fijar la dirección deseada. La cuña naranja muestra cuánto falta por girar.</p>
 </section>

 <section class="mod" id="m-mision"><h2><b>03</b>Navegación autónoma</h2>
  <div class="fila" style="margin-top:4px"><label>Rumbo °</label><input id="hdg" type="number" min="0" max="359" value="0">
   <label>Distancia cm</label><input id="dst" type="number" min="10" max="2000" value="100"></div>
  <div class="rosa"><button class="btn" data-h="0">N</button><button class="btn" data-h="90">E</button><button class="btn" data-h="180">S</button><button class="btn" data-h="270">O</button></div>
  <div class="fila"><label>Velocidad</label><input id="vAuto" type="range" min="40" max="85" value="60"><span class="val" id="vAutoTxt">60%</span></div>
  <div class="fila"><button class="btn go" id="bIniciar">Iniciar misión</button><button class="btn" id="bGirar">Solo girar al rumbo</button></div>
  <div class="dato" style="margin-top:10px"><span>Fase</span><i></i><b id="fase">-</b></div>
  <div class="dato"><span>Recorrido</span><i></i><b id="prog">0 / 0 cm</b></div>
  <div class="barra"><div id="progBar"></div></div>
 </section>

 <section class="mod" id="m-bit"><h2><b>04</b>Bitácora</h2>
  <ul id="ev"><li>Esperando datos…</li></ul>
 </section>

 <section class="mod" id="m-sens"><h2><b>05</b>Sensores</h2>
  <div class="dato"><span>Distancia frontal</span><i></i><b id="dist">-</b></div>
  <div class="barra"><div id="distBar"></div></div>
  <div class="dato"><span>Magnetómetro</span><i></i><b id="magTipo">-</b></div>
  <div class="dato"><span>Campo X / Y / Z</span><i></i><b id="crudo">-</b></div>
  <div class="dato"><span>Rumbo solo magnet.</span><i></i><b id="rMag">-</b></div>
  <div class="dato"><span>Acelerómetro g</span><i></i><b id="acel">-</b></div>
  <div class="dato"><span>Giroscopio °/s</span><i></i><b id="gir">-</b></div>
  <div class="dato"><span>Fusión giroscopio</span><i></i><b id="fus">-</b></div>
  <div class="dato"><span>Encoders rpm i / d</span><i></i><b id="rpm">-</b></div>
  <div class="dato"><span>Odometría</span><i></i><b id="odo">-</b></div>
 </section>

 <section class="mod" id="m-cal"><h2><b>06</b>Calibración</h2>
  <div class="fila" style="margin-top:4px"><button class="btn" id="bCal">1 · Calibrar brújula (20 s)</button></div>
  <div class="barra"><div id="calBar" style="background:var(--naranja)"></div></div>
  <div class="fila"><button class="btn" id="bNorte">2 · Mirando al norte: fijar 0°</button></div>
  <div class="fila"><button class="btn" id="bBorrar">Borrar ajuste</button><button class="btn" id="bInv">Invertir sentido</button></div>
  <div class="fila"><button class="btn" id="bPrueba">Prueba de distancia (3 s)</button></div>
  <div class="fila"><label>Medido cm</label><input id="cmReal" type="number" min="5" max="500" value="60"><button class="btn" id="bCalDist">Guardar</button></div>
  <div class="dato" style="margin-top:8px"><span>Distancia por tiempo</span><i></i><b id="cmps">-</b></div>
  <div class="dato"><span>Encoders factor / prueba</span><i></i><b id="fenc">-</b></div>
 </section>

 <section class="mod" id="m-reg"><h2><b>07</b>Registro · rumbo actual contra deseado</h2>
  <canvas id="grafica" width="900" height="200"></canvas>
  <div class="fila"><button class="btn" id="bCsv">Descargar CSV</button><button class="btn" id="bLimpiar">Borrar registro</button><b id="nLog">0 muestras</b></div>
  <p class="nota">Se guarda en este navegador cada 0,1 s. Sirve para las tablas y gráficos del informe.</p>
 </section>
</main>

<script>
const $=id=>document.getElementById(id);
const teclas=new Set();
let J=null,ultimoOk=0,ocupado=false;
let LOG=[],HIST=[];
const TINTA='#1a1a17',CARA='#f4f0e2',AZUL='#1d3f73',NARANJA='#d4501b';

const dif=(a,b)=>{let d=a-b;while(d>180)d-=360;while(d<-180)d+=360;return d};
const norm=a=>((a%360)+360)%360;

/* ---------- teclado y botones ---------- */
const mapa={w:'w',arrowup:'w',s:'s',arrowdown:'s',a:'a',arrowleft:'a',d:'d',arrowright:'d'};
addEventListener('keydown',e=>{
 if(e.target.tagName==='INPUT')return;
 const k=mapa[e.key.toLowerCase()];
 if(k){teclas.add(k);e.preventDefault();marcar();}
 if(e.key===' '){parar();e.preventDefault();}
});
addEventListener('keyup',e=>{const k=mapa[e.key.toLowerCase()];if(k){teclas.delete(k);marcar();}});
addEventListener('blur',()=>{teclas.clear();marcar();});
document.querySelectorAll('[data-d]').forEach(b=>{
 const d=b.dataset.d;
 b.addEventListener('pointerdown',e=>{teclas.add(d);b.setPointerCapture(e.pointerId);marcar();});
 ['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,()=>{teclas.delete(d);marcar();}));
});
function marcar(){document.querySelectorAll('[data-d]').forEach(b=>b.classList.toggle('on',teclas.has(b.dataset.d)));}
$('vel').oninput=()=>$('velTxt').textContent=$('vel').value+'%';
$('vAuto').oninput=()=>$('vAutoTxt').textContent=$('vAuto').value+'%';

function comando(){
 const v=(teclas.has('w')?1:0)-(teclas.has('s')?1:0);
 let w=(teclas.has('d')?1:0)-(teclas.has('a')?1:0);
 if(v!==0&&w!==0)w*=0.5;
 const s=+$('vel').value;
 const lim=x=>Math.round(Math.max(-1,Math.min(1,x))*s);
 return [lim(v+w),lim(v-w)];
}

/* ---------- comunicacion bidireccional ---------- */
async function pedir(url){
 try{
  const r=await fetch(url,{cache:'no-store'});
  const j=await r.json();ultimoOk=Date.now();mostrar(j);
 }catch(e){}
}
async function ciclo(){
 if(!ocupado){ocupado=true;const [l,r]=comando();await pedir(`/ctrl?l=${l}&r=${r}`);ocupado=false;}
 $('con').classList.toggle('on',Date.now()-ultimoOk<1000);
}
setInterval(ciclo,100);

function parar(){teclas.clear();marcar();pedir('/stop');}
$('bStop').onclick=parar;
$('bCal').onclick=()=>{if(confirm('El robot girará solo 20 s. ¿Está en el piso, con espacio libre y lejos de metales?'))pedir('/calibrar');};
$('bNorte').onclick=()=>pedir('/norte');
$('bBorrar').onclick=()=>pedir('/norte?borrar=1');
$('bInv').onclick=()=>pedir('/invertir');
$('bIniciar').onclick=()=>{
 const h=norm(+$('hdg').value||0),d=+$('dst').value||0;
 if(d<10||d>2000){alert('La distancia debe estar entre 10 y 2000 cm');return;}
 pedir(`/mision?h=${h}&d=${d}&v=${$('vAuto').value}`);
};
$('bGirar').onclick=()=>pedir('/girar?h='+norm(+$('hdg').value||0));
document.querySelectorAll('[data-h]').forEach(b=>b.onclick=()=>{$('hdg').value=b.dataset.h;if(J)mostrar(J);});
$('bPrueba').onclick=()=>{if(confirm('El robot avanzará 3 s en línea recta. Deje espacio libre.'))pedir('/pruebadist?v='+$('vAuto').value);};
$('bCalDist').onclick=()=>pedir('/caldist?cm='+$('cmReal').value);

/* ---------- mostrar estado ---------- */
function mostrar(j){
 J=j;
 document.querySelectorAll('.lamp[data-m]').forEach(l=>l.classList.toggle('on',l.dataset.m===j.modo));
 $('mot').textContent=j.vi+' / '+j.vd;
 $('fase').textContent=j.fase;
 $('prog').textContent=j.prog.toFixed(0)+' / '+(j.modo==='AUTONOMO'||j.prog>0?j.dobj.toFixed(0):'0')+' cm';
 $('progBar').style.width=(j.dobj>0?Math.min(100,j.prog/j.dobj*100):0)+'%';
 $('calBar').style.width=j.cal_prog+'%';

 const tipoMag=['No encontrado','QMC5883L','HMC5883L'][j.mag];
 $('magTipo').textContent=tipoMag+(j.mag?(j.cal?' · calibrado':' · SIN CALIBRAR'):(j.est?' · RUMBO ESTIMADO':''));
 $('crudo').textContent=j.mx+' / '+j.my+' / '+j.mz;
 $('rMag').textContent=j.mag?j.crudo.toFixed(1)+'°':'-';
 $('acel').textContent=j.imu?`${j.ax.toFixed(2)} / ${j.ay.toFixed(2)} / ${j.az.toFixed(2)}`:'no detectado';
 $('gir').textContent=j.imu?`${j.gx.toFixed(1)} / ${j.gy.toFixed(1)} / ${j.gz.toFixed(1)}`:'-';
 $('fus').textContent=!j.imu?'-':(j.giro?'activa':'pendiente');
 $('dist').textContent=j.dist<0?'fuera de rango':j.dist.toFixed(1)+' cm'+(j.obst?' · OBSTÁCULO':'');
 $('dist').className=j.obst?'rojo':'';
 $('distBar').style.width=(j.dist<0?100:Math.min(100,j.dist/2))+'%';
 $('distBar').style.background=j.obst?'var(--rojo)':'var(--azul)';
 $('rpm').textContent=j.rpmi+' / '+j.rpmd;
 $('odo').textContent=j.odo.toFixed(1)+' cm'+(j.enc?'':' (sin enc.)');
 $('cmps').textContent=j.cmps.toFixed(1)+' cm/s';
 $('fenc').textContent=j.fenc.toFixed(2)+' / '+j.pcm.toFixed(0)+' cm';
 $('ev').innerHTML=j.ev.slice().reverse().map(t=>`<li>${t}</li>`).join('')||'<li>Sin eventos</li>';

 const auto=(j.modo==='AUTONOMO'||j.modo==='GIRO');
 const obj=auto?j.obj:norm(+$('hdg').value||0);
 const act=(j.mag||j.est)?j.rumbo:null;
 $('nAct').textContent=act===null?'---°':act.toFixed(0)+'°';
 $('nObj').textContent=obj.toFixed(0)+'°';
 const e=act===null?null:dif(obj,act);
 $('nErr').textContent=e===null?'---°':(e>0?'+':'')+e.toFixed(0)+'°';
 $('nErr').className=e!==null&&Math.abs(e)>15?'rojo':'';

 LOG.push([j.t/1000,j.modo,j.fase,j.rumbo,j.crudo,obj,e===null?'':e,j.dist,j.vi,j.vd,j.prog,j.ax,j.ay,j.az,j.gx,j.gy,j.gz,j.rpmi,j.rpmd]);
 if(LOG.length>30000)LOG.shift();
 HIST.push([j.t/1000,act,obj]);
 while(HIST.length&&HIST[HIST.length-1][0]-HIST[0][0]>30)HIST.shift();
 $('nLog').textContent=LOG.length+' muestras';
 dibujarBrujula(act,obj);
 dibujarGrafica();
}

/* ---------- carta de rumbo: actual (azul) y deseado (naranja) ---------- */
const cv=$('brujula'),cx=cv.getContext('2d');
const rad=g=>(g-90)*Math.PI/180;
function dibujarBrujula(act,obj){
 const W=cv.width,c=W/2,R=c-8;
 cx.clearRect(0,0,W,W);
 // disco y anillos
 cx.fillStyle=CARA;cx.beginPath();cx.arc(c,c,R,0,7);cx.fill();
 cx.strokeStyle=TINTA;cx.lineWidth=4;cx.beginPath();cx.arc(c,c,R,0,7);cx.stroke();
 cx.lineWidth=1.5;cx.beginPath();cx.arc(c,c,R-30,0,7);cx.stroke();
 cx.lineWidth=1;cx.beginPath();cx.arc(c,c,R-98,0,7);cx.stroke();
 // marcas cada 5 grados
 for(let g=0;g<360;g+=5){
  const l=g%30===0?24:(g%10===0?15:8);
  cx.strokeStyle=TINTA;cx.lineWidth=g%30===0?2.5:1;
  cx.beginPath();cx.moveTo(c+Math.cos(rad(g))*R,c+Math.sin(rad(g))*R);
  cx.lineTo(c+Math.cos(rad(g))*(R-l),c+Math.sin(rad(g))*(R-l));cx.stroke();
 }
 // numeros cada 30 grados
 cx.font='13px Consolas,monospace';cx.textAlign='center';cx.textBaseline='middle';cx.fillStyle=TINTA;
 for(let g=30;g<360;g+=30){if(g%90===0)continue;
  cx.fillText(g,c+Math.cos(rad(g))*(R-44),c+Math.sin(rad(g))*(R-44));}
 // puntos cardinales
 cx.font='bold 26px Georgia,"Times New Roman",serif';
 [['N',0,NARANJA],['E',90,TINTA],['S',180,TINTA],['O',270,TINTA]].forEach(([t,g,col])=>{
  cx.fillStyle=col;cx.fillText(t,c+Math.cos(rad(g))*(R-50),c+Math.sin(rad(g))*(R-50));
 });
 // cuña de error entre actual y deseado
 if(act!==null&&obj!==null){
  const e=dif(obj,act);
  cx.fillStyle='rgba(212,80,27,.28)';cx.strokeStyle=NARANJA;cx.lineWidth=1.5;
  cx.beginPath();cx.moveTo(c,c);cx.arc(c,c,R-100,rad(act),rad(act+e),e<0);cx.closePath();cx.fill();cx.stroke();
 }
 // direccion deseada: trazo discontinuo y marca sobre el anillo
 if(obj!==null){
  cx.save();cx.translate(c,c);cx.rotate(obj*Math.PI/180);
  cx.strokeStyle=NARANJA;cx.lineWidth=2.5;cx.setLineDash([9,6]);
  cx.beginPath();cx.moveTo(0,-(R-100));cx.lineTo(0,-(R-32));cx.stroke();cx.setLineDash([]);
  cx.fillStyle=NARANJA;cx.strokeStyle=TINTA;cx.lineWidth=1.5;
  cx.beginPath();cx.moveTo(0,-R+2);cx.lineTo(12,-R+26);cx.lineTo(-12,-R+26);cx.closePath();cx.fill();cx.stroke();
  cx.restore();
 }
 // direccion actual: aguja
 if(act!==null){
  cx.save();cx.translate(c,c);cx.rotate(act*Math.PI/180);
  cx.fillStyle=AZUL;cx.strokeStyle=TINTA;cx.lineWidth=2;
  cx.beginPath();cx.moveTo(0,-(R-100));cx.lineTo(10,0);cx.lineTo(0,18);cx.lineTo(-10,0);cx.closePath();cx.fill();cx.stroke();
  cx.restore();
 }
 cx.fillStyle=CARA;cx.strokeStyle=TINTA;cx.lineWidth=2.5;cx.beginPath();cx.arc(c,c,7,0,7);cx.fill();cx.stroke();
}
cv.addEventListener('pointerdown',e=>{
 const r=cv.getBoundingClientRect(),s=cv.width/r.width;
 const x=(e.clientX-r.left)*s-cv.width/2,y=(e.clientY-r.top)*s-cv.height/2;
 $('hdg').value=Math.round(norm(Math.atan2(x,-y)*180/Math.PI));
 if(J)mostrar(J);else dibujarBrujula(null,+$('hdg').value);
});
$('hdg').addEventListener('input',()=>{if(J)mostrar(J);else dibujarBrujula(null,norm(+$('hdg').value||0));});
dibujarBrujula(null,0);

/* ---------- grafica: ultimos 30 s ---------- */
const gc=$('grafica'),gx=gc.getContext('2d');
function dibujarGrafica(){
 const W=gc.width,H=gc.height,ml=40,mb=22,mt=14;
 gx.clearRect(0,0,W,H);
 gx.font='12px Consolas,monospace';gx.fillStyle=TINTA;gx.textBaseline='middle';
 const Y=a=>H-mb-(a/360)*(H-mb-mt);
 for(let g=0;g<=360;g+=45){
  gx.strokeStyle=g%90===0?'rgba(26,26,23,.35)':'rgba(26,26,23,.12)';gx.lineWidth=1;
  gx.beginPath();gx.moveTo(ml,Y(g));gx.lineTo(W-6,Y(g));gx.stroke();
  if(g%90===0)gx.fillText(g+'°',4,Y(g));
 }
 if(HIST.length<2)return;
 const t0=HIST[0][0],t1=HIST[HIST.length-1][0],span=Math.max(10,t1-t0);
 const X=t=>ml+(t-t0)/span*(W-ml-6);
 gx.textBaseline='alphabetic';
 for(let s=0;s<=span;s+=5){const x=X(t0+s);gx.strokeStyle='rgba(26,26,23,.12)';gx.beginPath();gx.moveTo(x,mt);gx.lineTo(x,H-mb);gx.stroke();gx.fillText('-'+Math.round(span-s)+' s',x-14,H-5);}
 [[2,NARANJA,2],[1,AZUL,2.5]].forEach(([k,col,lw])=>{
  gx.strokeStyle=col;gx.lineWidth=lw;gx.beginPath();let prev=null;
  HIST.forEach(p=>{
   if(p[k]===null){prev=null;return;}
   if(prev===null||Math.abs(p[k]-prev)>180)gx.moveTo(X(p[0]),Y(p[k]));else gx.lineTo(X(p[0]),Y(p[k]));
   prev=p[k];
  });
  gx.stroke();
 });
 gx.fillStyle=AZUL;gx.fillRect(ml+8,2,14,5);gx.fillStyle=TINTA;gx.fillText('actual',ml+26,9);
 gx.fillStyle=NARANJA;gx.fillRect(ml+84,2,14,5);gx.fillStyle=TINTA;gx.fillText('deseado',ml+102,9);
}
dibujarGrafica();

/* ---------- registro CSV ---------- */
$('bCsv').onclick=()=>{
 const enc='t_s,modo,fase,rumbo_deg,rumbo_mag_deg,objetivo_deg,error_deg,dist_cm,motor_izq,motor_der,progreso_cm,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,rpm_izq,rpm_der\n';
 const filas=LOG.map(f=>f.map(v=>typeof v==='number'?(+v.toFixed(2)):v).join(',')).join('\n');
 const a=document.createElement('a');
 a.href=URL.createObjectURL(new Blob([enc+filas],{type:'text/csv'}));
 a.download='registro_robot.csv';a.click();
};
$('bLimpiar').onclick=()=>{LOG=[];HIST=[];$('nLog').textContent='0 muestras';dibujarGrafica();};
</script></body></html>)rawliteral";
