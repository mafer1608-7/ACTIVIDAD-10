// Pagina web de control servida por el ESP32 (sin internet: todo va incluido aqui)
#pragma once

const char PAGINA_WEB[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Robot movil</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--borde:#334155;--txt:#e2e8f0;--sub:#94a3b8;--acento:#38bdf8;--ok:#22c55e;--mal:#ef4444;--aviso:#f59e0b}
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;touch-action:manipulation}
body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,Segoe UI,Roboto,sans-serif}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--borde)}
h1{font-size:18px;margin:0}
#con{font-size:13px;padding:4px 10px;border-radius:99px;background:var(--mal)}
main{display:grid;gap:12px;padding:12px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));max-width:1100px;margin:auto}
.card{background:var(--card);border:1px solid var(--borde);border-radius:12px;padding:14px}
.card h2{font-size:14px;margin:0 0 10px;color:var(--sub);text-transform:uppercase;letter-spacing:.05em}
.pad{display:grid;grid-template-columns:repeat(3,80px);grid-template-rows:repeat(3,80px);gap:8px;justify-content:center}
.pad button{font-size:28px}
button{background:#334155;color:var(--txt);border:1px solid #475569;border-radius:10px;font-size:15px;padding:10px;cursor:pointer}
button:active,button.on{background:var(--acento);color:#0f172a}
#bStop{background:var(--mal);border-color:var(--mal)}
.fila{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px}
.dato{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--borde);font-size:15px}
.dato b{font-variant-numeric:tabular-nums}
#rumbo{font-size:40px;font-weight:700;text-align:center;font-variant-numeric:tabular-nums}
#card{text-align:center;color:var(--sub);margin-bottom:6px}
canvas{display:block;margin:auto;max-width:100%}
input[type=number]{width:80px;padding:9px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:var(--txt);font-size:15px}
input[type=range]{flex:1}
#msg{margin-top:10px;padding:8px;border-radius:8px;background:#0f172a;font-size:14px;min-height:20px}
.barra{height:8px;background:#0f172a;border-radius:4px;overflow:hidden;margin-top:6px}
.barra div{height:100%;width:0;background:var(--acento);transition:width .2s}
small{color:var(--sub)}
</style></head><body>
<header><h1>🤖 Robot móvil – Control</h1><span id="con">Sin conexión</span></header>
<main>
 <section class="card"><h2>Modo manual</h2>
  <div class="pad">
   <span></span><button data-d="w">▲</button><span></span>
   <button data-d="a">◀</button><button id="bStop">■</button><button data-d="d">▶</button>
   <span></span><button data-d="s">▼</button><span></span>
  </div>
  <div class="fila"><span>Velocidad</span><input id="vel" type="range" min="30" max="100" value="70"><b id="velTxt">70%</b></div>
  <small>Teclado: W A S D o flechas · Espacio = parar</small>
  <div class="dato"><span>Motor izq / der</span><b id="mot">0 / 0</b></div>
  <div class="dato"><span>Modo</span><b id="modo">-</b></div>
 </section>

 <section class="card"><h2>Orientación (norte)</h2>
  <div id="rumbo">---°</div><div id="card">-</div>
  <canvas id="brujula" width="260" height="260"></canvas>
  <div class="dato"><span>Magnetómetro</span><b id="magTipo">-</b></div>
  <div class="dato"><span>Crudo X / Y / Z</span><b id="crudo">-</b></div>
 </section>

 <section class="card"><h2>Sensores</h2>
  <div class="dato"><span>Distancia frontal</span><b id="dist">-</b></div>
  <div class="barra"><div id="distBar"></div></div>
  <div class="dato"><span>RPM izq / der</span><b id="rpm">-</b></div>
  <div class="dato"><span>Odometría</span><b id="odo">-</b></div>
  <div class="dato"><span>Batería</span><b id="bat">-</b></div>
 </section>

 <section class="card"><h2>Calibración y modo autónomo (base)</h2>
  <div class="fila"><button id="bCal">Calibrar brújula (20 s girando)</button></div>
  <div class="barra"><div id="calBar"></div></div>
  <div class="fila"><button id="bNorte">El robot mira al norte → fijar 0°</button><button id="bBorrar">Borrar ajuste</button></div>
  <div class="fila"><span>Girar a rumbo</span><input id="obj" type="number" min="0" max="359" value="0"><button id="bGirar">Girar</button></div>
  <div class="fila"><button data-h="0">N</button><button data-h="90">E</button><button data-h="180">S</button><button data-h="270">O</button></div>
  <div id="msg"></div>
 </section>
</main>
<script>
const $=id=>document.getElementById(id);
const teclas=new Set();
let ultimoOk=0,ocupado=false,rumboAct=null;

const mapa={w:'w',arrowup:'w',s:'s',arrowdown:'s',a:'a',arrowleft:'a',d:'d',arrowright:'d'};
addEventListener('keydown',e=>{const k=mapa[e.key.toLowerCase()];if(k){teclas.add(k);e.preventDefault();marcar();}if(e.key===' '){parar();e.preventDefault();}});
addEventListener('keyup',e=>{const k=mapa[e.key.toLowerCase()];if(k){teclas.delete(k);marcar();}});
addEventListener('blur',()=>{teclas.clear();marcar();});
document.querySelectorAll('[data-d]').forEach(b=>{
 const d=b.dataset.d;
 b.addEventListener('pointerdown',e=>{teclas.add(d);b.setPointerCapture(e.pointerId);marcar();});
 ['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,()=>{teclas.delete(d);marcar();}));
});
function marcar(){document.querySelectorAll('[data-d]').forEach(b=>b.classList.toggle('on',teclas.has(b.dataset.d)));}
$('vel').oninput=()=>$('velTxt').textContent=$('vel').value+'%';

function comando(){
 const v=(teclas.has('w')?1:0)-(teclas.has('s')?1:0);
 let w=(teclas.has('d')?1:0)-(teclas.has('a')?1:0);
 if(v!==0&&w!==0)w*=0.5;               // curva suave al combinar teclas
 const s=+$('vel').value;
 const lim=x=>Math.round(Math.max(-1,Math.min(1,x))*s);
 return [lim(v+w),lim(v-w)];
}

async function pedir(url){
 try{
  const r=await fetch(url,{cache:'no-store'});
  const j=await r.json();ultimoOk=Date.now();mostrar(j);
 }catch(e){}
}
async function ciclo(){
 if(!ocupado){ocupado=true;const [l,r]=comando();await pedir(`/ctrl?l=${l}&r=${r}`);ocupado=false;}
 const ok=Date.now()-ultimoOk<1000;
 $('con').textContent=ok?'Conectado':'Sin conexión';$('con').style.background=ok?'var(--ok)':'var(--mal)';
}
setInterval(ciclo,100);

function parar(){teclas.clear();marcar();pedir('/stop');}
$('bStop').onclick=parar;
$('bCal').onclick=()=>{if(confirm('El robot girará solo durante 20 s. ¿Está en el piso y con espacio libre?'))pedir('/calibrar');};
$('bNorte').onclick=()=>pedir('/norte');
$('bBorrar').onclick=()=>pedir('/norte?borrar=1');
$('bGirar').onclick=()=>pedir('/girar?h='+$('obj').value);
document.querySelectorAll('[data-h]').forEach(b=>b.onclick=()=>pedir('/girar?h='+b.dataset.h));

const nombres=['N','NE','E','SE','S','SO','O','NO'];
function mostrar(j){
 $('mot').textContent=j.vi+' / '+j.vd;
 $('modo').textContent=j.modo;
 $('magTipo').textContent=['No encontrado','QMC5883L','HMC5883L'][j.mag]+(j.mag?(j.cal?' · calibrado':' · SIN calibrar'):'');
 $('crudo').textContent=j.mx+' / '+j.my+' / '+j.mz;
 if(j.mag){rumboAct=j.rumbo;$('rumbo').textContent=j.rumbo.toFixed(0)+'°';$('card').textContent=nombres[Math.round(j.rumbo/45)%8];}
 else{rumboAct=null;$('rumbo').textContent='---°';$('card').textContent='conecte el magnetómetro';}
 $('dist').textContent=j.dist<0?'fuera de rango':j.dist.toFixed(1)+' cm'+(j.obst?' ⚠ obstáculo':'');
 $('distBar').style.width=(j.dist<0?100:Math.min(100,j.dist/2))+'%';
 $('distBar').style.background=j.obst?'var(--mal)':(j.dist>0&&j.dist<40?'var(--aviso)':'var(--acento)');
 $('rpm').textContent=j.rpmi+' / '+j.rpmd;
 $('odo').textContent=j.odo.toFixed(1)+' cm';
 $('bat').textContent=j.vbat>0?j.vbat.toFixed(2)+' V':'sin divisor';
 $('calBar').style.width=j.prog+'%';
 $('msg').textContent=j.msg;
 dibujar();
}

const cv=$('brujula'),cx=cv.getContext('2d');
function dibujar(){
 const W=cv.width,c=W/2,R=c-14;
 cx.clearRect(0,0,W,W);
 cx.strokeStyle='#475569';cx.lineWidth=3;cx.beginPath();cx.arc(c,c,R,0,7);cx.stroke();
 for(let g=0;g<360;g+=10){
  const a=(g-90)*Math.PI/180,l=g%90?6:14;
  cx.strokeStyle=g%90?'#64748b':'#e2e8f0';cx.lineWidth=g%90?1:2;cx.beginPath();
  cx.moveTo(c+Math.cos(a)*R,c+Math.sin(a)*R);cx.lineTo(c+Math.cos(a)*(R-l),c+Math.sin(a)*(R-l));cx.stroke();
 }
 cx.font='bold 18px system-ui';cx.textAlign='center';cx.textBaseline='middle';
 [['N',0,'#ef4444'],['E',90,'#e2e8f0'],['S',180,'#e2e8f0'],['O',270,'#e2e8f0']].forEach(([t,g,col])=>{
  const a=(g-90)*Math.PI/180;cx.fillStyle=col;cx.fillText(t,c+Math.cos(a)*(R-30),c+Math.sin(a)*(R-30));
 });
 if(rumboAct===null)return;
 // robot visto desde arriba, girado segun el rumbo
 cx.save();cx.translate(c,c);cx.rotate(rumboAct*Math.PI/180);
 cx.fillStyle='#38bdf8';cx.beginPath();cx.moveTo(0,-R+44);cx.lineTo(16,10);cx.lineTo(0,0);cx.lineTo(-16,10);cx.closePath();cx.fill();
 cx.strokeStyle='#38bdf8';cx.lineWidth=2;cx.beginPath();cx.arc(0,0,26,0,7);cx.stroke();
 cx.restore();
}
dibujar();
</script></body></html>)rawliteral";
