#!/usr/bin/env python3
"""Build index.html from ghin_data.json."""
import json, os
from datetime import date

DIR = "/Users/nathan.lee/pinehurst"

with open(f"{DIR}/ghin_data.json") as f:
    DATA = json.load(f)

ORDER = ["7866286", "7562830", "11367668", "11634995", "10460818", "3031631", "8676617", "11466889", "4990445"]
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

# Build first-name → current HI map from fetched data
name_hi = {}
for ghin, g in DATA.items():
    first = g["name"].split()[0]
    name_hi[first] = g["current"]
# David Ryu is "Dave" in the matchup table
name_hi["David"] = name_hi.get("David", "—")

def p(name):
    """Render a player name with handicap badge."""
    hi = name_hi.get(name, "—")
    badge = f'<span class="p-hi">{hi}</span>' if hi != "—" else '<span class="p-hi dim">—</span>'
    return f'<span class="player">{name}{badge}</span>'

def match(a, b, c, d):
    """Render a matchup cell: (a+b) vs (c+d)."""
    return f'{p(a)}<span class="plus">+</span>{p(b)}<span class="vs">vs</span>{p(c)}<span class="plus">+</span>{p(d)}'

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Pinehurst 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<style>
:root{
  --bg:#ffffff;--surface:#f4f6f4;--surface2:#e8ede9;--green-dark:#0a3318;
  --text:#0d1a10;--dim:#5a7a60;--radius:16px;
  --safe-top:env(safe-area-inset-top,0px);--safe-bot:env(safe-area-inset-bottom,0px);
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display',sans-serif;background:var(--bg);color:var(--text);min-height:100dvh;padding-top:var(--safe-top);padding-bottom:calc(var(--safe-bot)+24px);-webkit-font-smoothing:antialiased}
header{background:#ffffff;padding:14px 16px 14px;border-bottom:1px solid rgba(0,0,0,0.08)}
.header-row{display:flex;align-items:center;gap:10px}
.refresh-btn{margin-left:auto;padding:7px 14px;border-radius:20px;border:1.5px solid rgba(0,0,0,.1);background:transparent;font-family:inherit;font-size:12px;font-weight:700;color:var(--dim);cursor:pointer;transition:all .15s;white-space:nowrap;flex-shrink:0}
.refresh-btn:hover{border-color:#0a3318;color:#0a3318}
.refresh-btn.running{color:#b45309;border-color:#b45309}
.refresh-btn.done{color:#1a5c35;border-color:#1a5c35}
.refresh-btn.err{color:#be123c;border-color:#be123c}
.logo{height:52px;width:auto;flex-shrink:0;display:block}
.header-title{font-size:18px;font-weight:700;letter-spacing:-0.3px;color:#0d1a10}
.header-sub{font-size:12px;color:#5a7a60;margin-top:1px}
.team-filter{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.team-col{background:var(--surface);border-radius:12px;padding:10px}
.team-col-hdr{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;padding-bottom:7px;border-bottom:2px solid}
.left-hdr{color:#1a5c35;border-color:#1a5c35}
.right-hdr{color:#be123c;border-color:#be123c}
.tpill{display:flex;align-items:center;gap:7px;padding:6px 8px;border-radius:8px;border:1.5px solid rgba(0,0,0,.07);background:#fff;margin-bottom:5px;cursor:pointer;font-family:inherit;text-align:left;width:100%;transition:all .15s}
.tpill:last-child{margin-bottom:0}
.tpill .dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;opacity:.3;transition:opacity .15s}
.tpill .pname{font-size:12px;font-weight:600;color:var(--dim);flex:1;min-width:0}
.tpill .phi{font-size:13px;font-weight:800;color:var(--dim);flex-shrink:0}
.tpill.on{border-color:var(--c)}
.tpill.on .dot{opacity:1}
.tpill.on .pname{color:#0d1a10}
.tpill.on .phi{color:var(--c)}
.tpill.no-data{cursor:default;opacity:.45}
.pill-link{color:inherit;text-decoration:underline;text-decoration-style:dotted;text-underline-offset:2px}
.content{padding:14px;display:flex;flex-direction:column;gap:14px}
.range-tabs{display:flex;background:var(--surface);border-radius:10px;padding:3px;gap:2px}
.rtab{flex:1;text-align:center;padding:8px 4px;border-radius:7px;font-size:13px;font-weight:600;color:var(--dim);cursor:pointer;border:none;background:transparent;font-family:inherit;transition:all .15s}
.rtab.on{background:#0a3318;color:#ffffff}
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
.rtab2{padding:7px 14px;border-radius:20px;border:1.5px solid rgba(0,0,0,0.12);background:transparent;font-family:inherit;font-size:12px;font-weight:700;color:var(--dim);cursor:pointer;white-space:nowrap;transition:all .15s}
.rtab2.on{border-color:var(--c);color:var(--c);background:rgba(0,0,0,.03)}
.rounds-list{display:flex;flex-direction:column;gap:6px}
.round{display:flex;align-items:center;gap:10px;background:var(--surface);border-radius:11px;padding:10px 12px}
.round-idx{font-size:11px;color:var(--dim);min-width:18px;text-align:center;font-weight:600}
.round-date{font-size:11px;color:var(--dim);min-width:60px}
.round-course{flex:1;font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.round-holes{font-size:10px;color:var(--dim);background:var(--surface2);border-radius:4px;padding:2px 5px;flex-shrink:0}
.round-score{font-size:15px;font-weight:700;min-width:32px;text-align:right;flex-shrink:0}
/* ── Scores Table ── */
.scores-wrap{padding-bottom:2px}
.scores-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:12px;border:1px solid rgba(0,0,0,.08)}
.scores-table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:13px}
.scores-table thead tr:first-child{background:#0a3318}
.scores-table thead tr:first-child th{padding:8px 10px;font-size:10px;font-weight:700;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.05em;text-align:center}
.scores-table thead tr:first-child th:first-child{text-align:left}
.scores-table thead tr.sub-head th{padding:4px 10px 7px;font-size:9px;font-weight:600;color:rgba(255,255,255,.5);text-align:center;background:#0a3318;border-bottom:1px solid rgba(255,255,255,.12)}
.scores-table thead tr.sub-head th:first-child{text-align:left}
.scores-table td{padding:9px 10px;border-bottom:1px solid rgba(0,0,0,.05);text-align:center;vertical-align:middle}
.scores-table td:first-child{text-align:left;font-weight:600;font-size:13px}
.scores-table tbody tr:last-child td{border-bottom:none}
.scores-table tbody tr.team-divider td{border-top:2px solid rgba(0,0,0,.1);background:#f9fafb}
.sc-name{font-weight:700;font-size:13px;color:#0d1a10}
.sc-hi{font-size:10px;color:var(--dim);font-weight:500}
.sc-gross{font-weight:700;font-size:14px;color:#0d1a10}
.sc-net{font-size:11px;color:var(--dim);font-weight:600;margin-top:1px}
.sc-pending{color:rgba(0,0,0,.2);font-size:18px}
.sc-total{font-weight:800;font-size:14px;color:#0d1a10}
.sc-par.under{color:#1a5c35;font-weight:800}
.sc-par.over{color:#be123c;font-weight:800}
.sc-par.even{color:var(--dim);font-weight:700}
/* ── Course Info Table ── */
.ci-wrap{padding-bottom:2px}
.ci-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:12px;border:1px solid rgba(0,0,0,.08)}
.ci-table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:13px}
.ci-table thead tr{background:#0a3318}
.ci-table th{padding:9px 12px;text-align:left;font-size:10px;font-weight:700;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:.05em}
.ci-table td{padding:9px 12px;border-bottom:1px solid rgba(0,0,0,.05)}
.ci-table .white-row td{padding-top:4px;padding-bottom:9px;border-bottom:1px solid rgba(0,0,0,.08)}
.ci-table tbody tr:not(.white-row){padding-top:9px}
.ci-rnd{font-weight:800;font-size:14px;color:#0d1a10;width:32px;vertical-align:top;padding-top:10px}
.ci-course{vertical-align:top;padding-top:8px}
.ci-designer{font-size:10px;color:var(--dim);margin-top:2px}
.ci-tee{font-weight:700;font-size:11px;width:44px;vertical-align:middle}
.blue-tee{color:#1d4ed8}
.white-tee{color:#5a7a60}
.ci-yards{font-weight:600;font-size:13px;color:#0d1a10}
.ci-par{color:var(--dim);font-weight:600;text-align:center}
.ci-rating{font-weight:700;color:#0d1a10;text-align:center}
.ci-slope{font-weight:800;color:#0a3318;text-align:center}
/* ── Overall Scoreboard ── */
.overall-sb{background:#0a3318;border-radius:var(--radius);padding:16px 14px;color:#fff}
.ot-wrap{display:flex;align-items:center;gap:8px}
.ot-side{flex:1;text-align:center}
.ot-players{font-size:10px;color:rgba(255,255,255,.5);line-height:1.7;margin-bottom:6px;letter-spacing:.01em}
.ot-team-name{font-size:13px;font-weight:800;color:rgba(255,255,255,.8);letter-spacing:.04em;text-transform:uppercase;margin-bottom:6px}
.ot-score{font-size:52px;font-weight:900;line-height:1;color:#fff;letter-spacing:-2px}
.ot-divider{font-size:14px;font-weight:800;color:rgba(255,255,255,.35);flex-shrink:0}
.ot-bar{display:flex;height:5px;border-radius:3px;overflow:hidden;background:rgba(255,255,255,.15);margin-top:14px}
.ot-bar-l{background:#d4af37;transition:width .4s ease}
.ot-bar-r{background:rgba(255,255,255,.55);transition:width .4s ease}
.ot-matches{text-align:center;font-size:10px;color:rgba(255,255,255,.4);margin-top:6px}
/* ── Round Scoreboard ── */
.scoreboard{display:flex;flex-direction:column;gap:8px}
.sb-round-tabs{display:flex;gap:6px;margin-bottom:2px}
.sb-rtab{flex:1;padding:8px 4px;border-radius:8px;border:1.5px solid rgba(0,0,0,.08);background:var(--surface);font-family:inherit;font-size:13px;font-weight:700;color:var(--dim);cursor:pointer;transition:all .15s;text-align:center}
.sb-rtab.on{background:#0a3318;color:#fff;border-color:#0a3318}
.foursome-card{border-radius:12px;overflow:hidden;border:1.5px solid rgba(0,0,0,.08);background:#fff;margin-bottom:8px}
.foursome-teams{display:flex;align-items:stretch}
.team-btn{flex:1;min-width:0;padding:10px 7px;background:transparent;border:none;font-family:inherit;cursor:pointer;text-align:left;transition:background .15s;display:flex;flex-direction:column;gap:3px;overflow:hidden}
.team-btn.won{background:rgba(10,51,24,.07)}
.team-btn.won .t-names{color:#0a3318;font-weight:800}
.team-btn.gsel{background:rgba(10,51,24,.04)}
.t-names{font-size:12px;font-weight:700;color:#0d1a10;line-height:1.4;word-break:break-word}
.t-hi{font-size:10px;font-weight:600;color:var(--dim)}
.t-player{display:flex;align-items:center;gap:4px;width:100%;padding:2px 0;flex-wrap:nowrap;overflow:hidden}
.t-player+.t-player{border-top:1px solid rgba(0,0,0,.05);margin-top:2px;padding-top:4px}
.t-pname{font-size:12px;font-weight:700;color:#0d1a10;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.team-btn.won .t-pname{color:#0a3318}
.t-phi{font-size:10px;font-weight:700;color:var(--dim);background:rgba(0,0,0,.05);border-radius:4px;padding:1px 4px;flex-shrink:0;white-space:nowrap}
.sb-center{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;padding:8px 6px;background:var(--surface);border-left:1px solid rgba(0,0,0,.06);border-right:1px solid rgba(0,0,0,.06);flex-shrink:0;width:72px}
.win-btns{display:flex;gap:2px}
.win-btn{width:20px;height:22px;border-radius:5px;border:1.5px solid rgba(0,0,0,.1);background:transparent;font-family:inherit;font-size:11px;font-weight:800;color:var(--dim);cursor:pointer;transition:all .12s;padding:0;display:flex;align-items:center;justify-content:center}
.win-btn.active-l{background:#0a3318;border-color:#0a3318;color:#fff}
.win-btn.active-r{background:#0a3318;border-color:#0a3318;color:#fff}
.win-btn.active-h{background:#d4af37;border-color:#d4af37;color:#fff}
.tee-btn{padding:1px 5px;border-radius:4px;border:1.5px solid;font-family:inherit;font-size:9px;font-weight:800;cursor:pointer;transition:all .12s;line-height:1.5;flex-shrink:0}
.tee-b{border-color:rgba(29,78,216,.3);color:rgba(29,78,216,.45);background:transparent}
.tee-b.tb-on{border-color:#1d4ed8;color:#1d4ed8;background:rgba(29,78,216,.08)}
.tee-w{border-color:rgba(0,0,0,.15);color:rgba(0,0,0,.3);background:transparent}
.tee-w.tb-on{border-color:#374151;color:#374151;background:rgba(0,0,0,.06)}
.ch-badge{font-size:9px;font-weight:700;color:var(--dim);flex-shrink:0}
.stk-badge{font-size:9px;font-weight:800;color:#fff;background:#0a3318;border-radius:4px;padding:0 4px;flex-shrink:0}
.stk-badge.scratch{background:var(--dim)}
.result-input{width:62px;border:1px solid rgba(0,0,0,.12);border-radius:6px;padding:3px 5px;font-family:inherit;font-size:11px;text-align:center;background:#fff;color:#0d1a10;outline:none}
.result-input:focus{border-color:#0a3318}
.result-input::placeholder{color:rgba(0,0,0,.3)}
.matchup-wrap{padding-bottom:4px}
.matchup-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:12px;border:1px solid rgba(0,0,0,0.08)}
.matchup-table{width:100%;border-collapse:collapse;white-space:nowrap}
.matchup-table thead tr{background:#f4f6f4}
.matchup-table th{padding:9px 12px;text-align:left;font-size:10px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid rgba(0,0,0,0.08)}
.matchup-table td{padding:10px 12px;border-bottom:1px solid rgba(0,0,0,0.05);vertical-align:middle}
.matchup-table tbody tr:last-child td{border-bottom:none}
.matchup-table tbody tr:nth-child(even){background:#fafafa}
.round-num{font-weight:800;font-size:14px;color:#0d1a10;text-align:center;width:36px}
.course-num{font-weight:700;font-size:12px;color:var(--dim);text-align:center;width:60px}
.course-link{font-weight:700;font-size:12px;color:#0a3318;text-decoration:none;border-bottom:1px solid rgba(10,51,24,0.3);white-space:nowrap}
.course-link:hover{border-bottom-color:#0a3318}
.player{display:inline-flex;flex-direction:column;align-items:center;font-weight:600;font-size:12px;color:#0d1a10;line-height:1.2}
.p-hi{font-size:10px;font-weight:700;color:#0a3318}
.p-hi.dim{color:var(--dim)}
.plus{margin:0 4px;font-size:11px;color:var(--dim);font-weight:600}
.vs{margin:0 8px;font-size:10px;font-weight:800;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;vertical-align:middle}
#tooltip{position:fixed;background:#ffffff;border:1px solid rgba(0,0,0,.1);border-radius:12px;padding:10px 14px;pointer-events:none;display:none;box-shadow:0 8px 32px rgba(0,0,0,.15);z-index:999;transform:translateX(-50%);white-space:nowrap}
.tt-date{font-size:11px;color:var(--dim);margin-bottom:2px}
.tt-hi{font-size:26px;font-weight:800;line-height:1}
.tt-name{font-size:12px;color:var(--dim);margin-top:3px}
</style>
</head>
<body>
<header>
  <div class="header-row">
    <img class="logo" src="putterboy.png" alt="Pinehurst">
    <div><div class="header-title">Pinehurst 2026</div></div>
    <button class="refresh-btn" id="refreshBtn" onclick="triggerRefresh()">↻ Refresh</button>
  </div>
</header>
<div class="content">
  <!-- Course Info -->
  __COURSE_INFO_TABLE__
  <!-- Overall Scoreboard -->
  <div class="overall-sb">
    <div class="ot-wrap">
      <div class="ot-side">
        <div class="ot-team-name">Team Expand</div>
        <div class="ot-score" id="ot-score-l">0</div>
      </div>
      <div class="ot-divider">vs</div>
      <div class="ot-side">
        <div class="ot-team-name">Team Shrink</div>
        <div class="ot-score" id="ot-score-r">0</div>
      </div>
    </div>
    <div class="ot-bar"><div class="ot-bar-l" id="ot-bar-l" style="width:50%"></div><div class="ot-bar-r" id="ot-bar-r" style="width:50%"></div></div>
    <div class="ot-matches" id="ot-matches">0 of 12 matches played</div>
  </div>
  <!-- Round Scoreboard -->
  <div class="scoreboard">
    <div class="sb-round-tabs" id="sbTabs"></div>
    <div id="sbRows"></div>
  </div>
  <!-- Individual Scores -->
  __SCORES_TABLE__
  <!-- Team player filter -->
  <div class="team-filter">
    <div class="team-col" id="teamLeft">
      <div class="team-col-hdr left-hdr">Team Expand</div>
    </div>
    <div class="team-col" id="teamRight">
      <div class="team-col-hdr right-hdr">Team Shrink</div>
    </div>
  </div>
  <!-- Graph -->
  <div class="range-tabs">
    <button class="rtab on" data-r="1">1Y</button>
    <button class="rtab" data-r="2">2Y</button>
    <button class="rtab" data-r="5">5Y</button>
    <button class="rtab" data-r="all">All</button>
  </div>
  <div class="chart-card">
    <div class="chart-wrap"><canvas id="hiChart"></canvas></div>
  </div>
  <div><div class="stats-grid" id="statsGrid"></div></div>
  <div>
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
let active=new Set(ORDER),range='1',activeRounds=ORDER[0],chart=null;
function cutoff(r){if(r==='all')return new Date('2000-01-01');const d=new Date(NOW);d.setFullYear(d.getFullYear()-parseInt(r));return d;}
function fmtDate(s){return new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}
function fmtShort(s){return new Date(s+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'})}
const LEFT_TEAM=[{n:'Alec',g:'3031631'},{n:'Eddie',g:'7866286'},{n:'David',g:'11367668'},{n:'Nathan',g:'7562830'},{n:'Mike',g:'11466889'},{n:'Matt',g:null}];
const RIGHT_TEAM=[{n:'Dillon',g:'8676617'},{n:'Adam',g:'11634995'},{n:'Alex',g:'4990445'},{n:'Chris',g:null},{n:'Luis',g:null},{n:'John',g:'10460818'}];

const GHIN_LINKS={'11367668':'https://www.ghin.com/golfer-lookup/all-golfers'};
function pillHTML(p){
  if(!p.g){return`<button class="tpill no-data"><div class="dot" style="background:#ccc"></div><div class="pname">${p.n}</div><div class="phi" style="color:var(--dim)">—</div></button>`;}
  const d=G[p.g],on=active.has(p.g);
  const nameHTML=GHIN_LINKS[p.g]?`<a class="pill-link" href="${GHIN_LINKS[p.g]}" target="_blank" onclick="event.stopPropagation()">${p.n}</a>`:p.n;
  return`<button class="tpill${on?' on':''}" data-g="${p.g}" style="--c:${d.color}"><div class="dot" style="background:${d.color}"></div><div class="pname">${nameHTML}</div><div class="phi">${d.current}</div></button>`;
}

function renderPills(){
  const leftEl=document.getElementById('teamLeft');
  const rightEl=document.getElementById('teamRight');
  leftEl.innerHTML='<div class="team-col-hdr left-hdr">Team Expand</div>'+LEFT_TEAM.map(pillHTML).join('');
  rightEl.innerHTML='<div class="team-col-hdr right-hdr">Team Shrink</div>'+RIGHT_TEAM.map(pillHTML).join('');
  document.querySelectorAll('.tpill:not(.no-data)').forEach(p=>p.addEventListener('click',()=>{
    const g=p.dataset.g;
    if(active.size===1&&active.has(g)){active=new Set(ORDER)}
    else if(active.size===1&&!active.has(g)){active.add(g)}
    else{active=new Set([g])}
    renderPills();buildChart();renderStats();renderRoundsTabs();
  }));
}
function renderStats(){
  const el=document.getElementById('statsGrid');const cards=[];
  active.forEach(g=>{const d=G[g];const filtered=d.revs.filter(r=>new Date(r.date)>=cutoff(range));if(!filtered.length)return;const his=filtered.map(r=>r.hi);const mx=Math.max(...his);const delta=(filtered[filtered.length-1].hi-filtered[0].hi).toFixed(1);const isDown=parseFloat(delta)<0;cards.push(`<div class="stat" style="border-left:3px solid ${d.color}"><div class="stat-val" style="color:${d.color}">${d.current}</div><div class="stat-lbl">${d.name.split(' ')[0]}</div><div style="font-size:11px;color:var(--dim);margin-top:4px">Low ${d.low} &middot; Hi ${mx}</div><div style="font-size:12px;font-weight:700;margin-top:3px;color:${isDown?'#0a3318':'#b45309'}">${isDown?'▼':'▲'} ${Math.abs(delta)}</div></div>`);});
  el.style.gridTemplateColumns=`repeat(${Math.min(cards.length,3)},1fr)`;el.innerHTML=cards.join('');
}
function buildChart(){
  const ctx=document.getElementById('hiChart').getContext('2d');const datasets=[];
  ORDER.forEach(g=>{
    if(!active.has(g))return;const d=G[g];
    const filtered=d.revs.filter(r=>new Date(r.date)>=cutoff(range));
    const pts=filtered.map(r=>({x:r.date,y:r.hi,name:d.name,series:'revisions'}));
    datasets.push({label:d.name,data:pts,borderColor:d.color,backgroundColor:'transparent',borderWidth:2.5,fill:false,tension:0.3,pointRadius:0,pointHoverRadius:4,pointBackgroundColor:d.color,pointBorderColor:'#ffffff',pointBorderWidth:2,pointHoverBackgroundColor:'#ffffff',pointHoverBorderColor:d.color,pointHoverBorderWidth:2});
  });
  if(chart)chart.destroy();
  const endLabelPlugin={id:'endLabels',afterDatasetsDraw(chart){const ctx=chart.ctx;const GAP=15;const labels=[];chart.data.datasets.forEach((ds,i)=>{if(!ds.data.length)return;const meta=chart.getDatasetMeta(i);if(meta.hidden)return;const last=meta.data[meta.data.length-1];if(!last)return;labels.push({y:last.y,color:ds.borderColor,name:ds.label.split(' ')[0]});});if(!labels.length)return;labels.sort((a,b)=>a.y-b.y);const adj=labels.map(l=>l.y);for(let i=1;i<adj.length;i++){if(adj[i]-adj[i-1]<GAP)adj[i]=adj[i-1]+GAP;}const top=chart.chartArea.top+6,bot=chart.chartArea.bottom-6;for(let i=adj.length-1;i>=0;i--){adj[i]=Math.min(adj[i],bot-(adj.length-1-i)*GAP);}for(let i=0;i<adj.length;i++){adj[i]=Math.max(adj[i],top+i*GAP);}const xRight=chart.chartArea.right+6;ctx.save();ctx.font='bold 11px -apple-system,BlinkMacSystemFont,sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';labels.forEach((l,i)=>{ctx.fillStyle=l.color;ctx.fillText(l.name,xRight,adj[i]);});ctx.restore();}};
  chart=new Chart(ctx,{type:'line',data:{datasets},plugins:[endLabelPlugin],options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'nearest',intersect:false,axis:'x'},layout:{padding:{right:52}},plugins:{legend:{display:false},tooltip:{enabled:false,external:extTT}},scales:{x:{type:'time',time:{unit:range==='1'?'month':range==='2'?'month':'year',tooltipFormat:'MMM d, yyyy'},grid:{color:'rgba(0,0,0,0.06)'},ticks:{color:'#5a7a60',font:{size:11},maxTicksLimit:6},border:{display:false}},y:{reverse:true,grid:{color:'rgba(0,0,0,0.06)'},ticks:{color:'#5a7a60',font:{size:11},maxTicksLimit:6,callback:v=>v.toFixed(1)},border:{display:false}}}}});
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
// ── Scoreboard ──────────────────────────────────────
const MATCHUPS={
  1:[{left:['Alec','Nathan'],right:['Dillon','Adam']},{left:['Eddie','David'],right:['Alex','Chris']},{left:['Mike','Matt'],right:['Luis','John']}],
  2:[{left:['Alec','David'],right:['Alex','John']},{left:['Eddie','Mike'],right:['Dillon','Luis']},{left:['Nathan','Matt'],right:['Adam','Chris']}],
  3:[{left:['Alec','Eddie'],right:['Alex','Luis']},{left:['David','Matt'],right:['Chris','Dillon']},{left:['Mike','Nathan'],right:['John','Adam']}],
  4:[{left:['Alec','Mike'],right:['Adam','Luis']},{left:['Eddie','Matt'],right:['John','Chris']},{left:['David','Nathan'],right:['Alex','Dillon']}],
};
const NAME_GHIN={'Alec':'3031631','Nathan':'7562830','Eddie':'7866286','David':'11367668','Adam':'11634995','John':'10460818','Dillon':'8676617','Mike':'11466889','Alex':'4990445'};
const STORE='pinehurst2026';
const TEE_STORE='pinehurst2026_tees';
const ROUND_TEES={
  1:{blue:{rating:74.1,slope:142,par:70},white:{rating:71.5,slope:137,par:70}},
  2:{blue:{rating:73.7,slope:135,par:72},white:{rating:70.8,slope:131,par:72}},
  3:{blue:{rating:75.4,slope:143,par:72},white:{rating:72.0,slope:139,par:72}},
  4:{blue:{rating:72.9,slope:131,par:72},white:{rating:70.5,slope:127,par:72}},
};
let sbRound=1,sbSel=null;

function loadRes(){try{return JSON.parse(localStorage.getItem(STORE)||'{}');}catch(e){return {};}}
function saveRes(r){localStorage.setItem(STORE,JSON.stringify(r));}
function loadTees(){try{return JSON.parse(localStorage.getItem(TEE_STORE)||'{}');}catch(e){return {};}}
function saveTees(t){localStorage.setItem(TEE_STORE,JSON.stringify(t));}
function matchKey(round,idx){return `${round}-${idx}`;}
function teeKey(round,name){return `${round}-${name}`;}

function calcScores(){
  const res=loadRes();let l=0,r=0,played=0;
  Object.values(res).forEach(v=>{
    if(!v.winner)return;played++;
    if(v.winner==='l')l+=1;else if(v.winner==='r')r+=1;else{l+=0.5;r+=0.5;}
  });
  return{l,r,played};
}

function fmtPts(n){return n===Math.floor(n)?String(n):n.toFixed(1);}

function updateOverall(){
  const{l,r,played}=calcScores();
  document.getElementById('ot-score-l').textContent=fmtPts(l);
  document.getElementById('ot-score-r').textContent=fmtPts(r);
  const total=12,pct=total>0?(l/total)*100:50;
  document.getElementById('ot-bar-l').style.width=pct+'%';
  document.getElementById('ot-bar-r').style.width=(100-pct)+'%';
  document.getElementById('ot-matches').textContent=`${played} of ${total} matches played`;
}

function ghinsFor(names){return names.map(n=>NAME_GHIN[n]).filter(Boolean);}
function playerHI(name){const g=Object.values(G).find(x=>x.name.split(' ')[0]===name);return g?parseFloat(g.current):null;}
function playerHIStr(name){const h=playerHI(name);return h!==null?h.toFixed(1):'—';}

function calcCH(name,round,tee){
  const hi=playerHI(name);if(hi===null)return null;
  const t=ROUND_TEES[round][tee];
  return Math.round(hi*(t.slope/113)+(t.rating-t.par));
}

function getMatchStrokes(allNames,round){
  // Returns {name: strokes} if all players with HI data have tees selected, else null
  const tees=loadTees();
  const chs={};
  for(const name of allNames){
    if(playerHI(name)===null) continue; // skip players with no HI data
    const tee=tees[teeKey(round,name)];
    if(!tee) return null; // not all selected yet
    const ch=calcCH(name,round,tee);
    if(ch===null) return null;
    chs[name]=ch;
  }
  if(!Object.keys(chs).length) return null;
  const minCH=Math.min(...Object.values(chs));
  const strokes={};
  for(const[name,ch] of Object.entries(chs)) strokes[name]=ch-minCH;
  return strokes;
}

function renderSBTabs(){
  const tabs=document.getElementById('sbTabs');
  tabs.innerHTML=[1,2,3,4].map(r=>`<button class="sb-rtab${r===sbRound?' on':''}" data-r="${r}">Round ${r}</button>`).join('');
  tabs.querySelectorAll('.sb-rtab').forEach(b=>b.addEventListener('click',()=>{
    sbRound=+b.dataset.r;sbSel=null;active=new Set(ORDER);
    renderPills();buildChart();renderStats();renderRoundsTabs();renderSBTabs();renderSBRows();
  }));
}

function renderSBRows(){
  const res=loadRes();
  const tees=loadTees();
  const rows=document.getElementById('sbRows');

  rows.innerHTML=MATCHUPS[sbRound].map((m,i)=>{
    const key=matchKey(sbRound,i);
    const saved=res[key]||{};
    const winner=saved.winner||'';
    const resultVal=saved.result||'';
    const lsel=sbSel===key+'-l',rsel=sbSel===key+'-r';
    const allNames=[...m.left,...m.right];
    const strokes=getMatchStrokes(allNames,sbRound);

    function playerHTML(name){
      const hi=playerHI(name);
      const tee=tees[teeKey(sbRound,name)]||null;
      const ch=tee&&hi!==null?calcCH(name,sbRound,tee):null;
      const stk=strokes&&strokes[name]!==undefined?strokes[name]:null;
      const chStr=ch!==null?`<span class="ch-badge">CH${ch}</span>`:'';
      const stkStr=stk!==null?(stk===0?`<span class="stk-badge scratch">—</span>`:`<span class="stk-badge">+${stk}</span>`):'';
      return `<div class="t-player">
        <span class="t-pname">${name}</span>
        <span class="t-phi">${hi!==null?hi.toFixed(1):'—'}</span>
        <button class="tee-btn tee-b${tee==='blue'?' tb-on':''}" data-p="${name}" data-r="${sbRound}" data-t="blue">B</button>
        <button class="tee-btn tee-w${tee==='white'?' tb-on':''}" data-p="${name}" data-r="${sbRound}" data-t="white">W</button>
        ${chStr}${stkStr}
      </div>`;
    }

    const lHTML=m.left.map(playerHTML).join('');
    const rHTML=m.right.map(playerHTML).join('');

    return `<div class="foursome-card" data-key="${key}">
      <div class="foursome-teams">
        <button class="team-btn${winner==='l'?' won':''}${lsel?' gsel':''}" data-side="l" data-key="${key}" data-names="${m.left.join(',')}">
          ${lHTML}
        </button>
        <div class="sb-center">
          <div class="win-btns">
            <button class="win-btn${winner==='l'?' active-l':''}" data-key="${key}" data-w="l">◀</button>
            <button class="win-btn${winner==='h'?' active-h':''}" data-key="${key}" data-w="h">½</button>
            <button class="win-btn${winner==='r'?' active-r':''}" data-key="${key}" data-w="r">▶</button>
          </div>
          <input class="result-input" data-key="${key}" placeholder="e.g. 2&1" value="${resultVal}">
        </div>
        <button class="team-btn${winner==='r'?' won':''}${rsel?' gsel':''}" data-side="r" data-key="${key}" data-names="${m.right.join(',')}">
          ${rHTML}
        </button>
      </div>
    </div>`;
  }).join('');

  // Team buttons → filter graph (ignore clicks on tee buttons inside)
  rows.querySelectorAll('.team-btn').forEach(b=>b.addEventListener('click',()=>{
    const k=b.dataset.key+'-'+b.dataset.side,names=b.dataset.names.split(','),ghins=ghinsFor(names);
    if(sbSel===k){sbSel=null;active=new Set(ORDER);}
    else{sbSel=k;active=ghins.length?new Set(ghins):new Set(ORDER);}
    renderPills();buildChart();renderStats();renderRoundsTabs();renderSBRows();
  }));

  // Tee buttons → save tee and re-render
  rows.querySelectorAll('.tee-btn').forEach(b=>b.addEventListener('click',e=>{
    e.stopPropagation();
    const t=loadTees();const k=teeKey(+b.dataset.r,b.dataset.p);
    t[k]=b.dataset.t;saveTees(t);renderSBRows();
  }));

  // Winner buttons
  rows.querySelectorAll('.win-btn').forEach(b=>b.addEventListener('click',e=>{
    e.stopPropagation();
    const res=loadRes();const key=b.dataset.key;
    const cur=(res[key]||{}).winner;
    if(!res[key])res[key]={};
    res[key].winner=cur===b.dataset.w?'':b.dataset.w;
    saveRes(res);updateOverall();renderSBRows();
  }));

  // Result input
  rows.querySelectorAll('.result-input').forEach(inp=>inp.addEventListener('change',()=>{
    const res=loadRes();const key=inp.dataset.key;
    if(!res[key])res[key]={};
    res[key].result=inp.value.trim();saveRes(res);
  }));
}

renderPills();renderSBTabs();renderSBRows();updateOverall();buildChart();renderStats();renderRoundsTabs();renderRounds();

async function triggerRefresh(){
  const btn=document.getElementById('refreshBtn');
  let token=localStorage.getItem('gh_pat');
  if(!token){
    token=prompt('Enter a GitHub PAT with "workflow" scope. Stored only on this device.');
    if(!token)return;
    localStorage.setItem('gh_pat',token.trim());
  }
  btn.textContent='⏳ Running...';btn.className='refresh-btn running';btn.disabled=true;
  try{
    const res=await fetch('https://api.github.com/repos/nathanmjlee22/pinehurst/actions/workflows/refresh.yml/dispatches',{
      method:'POST',
      headers:{'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'},
      body:JSON.stringify({ref:'master'}),
    });
    if(res.status===204){
      btn.textContent='✓ Refreshing — reload in ~2 min';btn.className='refresh-btn done';
      setTimeout(()=>{btn.textContent='↻ Refresh';btn.className='refresh-btn';btn.disabled=false;},120000);
    } else if(res.status===401||res.status===403){
      localStorage.removeItem('gh_pat');
      btn.textContent='✗ Bad token — tap to retry';btn.className='refresh-btn err';btn.disabled=false;
    } else {
      btn.textContent='✗ Error '+res.status;btn.className='refresh-btn err';
      setTimeout(()=>{btn.textContent='↻ Refresh';btn.className='refresh-btn';btn.disabled=false;},4000);
    }
  }catch(e){
    btn.textContent='✗ Network error';btn.className='refresh-btn err';
    setTimeout(()=>{btn.textContent='↻ Refresh';btn.className='refresh-btn';btn.disabled=false;},4000);
  }
}
</script>
</body>
</html>"""

# Build matchup table HTML
COURSE_URLS = {
    2:  "https://www.pinehurst.com/golf/courses/no-2/",
    4:  "https://www.pinehurst.com/golf/courses/no-4/",
    8:  "https://www.pinehurst.com/golf/courses/no-8/",
    10: "https://www.pinehurst.com/golf/courses/no-10/",
}

COURSE_INFO = {
    10: {"url": "https://www.pinehurst.com/golf/courses/no-10/", "designer": "Tom Doak", "par": 70,
         "blue": {"yards": 7020, "rating": 74.1, "slope": 142},
         "white": {"yards": 6439, "rating": 71.5, "slope": 137}},
    4:  {"url": "https://www.pinehurst.com/golf/courses/no-4/", "designer": "Gil Hanse", "par": 72,
         "blue": {"yards": 6961, "rating": 73.7, "slope": 135},
         "white": {"yards": 6428, "rating": 70.8, "slope": 131}},
    2:  {"url": "https://www.pinehurst.com/golf/courses/no-2/", "designer": "Donald Ross", "par": 72,
         "blue": {"yards": 6961, "rating": 75.4, "slope": 143},
         "white": {"yards": 6307, "rating": 72.0, "slope": 139}},
    8:  {"url": "https://www.pinehurst.com/golf/courses/no-8/", "designer": "Tom Fazio", "par": 72,
         "blue": {"yards": 6694, "rating": 72.9, "slope": 131},
         "white": {"yards": 6311, "rating": 70.5, "slope": 127}},
}

course_rounds = [(1, 10), (2, 4), (3, 2), (4, 8)]
ci_rows = ""
for rnd, cnum in course_rounds:
    ci = COURSE_INFO[cnum]
    ci_rows += f"""<tr>
      <td class="ci-rnd">{rnd}</td>
      <td class="ci-course"><a href="{ci['url']}" target="_blank" class="course-link">No.&nbsp;{cnum}</a><div class="ci-designer">{ci['designer']}</div></td>
      <td class="ci-tee blue-tee">Blue</td>
      <td class="ci-yards">{ci['blue']['yards']:,}</td>
      <td class="ci-par">{ci['par']}</td>
      <td class="ci-rating">{ci['blue']['rating']}</td>
      <td class="ci-slope">{ci['blue']['slope']}</td>
    </tr>
    <tr class="white-row">
      <td></td><td></td>
      <td class="ci-tee white-tee">White</td>
      <td class="ci-yards">{ci['white']['yards']:,}</td>
      <td class="ci-par">{ci['par']}</td>
      <td class="ci-rating">{ci['white']['rating']}</td>
      <td class="ci-slope">{ci['white']['slope']}</td>
    </tr>"""

course_info_table = f"""<div class="ci-wrap">
    <div class="ci-scroll">
      <table class="ci-table">
        <thead><tr>
          <th>Rnd</th><th>Course</th><th>Tee</th>
          <th>Yards</th><th>Par</th><th>Rating</th><th>Slope</th>
        </tr></thead>
        <tbody>{ci_rows}</tbody>
      </table>
    </div>
  </div>"""

ROUNDS = [
    {"round": 1, "date": "2026-09-04", "course_num": 10, "par": 70,
     "blue": {"rating": 74.1, "slope": 142}, "white": {"rating": 71.5, "slope": 137}},
    {"round": 2, "date": "2026-09-05", "course_num": 4,  "par": 72,
     "blue": {"rating": 73.7, "slope": 135}, "white": {"rating": 70.8, "slope": 131}},
    {"round": 3, "date": "2026-09-05", "course_num": 2,  "par": 72,
     "blue": {"rating": 75.4, "slope": 143}, "white": {"rating": 72.0, "slope": 139}},
    {"round": 4, "date": "2026-09-06", "course_num": 8,  "par": 72,
     "blue": {"rating": 72.9, "slope": 131}, "white": {"rating": 70.5, "slope": 127}},
]

# All 12 players in order (left team then right team)
ALL_PLAYERS = [
    # (display_name, ghin_or_None, team)
    ("Alec",   "3031631",  "left"),
    ("Eddie",  "7866286",  "left"),
    ("David",  "11367668", "left"),
    ("Nathan", "7562830",  "left"),
    ("Mike",   "11466889", "left"),
    ("Matt",   None,       "left"),
    ("Dillon", "8676617",  "right"),
    ("Adam",   "11634995", "right"),
    ("Alex",   "4990445",  "right"),
    ("Chris",  None,       "right"),
    ("Luis",   None,       "right"),
    ("John",   "10460818", "right"),
]

TOTAL_PAR = sum(r["par"] for r in ROUNDS)  # 70+72+72+72 = 286

def fmt_par(diff):
    if diff is None: return '<span class="sc-pending">—</span>'
    if diff == 0: return '<span class="sc-par even">E</span>'
    sign = "+" if diff > 0 else ""
    cls = "over" if diff > 0 else "under"
    return f'<span class="sc-par {cls}">{sign}{diff}</span>'

def build_scores_table():
    score_rows = ""
    prev_team = None
    for name, ghin, team in ALL_PLAYERS:
        if prev_team == "left" and team == "right":
            # divider row between teams
            score_rows += '<tr class="team-divider"><td colspan="9"></td></tr>'
        prev_team = team

        g = DATA.get(ghin, {}) if ghin else {}
        hi = g.get("current", "—")
        tourney = g.get("tourney", {}) if ghin else {}

        cells = ""
        total_gross = 0
        total_net = 0
        has_any = False

        for rnd in ROUNDS:
            rnum = rnd["round"]
            rd = tourney.get(str(rnum)) or tourney.get(rnum)
            if rd and rd.get("gross"):
                gross = rd["gross"]
                net = rd.get("net", "—")
                total_gross += gross
                if isinstance(net, int): total_net += net
                has_any = True
                net_str = str(net) if isinstance(net, int) else "—"
                cells += f'<td><div class="sc-gross">{gross}</div><div class="sc-net">Net {net_str}</div></td>'
            else:
                cells += '<td><span class="sc-pending">—</span></td>'

        if has_any:
            gross_par = total_gross - TOTAL_PAR
            net_par = total_net - TOTAL_PAR
            total_cell = f'<td class="sc-total">{total_gross}</td>'
            net_cell = f'<td class="sc-total">{total_net}</td>'
            par_cell = f'<td>{fmt_par(gross_par)}</td>'
            net_par_cell = f'<td>{fmt_par(net_par)}</td>'
        else:
            total_cell = '<td><span class="sc-pending">—</span></td>'
            net_cell = '<td><span class="sc-pending">—</span></td>'
            par_cell = '<td><span class="sc-pending">—</span></td>'
            net_par_cell = '<td><span class="sc-pending">—</span></td>'

        score_rows += f'''<tr>
          <td><div class="sc-name">{name}</div><div class="sc-hi">HI {hi}</div></td>
          {cells}{total_cell}{net_cell}{par_cell}{net_par_cell}
        </tr>'''

    scores_table = f'''<div class="scores-wrap">
    <div class="scores-scroll">
      <table class="scores-table">
        <thead>
          <tr>
            <th rowspan="2">Player</th>
            <th>R1 · 9/4</th><th>R2 · 9/5</th><th>R3 · 9/5</th><th>R4 · 9/6</th>
            <th>Gross</th><th>Net</th><th>+/- Gross</th><th>+/- Net</th>
          </tr>
          <tr class="sub-head">
            <th>No.10</th><th>No.4</th><th>No.2</th><th>No.8</th>
            <th colspan="4"></th>
          </tr>
        </thead>
        <tbody>{score_rows}</tbody>
      </table>
    </div>
  </div>'''
    return scores_table

scores_table_html = build_scores_table()

matchup_rows = [
    (1, 10, ("Alec","Nathan","Dillon","Adam"),   ("Eddie","Dave","Alex","Chris"),    ("Mike","Matt","Luis","John")),
    (2,  4, ("Alec","Dave","Alex","John"),        ("Eddie","Mike","Dillon","Luis"),   ("Nathan","Matt","Adam","Chris")),
    (3,  2, ("Alec","Eddie","Alex","Luis"),       ("Dave","Matt","Chris","Dillon"),   ("Mike","Nathan","John","Adam")),
    (4,  8, ("Alec","Mike","Adam","Luis"),        ("Eddie","Matt","John","Chris"),    ("Dave","Nathan","Alex","Dillon")),
]
rows_html = ""
for rnd, course, f1, f2, f3 in matchup_rows:
    url = COURSE_URLS.get(course, "#")
    course_cell = f'<a class="course-link" href="{url}" target="_blank">No.&nbsp;{course}</a>'
    rows_html += f"""<tr>
      <td class="round-num">{rnd}</td>
      <td class="course-num">{course_cell}</td>
      <td>{match(*f1)}</td>
      <td>{match(*f2)}</td>
      <td>{match(*f3)}</td>
    </tr>"""

matchup_table = f"""<div class="matchup-wrap">
    <div class="matchup-scroll">
      <table class="matchup-table">
        <thead><tr>
          <th>Rnd</th><th>Crs</th>
          <th>Foursome 1</th><th>Foursome 2</th><th>Foursome 3</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
  </div>"""

# Substitute placeholders
ghin_order_str = ",".join(f'"{g}"' for g in ORDER)
HTML = HTML.replace("__GOLFERS__", golfers_js)
HTML = HTML.replace("__ORDER__", ghin_order_str)
HTML = HTML.replace("__TODAY__", TODAY)
HTML = HTML.replace("__TODAY_ISO__", date.today().isoformat())
HTML = HTML.replace("__MATCHUP_TABLE__", matchup_table)
HTML = HTML.replace("__COURSE_INFO_TABLE__", course_info_table)
HTML = HTML.replace("__SCORES_TABLE__", scores_table_html)

for fname in ["index.html", "handicap.html"]:
    path = os.path.join(DIR, fname)
    with open(path, "w") as f:
        f.write(HTML)
    print(f"Wrote {path}")
