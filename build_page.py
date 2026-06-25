#!/usr/bin/env python3
"""Build index.html from ghin_data.json."""
import json, os
from datetime import date

DIR = "/Users/nathan.lee/pinehurst"

with open(f"{DIR}/ghin_data.json") as f:
    DATA = json.load(f)

ORDER = ["7866286", "7562830", "11367668", "11634995", "10460818", "3031631"]
TODAY = date.today().strftime("%b %Y")

def js(v):
    return json.dumps(v, separators=(",", ":"))

golfers_js = "{\n"
for ghin in ORDER:
    g = DATA[ghin]
    current = float(g["current"]) if g["current"] else 0
    low = float(g["low"]) if g["low"] else 0
    golfers_js += f'  "{ghin}":{{'
    golfers_js += f'name:{js(g["name"])},club:{js(g["club"])},current:{current},low:{low},color:{js(g["color"])},'
    golfers_js += f'revs:{js(g["revs"])},'
    golfers_js += f'rounds:{js(g["rounds"])}'
    golfers_js += '},\n'
golfers_js += "}"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Handicap History</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<style>
:root{
  --bg:#0d1a10;--surface:#132016;--surface2:#1a2e1e;--green-dark:#0a3318;
  --text:#f0f7f2;--dim:#7a9b82;--radius:16px;
  --safe-top:env(safe-area-inset-top,0px);--safe-bot:env(safe-area-inset-bottom,0px);
  --c1:#d4af37;--c2:#f0f7f2;--c3:#6dbf82;--c4:#a8d5b5;--c5:#e8c84a;--c6:#b5d99c;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display',sans-serif;background:var(--bg);color:var(--text);min-height:100dvh;padding-top:var(--safe-top);padding-bottom:calc(var(--safe-bot)+24px);-webkit-font-smoothing:antialiased}
header{background:linear-gradient(160deg,#0a3318 0%,#0d1a10 100%);padding:18px 16px 14px;border-bottom:1px solid rgba(212,175,55,0.15)}
.header-row{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.logo{width:34px;height:34px;background:var(--c1);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:900;color:#0a3318;flex-shrink:0;letter-spacing:-0.5px}
.header-title{font-size:18px;font-weight:700;letter-spacing:-0.3px}
.header-sub{font-size:12px;color:var(--dim);margin-top:1px}
.pills{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.pill{display:flex;align-items:center;gap:9px;padding:9px 12px;border-radius:12px;border:1.5px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);color:var(--dim);font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:all .18s;text-align:left}
.pill .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;opacity:.35;transition:opacity .18s}
.pill .pname{font-size:12px;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
.pill .phi{font-size:20px;font-weight:800;line-height:1;flex-shrink:0}
.pill.on{background:rgba(255,255,255,0.05)}
.pill.on .dot{opacity:1}
.content{padding:14px;display:flex;flex-direction:column;gap:14px}
.range-tabs{display:flex;background:var(--surface);border-radius:10px;padding:3px;gap:2px}
.rtab{flex:1;text-align:center;padding:8px 4px;border-radius:7px;font-size:13px;font-weight:600;color:var(--dim);cursor:pointer;border:none;background:transparent;font-family:inherit;transition:all .15s}
.rtab.on{background:#0a3318;color:#d4af37}
.chart-card{background:var(--surface);border-radius:var(--radius);padding:16px}
.chart-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.chart-label{font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.06em}
.chart-note{font-size:11px;color:var(--dim);margin-top:2px}
.chart-wrap{position:relative;height:240px}
.section-label{font-size:12px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat{background:var(--surface);border-radius:12px;padding:12px 10px;text-align:center}
.stat-val{font-size:22px;font-weight:800;line-height:1}
.stat-lbl{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.05em;margin-top:3px}
.rounds-tabs{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px;margin-bottom:10px}
.rounds-tabs::-webkit-scrollbar{display:none}
.rtab2{padding:7px 14px;border-radius:20px;border:1.5px solid rgba(255,255,255,0.1);background:transparent;font-family:inherit;font-size:12px;font-weight:700;color:var(--dim);cursor:pointer;white-space:nowrap;transition:all .15s}
.rtab2.on{border-color:var(--c);color:var(--c);background:rgba(255,255,255,.04)}
.rounds-list{display:flex;flex-direction:column;gap:6px}
.round{display:flex;align-items:center;gap:10px;background:var(--surface);border-radius:11px;padding:10px 12px}
.round-idx{font-size:11px;color:var(--dim);min-width:18px;text-align:center;font-weight:600}
.round-date{font-size:11px;color:var(--dim);min-width:60px}
.round-course{flex:1;font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.round-holes{font-size:10px;color:var(--dim);background:var(--surface2);border-radius:4px;padding:2px 5px;flex-shrink:0}
.round-score{font-size:15px;font-weight:700;min-width:32px;text-align:right;flex-shrink:0}
#tooltip{position:fixed;background:var(--surface2);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px 14px;pointer-events:none;display:none;box-shadow:0 8px 32px rgba(0,0,0,.6);z-index:999;transform:translateX(-50%);white-space:nowrap}
.tt-date{font-size:11px;color:var(--dim);margin-bottom:2px}
.tt-hi{font-size:26px;font-weight:800;line-height:1}
.tt-name{font-size:12px;color:var(--dim);margin-top:3px}
</style>
</head>
<body>
<header>
  <div class="header-row">
    <div class="logo">HI</div>
    <div><div class="header-title">Handicap History</div><div class="header-sub">SCGA &middot; GHIN &middot; Updated __TODAY__</div></div>
  </div>
  <div class="pills" id="pills"></div>
</header>
<div class="content">
  <div class="range-tabs">
    <button class="rtab" data-r="1">1Y</button>
    <button class="rtab" data-r="2">2Y</button>
    <button class="rtab" data-r="5">5Y</button>
    <button class="rtab on" data-r="all">All</button>
  </div>
  <div class="chart-card">
    <div class="chart-top">
      <div>
        <div class="chart-label">Handicap Index over time</div>
        <div class="chart-note">Lower is better &nbsp;&middot;&nbsp; <span style="border-bottom:2px solid var(--dim)">Revisions</span> &nbsp;<span style="border-bottom:2px dashed var(--dim)">Last 20 rounds</span></div>
      </div>
    </div>
    <div class="chart-wrap"><canvas id="hiChart"></canvas></div>
  </div>
  <div>
    <div class="section-label">Stats (selected range)</div>
    <div class="stats-grid" id="statsGrid"></div>
  </div>
  <div>
    <div class="section-label">Recent Rounds</div>
    <div class="rounds-tabs" id="roundsTabs"></div>
    <div class="rounds-list" id="roundsList"></div>
  </div>
</div>
<div id="tooltip">
  <div class="tt-date" id="ttDate"></div>
  <div class="tt-hi" id="ttHI"></div>
  <div class="tt-name" id="ttName"></div>
</div>
<script>
const G=__GOLFERS__;
const ORDER=[__ORDER__];
const NOW=new Date('__TODAY_ISO__');
let active=new Set(ORDER),range='all',activeRounds=ORDER[0],chart=null;
function cutoff(r){if(r==='all')return new Date('2000-01-01');const d=new Date(NOW);d.setFullYear(d.getFullYear()-parseInt(r));return d;}
function fmtDate(s){return new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}
function fmtShort(s){return new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'})}
function renderPills(){
  const c=document.getElementById('pills');
  c.innerHTML=ORDER.map(g=>{const d=G[g],on=active.has(g);return`<button class="pill${on?' on':''}" data-g="${g}" style="--c:${d.color}"><div class="dot" style="background:${d.color}"></div><div class="pname" style="color:${on?d.color:'var(--dim)'}">${d.name}</div><div class="phi" style="color:${on?d.color:'var(--dim)'}">${d.current}</div></button>`;}).join('');
  document.querySelectorAll('.pill').forEach(p=>p.addEventListener('click',()=>{const g=p.dataset.g;if(active.has(g)&&active.size>1){active.delete(g)}else{active.add(g)}renderPills();buildChart();renderStats();renderRoundsTabs();}));
}
function renderStats(){
  const el=document.getElementById('statsGrid');const cards=[];
  active.forEach(g=>{const d=G[g];const filtered=d.revs.filter(r=>new Date(r.date)>=cutoff(range));if(!filtered.length)return;const his=filtered.map(r=>r.hi);const mx=Math.max(...his);const delta=(filtered[filtered.length-1].hi-filtered[0].hi).toFixed(1);const isDown=parseFloat(delta)<0;cards.push(`<div class="stat" style="border-left:3px solid ${d.color}"><div class="stat-val" style="color:${d.color}">${d.current}</div><div class="stat-lbl">${d.name.split(' ')[0]}</div><div style="font-size:11px;color:var(--dim);margin-top:4px">Low ${d.low} &middot; Hi ${mx}</div><div style="font-size:12px;font-weight:700;margin-top:3px;color:${isDown?'#d4af37':'#c0392b'}">${isDown?'▼':'▲'} ${Math.abs(delta)}</div></div>`);});
  el.style.gridTemplateColumns=`repeat(${Math.min(cards.length,3)},1fr)`;el.innerHTML=cards.join('');
}
function buildChart(){
  const ctx=document.getElementById('hiChart').getContext('2d');const datasets=[];
  ORDER.forEach(g=>{
    if(!active.has(g))return;const d=G[g];
    const filtered=d.revs.filter(r=>new Date(r.date)>=cutoff(range));
    const pts=filtered.map(r=>({x:r.date,y:r.hi,name:d.name,series:'revisions'}));
    const grad=ctx.createLinearGradient(0,0,0,240);grad.addColorStop(0,d.color+'22');grad.addColorStop(1,d.color+'00');
    datasets.push({label:d.name,data:pts,borderColor:d.color,backgroundColor:grad,borderWidth:2.5,fill:true,tension:0.3,pointRadius:filtered.length>60?0:3,pointHoverRadius:7,pointBackgroundColor:d.color,pointBorderColor:'#162019',pointBorderWidth:2,pointHoverBackgroundColor:'#fff',pointHoverBorderColor:d.color,pointHoverBorderWidth:2});
    const rpts=d.rounds.map(r=>({x:r.date,y:r.hi,name:d.name,course:r.course,score:r.score,series:'rounds'}));
    datasets.push({label:d.name+' (rounds)',data:rpts,borderColor:d.color,backgroundColor:'transparent',borderWidth:1.5,borderDash:[5,4],fill:false,tension:0.3,pointRadius:3,pointHoverRadius:6,pointBackgroundColor:d.color+'bb',pointBorderColor:'#162019',pointBorderWidth:1,pointHoverBackgroundColor:'#fff',pointHoverBorderColor:d.color,pointHoverBorderWidth:2});
  });
  if(chart)chart.destroy();
  chart=new Chart(ctx,{type:'line',data:{datasets},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'nearest',intersect:false,axis:'x'},plugins:{legend:{display:false},tooltip:{enabled:false,external:extTT}},scales:{x:{type:'time',time:{unit:range==='1'?'month':range==='2'?'month':'year',tooltipFormat:'MMM d, yyyy'},grid:{color:'rgba(255,255,255,0.04)'},ticks:{color:'#7a9b82',font:{size:11},maxTicksLimit:6},border:{display:false}},y:{reverse:true,grid:{color:'rgba(255,255,255,0.06)'},ticks:{color:'#7a9b82',font:{size:11},maxTicksLimit:6,callback:v=>v.toFixed(1)},border:{display:false}}}}});
}
const tt=document.getElementById('tooltip'),ttD=document.getElementById('ttDate'),ttH=document.getElementById('ttHI'),ttN=document.getElementById('ttName');
function extTT(ctx){
  const {tooltip}=ctx;if(!tooltip.opacity||!tooltip.dataPoints?.length){tt.style.display='none';return}
  const dp=tooltip.dataPoints[0];const raw=dp.raw;const label=dp.dataset.label;
  const ghin=Object.keys(G).find(k=>G[k].name===label||G[k].name+' (rounds)'===label);
  const col=ghin?G[ghin].color:'#fff';
  ttD.textContent=fmtDate(raw.x);ttH.textContent=raw.y.toFixed(1);ttH.style.color=col;
  ttN.textContent=raw.series==='rounds'&&raw.course?`${raw.course} · ${raw.score}`:label.replace(' (rounds)','')+' · Revision';
  tt.style.display='block';
  const rect=ctx.chart.canvas.getBoundingClientRect();
  tt.style.left=(rect.left+tooltip.caretX)+'px';tt.style.top=Math.max(60,rect.top+tooltip.caretY-tt.offsetHeight-14+window.scrollY)+'px';
}
document.addEventListener('click',()=>{tt.style.display='none';},{passive:true});
function renderRoundsTabs(){
  const el=document.getElementById('roundsTabs');
  el.innerHTML=ORDER.filter(g=>active.has(g)).map(g=>{const d=G[g];return`<button class="rtab2${g===activeRounds?' on':''}" data-g="${g}" style="--c:${d.color}">${d.name.split(' ')[0]}</button>`;}).join('');
  document.querySelectorAll('.rtab2').forEach(b=>b.addEventListener('click',()=>{activeRounds=b.dataset.g;renderRoundsTabs();renderRounds();}));
}
function renderRounds(){
  const d=G[activeRounds];const el=document.getElementById('roundsList');
  const display=[...d.rounds].reverse();
  el.innerHTML=display.map((s,i)=>`<div class="round"><div class="round-idx">${i+1}</div><div class="round-date">${fmtShort(s.date)}</div><div class="round-course">${s.course}</div><div class="round-holes" style="color:${d.color}">${s.holes===9?'9H':'18H'}</div><div class="round-score">${s.score}</div><div style="font-size:13px;font-weight:700;min-width:30px;text-align:right;color:${d.color}">${s.hi.toFixed(1)}</div></div>`).join('');
}
document.querySelectorAll('.rtab').forEach(t=>t.addEventListener('click',()=>{document.querySelectorAll('.rtab').forEach(x=>x.classList.remove('on'));t.classList.add('on');range=t.dataset.r;buildChart();renderStats();}));
renderPills();buildChart();renderStats();renderRoundsTabs();renderRounds();
</script>
</body>
</html>"""

# Substitute placeholders
ghin_order_str = ",".join(f'"{g}"' for g in ORDER)
HTML = HTML.replace("__GOLFERS__", golfers_js)
HTML = HTML.replace("__ORDER__", ghin_order_str)
HTML = HTML.replace("__TODAY__", TODAY)
HTML = HTML.replace("__TODAY_ISO__", date.today().isoformat())

for fname in ["index.html", "handicap.html"]:
    path = os.path.join(DIR, fname)
    with open(path, "w") as f:
        f.write(HTML)
    print(f"Wrote {path}")
