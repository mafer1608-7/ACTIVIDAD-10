// Pagina web de control (modo manual), servida por el ESP32. No necesita internet.
#pragma once

const char PAGINA_WEB[] PROGMEM = R"rawliteral(<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Robot movil</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--borde:#334155;--txt:#e2e8f0;--sub:#94a3b8;--acento:#38bdf8;--ok:#22c55e;--mal:#ef4444}
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;touch-action:manipulation}
body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,Segoe UI,Roboto,sans-serif}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--borde)}
h1{font-size:18px;margin:0}
#con{font-size:13px;padding:4px 10px;border-radius:99px;background:var(--mal)}
main{padding:12px;max-width:420px;margin:auto}
.card{background:var(--card);border:1px solid var(--borde);border-radius:12px;padding:14px}
.card h2{font-size:14px;margin:0 0 10px;color:var(--sub);text-transform:uppercase;letter-spacing:.05em}
.pad{display:grid;grid-template-columns:repeat(3,80px);grid-template-rows:repeat(3,80px);gap:8px;justify-content:center}
.pad button{font-size:28px}
button{background:#334155;color:var(--txt);border:1px solid #475569;border-radius:10px;font-size:15px;padding:10px;cursor:pointer}
button:active,button.on{background:var(--acento);color:#0f172a}
#bStop{background:var(--mal);border-color:var(--mal)}
.fila{display:flex;gap:8px;align-items:center;margin-top:12px}
.dato{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--borde);font-size:15px}
input[type=range]{flex:1}
small{color:var(--sub);display:block;margin-top:8px}
</style></head><body>
<header><h1>🤖 Robot móvil – Modo manual</h1><span id="con">Sin conexión</span></header>
<main>
 <section class="card"><h2>Control</h2>
  <div class="pad">
   <span></span><button data-d="w">▲</button><span></span>
   <button data-d="a">◀</button><button id="bStop">■</button><button data-d="d">▶</button>
   <span></span><button data-d="s">▼</button><span></span>
  </div>
  <div class="fila"><span>Velocidad</span><input id="vel" type="range" min="30" max="100" value="70"><b id="velTxt">70%</b></div>
  <small>Teclado: W A S D o flechas · Espacio = parar</small>
  <div class="dato"><span>Motor izq / der</span><b id="mot">0 / 0</b></div>
 </section>
</main>
<script>
const $=id=>document.getElementById(id);
const teclas=new Set();
let ultimoOk=0,ocupado=false;

// ---- teclado ----
const mapa={w:'w',arrowup:'w',s:'s',arrowdown:'s',a:'a',arrowleft:'a',d:'d',arrowright:'d'};
addEventListener('keydown',e=>{const k=mapa[e.key.toLowerCase()];if(k){teclas.add(k);e.preventDefault();marcar();}if(e.key===' '){parar();e.preventDefault();}});
addEventListener('keyup',e=>{const k=mapa[e.key.toLowerCase()];if(k){teclas.delete(k);marcar();}});
addEventListener('blur',()=>{teclas.clear();marcar();});

// ---- botones en pantalla (mouse o dedo): mientras se mantienen presionados ----
document.querySelectorAll('[data-d]').forEach(b=>{
 const d=b.dataset.d;
 b.addEventListener('pointerdown',e=>{teclas.add(d);b.setPointerCapture(e.pointerId);marcar();});
 ['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,()=>{teclas.delete(d);marcar();}));
});
function marcar(){document.querySelectorAll('[data-d]').forEach(b=>b.classList.toggle('on',teclas.has(b.dataset.d)));}
$('vel').oninput=()=>$('velTxt').textContent=$('vel').value+'%';

// ---- de las teclas presionadas a velocidad de cada motor ----
function comando(){
 const v=(teclas.has('w')?1:0)-(teclas.has('s')?1:0);   // adelante / atras
 let w=(teclas.has('d')?1:0)-(teclas.has('a')?1:0);     // derecha / izquierda
 if(v!==0&&w!==0)w*=0.5;                                // curva suave al combinar teclas
 const s=+$('vel').value;
 const lim=x=>Math.round(Math.max(-1,Math.min(1,x))*s);
 return [lim(v+w),lim(v-w)];                            // [motor izq, motor der]
}

// ---- comunicacion con el robot ----
async function pedir(url){
 try{
  const r=await fetch(url,{cache:'no-store'});
  const j=await r.json();ultimoOk=Date.now();
  $('mot').textContent=j.vi+' / '+j.vd;
 }catch(e){}
}
async function ciclo(){
 if(!ocupado){ocupado=true;const [l,r]=comando();await pedir(`/ctrl?l=${l}&r=${r}`);ocupado=false;}
 const ok=Date.now()-ultimoOk<1000;
 $('con').textContent=ok?'Conectado':'Sin conexión';
 $('con').style.background=ok?'var(--ok)':'var(--mal)';
}
setInterval(ciclo,100);   // 10 ordenes por segundo

function parar(){teclas.clear();marcar();pedir('/stop');}
$('bStop').onclick=parar;
</script></body></html>)rawliteral";
