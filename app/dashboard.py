"""Dashboard routes: serves the 6-panel observability dashboard and its data API."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

try:
  # Package mode (e.g., imported by app.main)
  from .metrics import timeseries_data
except ImportError:
  # Script mode (e.g., `python dashboard.py` from app/)
  from metrics import timeseries_data

router = APIRouter(tags=["dashboard"])


# ---------------------------------------------------------------------------
# Data API — consumed by the frontend charts via fetch()
# ---------------------------------------------------------------------------

@router.get("/dashboard/data")
async def dashboard_data(window: int = 3600, bucket: int = 30) -> dict:
    """Return time-bucketed metrics for all 6 dashboard panels.

    Query params:
        window: look-back window in seconds (default 3600 = 1 h)
        bucket: bucket size in seconds (default 30)
    """
    return timeseries_data(window_seconds=window, bucket_seconds=bucket)


# ---------------------------------------------------------------------------
# Dashboard HTML page
# ---------------------------------------------------------------------------

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page() -> str:
    return DASHBOARD_HTML


# ===================================================================
# HTML source — self-contained single-page dashboard
# Uses Chart.js 4.x + chartjs-plugin-annotation for SLO lines
# Auto-refreshes every 15 s, default time range 1 h
# ===================================================================

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Day 13 Observability Dashboard</title>
<meta name="description" content="Real-time observability dashboard for Day 13 AI Agent — Latency, Traffic, Errors, Cost, Tokens, Quality">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js"></script>
<style>
/* ========== RESET & BASE ========== */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg-primary:#0a0a1a;
  --bg-secondary:#111128;
  --bg-card:rgba(17,17,40,0.72);
  --border:rgba(255,255,255,0.06);
  --border-hover:rgba(255,255,255,0.12);
  --text-1:#f0f0f5;
  --text-2:#9191b0;
  --text-3:#5c5c80;
  --cyan:#06b6d4;
  --amber:#f59e0b;
  --red:#ef4444;
  --green:#10b981;
  --emerald:#34d399;
  --purple:#8b5cf6;
  --blue:#3b82f6;
  --violet:#a78bfa;
  --orange:#f97316;
  --pink:#ec4899;
  --teal:#14b8a6;
  --font-sans:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  --font-mono:'JetBrains Mono','Fira Code',monospace;
  --radius:16px;
  --radius-sm:8px;
}
body{
  font-family:var(--font-sans);
  background:var(--bg-primary);
  color:var(--text-1);
  min-height:100vh;
  overflow-x:hidden;
}
/* ambient glow orbs */
body::before,body::after{content:'';position:fixed;width:600px;height:600px;border-radius:50%;pointer-events:none;z-index:0}
body::before{top:-250px;left:-200px;background:radial-gradient(circle,rgba(6,182,212,0.07),transparent 70%)}
body::after{bottom:-250px;right:-200px;background:radial-gradient(circle,rgba(139,92,246,0.07),transparent 70%)}

.container{max-width:1480px;margin:0 auto;padding:24px 32px;position:relative;z-index:1}

/* ========== HEADER ========== */
.header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.header-left{display:flex;align-items:center;gap:14px}
.header-title{font-size:22px;font-weight:700;background:linear-gradient(135deg,var(--cyan),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.header-badge{background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.2);color:var(--cyan);padding:4px 12px;border-radius:20px;font-size:11px;font-weight:500;letter-spacing:.5px}
.header-right{display:flex;align-items:center;gap:10px}
.time-btn{background:var(--bg-card);border:1px solid var(--border);color:var(--text-2);padding:5px 14px;border-radius:var(--radius-sm);font-size:12px;font-family:var(--font-sans);cursor:pointer;transition:all .2s}
.time-btn:hover{border-color:var(--cyan);color:var(--text-1)}
.time-btn.active{background:rgba(6,182,212,0.15);border-color:var(--cyan);color:var(--cyan)}
.refresh-ind{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text-3);font-family:var(--font-mono)}
.refresh-dot{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}

/* ========== SUMMARY ROW ========== */
.summary-row{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:22px}
.s-card{background:var(--bg-card);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;position:relative;overflow:hidden;transition:all .3s}
.s-card:hover{border-color:var(--border-hover);transform:translateY(-2px)}
.s-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:var(--radius) var(--radius) 0 0}
.s-card[data-st="ok"]::before{background:var(--green)}
.s-card[data-st="warn"]::before{background:var(--amber)}
.s-card[data-st="crit"]::before{background:var(--red)}
.s-label{font-size:11px;color:var(--text-3);text-transform:uppercase;letter-spacing:.7px;margin-bottom:6px}
.s-val{font-size:26px;font-weight:700;font-family:var(--font-mono);line-height:1.2}
.s-unit{font-size:13px;font-weight:400;color:var(--text-2);margin-left:3px}
.s-slo{font-size:10px;color:var(--text-3);margin-top:5px;font-family:var(--font-mono)}
.slo-ok{color:var(--green)!important}
.slo-breach{color:var(--red)!important}

/* ========== CHART GRID ========== */
.charts-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.c-card{background:var(--bg-card);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid var(--border);border-radius:var(--radius);padding:22px 24px;transition:border-color .3s}
.c-card:hover{border-color:var(--border-hover)}
.c-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.c-title{font-size:13px;font-weight:600;display:flex;align-items:center;gap:8px}
.c-icon{font-size:15px}
.c-badge{font-size:11px;font-family:var(--font-mono);padding:3px 10px;border-radius:6px;font-weight:500}
.c-wrap{position:relative;height:220px}

/* ========== FOOTER ========== */
.footer{margin-top:20px;padding:14px 0;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-3)}
.footer-slo{font-family:var(--font-mono)}

/* ========== RESPONSIVE ========== */
@media(max-width:1200px){.summary-row{grid-template-columns:repeat(3,1fr)}}
@media(max-width:900px){.charts-grid{grid-template-columns:1fr}.summary-row{grid-template-columns:repeat(2,1fr)}.container{padding:16px}}
@media(max-width:600px){.summary-row{grid-template-columns:1fr}.header{flex-direction:column;align-items:flex-start}}

/* ========== ANIMATIONS ========== */
.c-card,.s-card{animation:fadeUp .5s ease-out both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.c-card:nth-child(1){animation-delay:.0s}
.c-card:nth-child(2){animation-delay:.05s}
.c-card:nth-child(3){animation-delay:.1s}
.c-card:nth-child(4){animation-delay:.15s}
.c-card:nth-child(5){animation-delay:.2s}
.c-card:nth-child(6){animation-delay:.25s}
</style>
</head>
<body>
<div class="container">
  <!-- ===== HEADER ===== -->
  <header class="header">
    <div class="header-left">
      <h1 class="header-title">&#128301; Observability Dashboard</h1>
      <span class="header-badge">day13-observability-lab</span>
    </div>
    <div class="header-right">
      <button class="time-btn active" data-w="3600" data-b="30">1 h</button>
      <button class="time-btn" data-w="21600" data-b="180">6 h</button>
      <button class="time-btn" data-w="86400" data-b="720">24 h</button>
      <div class="refresh-ind"><span class="refresh-dot"></span><span id="ref-lbl">auto-refresh 15 s</span></div>
    </div>
  </header>

  <!-- ===== SUMMARY ROW ===== -->
  <div class="summary-row">
    <div class="s-card" id="sc-traffic" data-st="ok">
      <div class="s-label">Total Traffic</div>
      <div class="s-val" id="sv-traffic">0<span class="s-unit">req</span></div>
      <div class="s-slo">since server start</div>
    </div>
    <div class="s-card" id="sc-latency" data-st="ok">
      <div class="s-label">Latency P95</div>
      <div class="s-val" id="sv-latency">0<span class="s-unit">ms</span></div>
      <div class="s-slo">SLO: <span id="sl-lat">&lt; 3 000 ms</span></div>
    </div>
    <div class="s-card" id="sc-error" data-st="ok">
      <div class="s-label">Error Rate</div>
      <div class="s-val" id="sv-error">0.0<span class="s-unit">%</span></div>
      <div class="s-slo">SLO: <span id="sl-err">&lt; 2 %</span></div>
    </div>
    <div class="s-card" id="sc-cost" data-st="ok">
      <div class="s-label">Total Cost</div>
      <div class="s-val" id="sv-cost">$0.00<span class="s-unit">USD</span></div>
      <div class="s-slo">SLO: <span id="sl-cost">&lt; $2.50 / day</span></div>
    </div>
    <div class="s-card" id="sc-quality" data-st="ok">
      <div class="s-label">Avg Quality</div>
      <div class="s-val" id="sv-quality">0.00<span class="s-unit">/ 1.0</span></div>
      <div class="s-slo">SLO: <span id="sl-qual">&gt; 0.75</span></div>
    </div>
  </div>

  <!-- ===== CHART GRID (6 panels) ===== -->
  <div class="charts-grid">
    <!-- 1  Latency P50 / P95 / P99 -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#128202;</span>Latency P50 / P95 / P99</div>
        <span class="c-badge" id="bg-lat" style="background:rgba(6,182,212,.12);color:#06b6d4">-- ms</span>
      </div>
      <div class="c-wrap"><canvas id="ch-lat"></canvas></div>
    </div>
    <!-- 2  Traffic -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#128200;</span>Traffic (Requests)</div>
        <span class="c-badge" id="bg-trf" style="background:rgba(139,92,246,.12);color:#8b5cf6">-- req</span>
      </div>
      <div class="c-wrap"><canvas id="ch-trf"></canvas></div>
    </div>
    <!-- 3  Error Rate -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#9888;&#65039;</span>Error Rate with Breakdown</div>
        <span class="c-badge" id="bg-err" style="background:rgba(239,68,68,.12);color:#ef4444">-- %</span>
      </div>
      <div class="c-wrap"><canvas id="ch-err"></canvas></div>
    </div>
    <!-- 4  Cost -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#128176;</span>Cost Over Time (USD)</div>
        <span class="c-badge" id="bg-cst" style="background:rgba(16,185,129,.12);color:#10b981">$--</span>
      </div>
      <div class="c-wrap"><canvas id="ch-cst"></canvas></div>
    </div>
    <!-- 5  Tokens In / Out -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#128289;</span>Tokens In / Out</div>
        <span class="c-badge" id="bg-tok" style="background:rgba(59,130,246,.12);color:#3b82f6">-- tok</span>
      </div>
      <div class="c-wrap"><canvas id="ch-tok"></canvas></div>
    </div>
    <!-- 6  Quality Proxy -->
    <div class="c-card">
      <div class="c-head">
        <div class="c-title"><span class="c-icon">&#11088;</span>Quality Score (Heuristic Proxy)</div>
        <span class="c-badge" id="bg-qlty" style="background:rgba(52,211,153,.12);color:#34d399">--</span>
      </div>
      <div class="c-wrap"><canvas id="ch-qlty"></canvas></div>
    </div>
  </div>

  <!-- ===== FOOTER ===== -->
  <footer class="footer">
    <div>Last refreshed: <span id="last-ref">--</span></div>
    <div class="footer-slo">SLO source: config/slo.yaml &nbsp;|&nbsp; Window: 28 d</div>
  </footer>
</div>

<!-- ========================================================================
     JAVASCRIPT — Chart.js setup, data fetching, auto-refresh
     ======================================================================== -->
<script>
/* -------- Chart.js global defaults -------- */
Chart.defaults.color='#9191b0';
Chart.defaults.borderColor='rgba(255,255,255,0.04)';
Chart.defaults.font.family="'Inter',sans-serif";
Chart.defaults.font.size=11;
Chart.defaults.elements.line.tension=0.35;
Chart.defaults.elements.point.radius=0;
Chart.defaults.elements.point.hoverRadius=4;
Chart.defaults.plugins.legend.labels.usePointStyle=true;
Chart.defaults.plugins.legend.labels.pointStyleWidth=8;
Chart.defaults.plugins.legend.labels.padding=14;
Chart.defaults.plugins.tooltip.backgroundColor='rgba(10,10,26,0.92)';
Chart.defaults.plugins.tooltip.titleFont={weight:'600'};
Chart.defaults.plugins.tooltip.bodyFont={size:11};
Chart.defaults.plugins.tooltip.padding=10;
Chart.defaults.plugins.tooltip.cornerRadius=8;
Chart.defaults.plugins.tooltip.borderColor='rgba(255,255,255,0.08)';
Chart.defaults.plugins.tooltip.borderWidth=1;

/* -------- State -------- */
let W=3600,B=30;
const REFRESH_MS=15000;
let refreshTimer=null;
const charts={};

/* -------- SLO annotation helper -------- */
function sloLine(val,label,col='rgba(239,68,68,0.65)'){
  return{type:'line',yMin:val,yMax:val,borderColor:col,borderWidth:2,borderDash:[8,4],
    label:{display:true,content:label,position:'start',backgroundColor:col,color:'#fff',
      font:{size:9,weight:'600',family:"'Inter',sans-serif"},padding:{x:6,y:3},borderRadius:4}};
}

/* -------- Shared axis helpers -------- */
function xAxis(){return{title:{display:true,text:'Time',color:'#5c5c80',font:{size:10}},ticks:{maxTicksLimit:10,font:{size:9}}}}
function yAxis(txt){return{title:{display:true,text:txt,color:'#5c5c80',font:{size:10}},beginAtZero:true,ticks:{font:{size:9}}}}

/* ====================================================================
   CREATE CHARTS
   ==================================================================== */
function createCharts(){
  /* 1. Latency */
  charts.lat=new Chart(document.getElementById('ch-lat'),{type:'line',
    data:{labels:[],datasets:[
      {label:'P50',data:[],borderColor:'#06b6d4',backgroundColor:'rgba(6,182,212,0.08)',fill:false,borderWidth:2},
      {label:'P95',data:[],borderColor:'#f59e0b',backgroundColor:'rgba(245,158,11,0.08)',fill:false,borderWidth:2},
      {label:'P99',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.08)',fill:false,borderWidth:2}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:yAxis('Latency (ms)'),x:xAxis()},
      plugins:{annotation:{annotations:{slo:sloLine(3000,'SLO: P95 < 3 000 ms')}}}}
  });

  /* 2. Traffic */
  charts.trf=new Chart(document.getElementById('ch-trf'),{type:'bar',
    data:{labels:[],datasets:[
      {label:'Requests',data:[],backgroundColor:'rgba(139,92,246,0.55)',borderColor:'#8b5cf6',borderWidth:1,borderRadius:3,maxBarThickness:18}
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:yAxis('Request Count'),x:xAxis()}}
  });

  /* 3. Error Rate */
  charts.err=new Chart(document.getElementById('ch-err'),{type:'line',
    data:{labels:[],datasets:[
      {label:'Error Rate',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.12)',fill:true,borderWidth:2}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:Object.assign(yAxis('Error Rate (%)'),{suggestedMax:10}),x:xAxis()},
      plugins:{annotation:{annotations:{slo:sloLine(2,'SLO: < 2 %','rgba(245,158,11,0.75)')}}}}
  });

  /* 4. Cost */
  charts.cst=new Chart(document.getElementById('ch-cst'),{type:'line',
    data:{labels:[],datasets:[
      {label:'Cumulative Cost',data:[],borderColor:'#10b981',backgroundColor:'rgba(16,185,129,0.10)',fill:true,borderWidth:2},
      {label:'Per Interval',data:[],borderColor:'#34d399',backgroundColor:'transparent',fill:false,borderWidth:1,borderDash:[4,2]}
    ]},
    options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
      scales:{y:yAxis('Cost (USD)'),x:xAxis()},
      plugins:{annotation:{annotations:{slo:sloLine(2.5,'SLO: < $2.50 / day','rgba(245,158,11,0.75)')}}}}
  });

  /* 5. Tokens */
  charts.tok=new Chart(document.getElementById('ch-tok'),{type:'bar',
    data:{labels:[],datasets:[
      {label:'Tokens In',data:[],backgroundColor:'rgba(59,130,246,0.55)',borderColor:'#3b82f6',borderWidth:1,borderRadius:3,maxBarThickness:18},
      {label:'Tokens Out',data:[],backgroundColor:'rgba(167,139,250,0.55)',borderColor:'#a78bfa',borderWidth:1,borderRadius:3,maxBarThickness:18}
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:Object.assign(yAxis('Token Count'),{stacked:true}),x:Object.assign(xAxis(),{stacked:true})}}
  });

  /* 6. Quality */
  charts.qlty=new Chart(document.getElementById('ch-qlty'),{type:'line',
    data:{labels:[],datasets:[
      {label:'Avg Quality',data:[],borderColor:'#34d399',backgroundColor:'rgba(52,211,153,0.10)',fill:true,borderWidth:2}
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      scales:{y:Object.assign(yAxis('Quality Score (0 – 1)'),{max:1.0}),x:xAxis()},
      plugins:{annotation:{annotations:{slo:sloLine(0.75,'SLO: > 0.75','rgba(16,185,129,0.70)')}}}}
  });
}

/* ====================================================================
   FETCH & UPDATE
   ==================================================================== */
const BREAKDOWN_COLORS=['#f97316','#a855f7','#ec4899','#14b8a6','#eab308','#64748b'];

async function fetchAndUpdate(){
  try{
    const r=await fetch('/dashboard/data?window='+W+'&bucket='+B);
    const d=await r.json();
    const s=d.summary, slo=d.slo;

    /* --- Charts --- */
    // 1 Latency
    charts.lat.data.labels=d.labels;
    charts.lat.data.datasets[0].data=d.latency.p50;
    charts.lat.data.datasets[1].data=d.latency.p95;
    charts.lat.data.datasets[2].data=d.latency.p99;
    charts.lat.update('none');

    // 2 Traffic
    charts.trf.data.labels=d.labels;
    charts.trf.data.datasets[0].data=d.traffic.counts;
    charts.trf.update('none');

    // 3 Error Rate + breakdown
    charts.err.data.labels=d.labels;
    charts.err.data.datasets[0].data=d.errors.rates;
    // dynamic breakdown datasets
    while(charts.err.data.datasets.length>1) charts.err.data.datasets.pop();
    let ci=0;
    for(const[tp,counts]of Object.entries(d.errors.breakdown)){
      charts.err.data.datasets.push({label:tp,data:counts,
        borderColor:BREAKDOWN_COLORS[ci%BREAKDOWN_COLORS.length],
        backgroundColor:BREAKDOWN_COLORS[ci%BREAKDOWN_COLORS.length]+'33',
        fill:true,borderWidth:1,pointRadius:0});
      ci++;
    }
    charts.err.update('none');

    // 4 Cost
    charts.cst.data.labels=d.labels;
    charts.cst.data.datasets[0].data=d.cost.cumulative;
    charts.cst.data.datasets[1].data=d.cost.per_bucket;
    charts.cst.update('none');

    // 5 Tokens
    charts.tok.data.labels=d.labels;
    charts.tok.data.datasets[0].data=d.tokens.in;
    charts.tok.data.datasets[1].data=d.tokens.out;
    charts.tok.update('none');

    // 6 Quality
    charts.qlty.data.labels=d.labels;
    charts.qlty.data.datasets[0].data=d.quality.avg;
    charts.qlty.update('none');

    /* --- Badges --- */
    document.getElementById('bg-lat').textContent='P95: '+s.latency_p95.toFixed(0)+' ms';
    document.getElementById('bg-trf').textContent=s.traffic+' req';
    const totErr=Object.values(s.error_breakdown).reduce((a,b)=>a+b,0);
    const errRate=s.traffic>0?(totErr/(s.traffic+totErr)*100).toFixed(1):'0.0';
    document.getElementById('bg-err').textContent=errRate+' %';
    document.getElementById('bg-cst').textContent='$'+s.total_cost_usd.toFixed(4);
    document.getElementById('bg-tok').textContent=(s.tokens_in_total+s.tokens_out_total).toLocaleString()+' tok';
    document.getElementById('bg-qlty').textContent=s.quality_avg.toFixed(3);

    /* --- Summary cards --- */
    document.getElementById('sv-traffic').innerHTML=s.traffic+'<span class="s-unit">req</span>';
    document.getElementById('sv-latency').innerHTML=s.latency_p95.toFixed(0)+'<span class="s-unit">ms</span>';
    document.getElementById('sv-error').innerHTML=errRate+'<span class="s-unit">%</span>';
    document.getElementById('sv-cost').innerHTML='$'+s.total_cost_usd.toFixed(4)+'<span class="s-unit">USD</span>';
    document.getElementById('sv-quality').innerHTML=s.quality_avg.toFixed(3)+'<span class="s-unit">/ 1.0</span>';

    /* --- SLO status indicators --- */
    setStatus('sc-latency','sl-lat',s.latency_p95<=slo.latency_p95_ms);
    setStatus('sc-error','sl-err',parseFloat(errRate)<=slo.error_rate_pct);
    setStatus('sc-cost','sl-cost',s.total_cost_usd<=slo.daily_cost_usd);
    setStatus('sc-quality','sl-qual',s.quality_avg>=slo.quality_score_avg);

    document.getElementById('last-ref').textContent=new Date().toLocaleTimeString();
  }catch(e){console.error('Dashboard fetch error:',e);}
}

function setStatus(cardId,sloId,ok){
  document.getElementById(cardId).dataset.st=ok?'ok':'crit';
  const el=document.getElementById(sloId);
  if(el) el.className=ok?'slo-ok':'slo-breach';
}

/* ====================================================================
   TIME RANGE BUTTONS & INIT
   ==================================================================== */
document.querySelectorAll('.time-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    document.querySelectorAll('.time-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    W=parseInt(btn.dataset.w);
    B=parseInt(btn.dataset.b);
    fetchAndUpdate();
  });
});

createCharts();
fetchAndUpdate();
refreshTimer=setInterval(fetchAndUpdate,REFRESH_MS);
</script>
</body>
</html>
"""
