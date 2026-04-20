# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 
- [REPO_URL]: 
- [MEMBERS]:
  - Member A: [Name] | Role: Logging & PII
  - Member B: [Name] | Role: Tracing & Enrichment
  - Member C: [Name] | Role: SLO & Alerts
  - Member D: [Nguyễn Thế Anh] | Role: Load Test & Dashboard
  - Member E: [Name] | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]: 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Path to image]
- [TRACE_WATERFALL_EXPLANATION]: (Briefly explain one interesting span in your trace)

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- **Dashboard URL**: `/dashboard` (served by `app/dashboard.py`)
- **Panels implemented**: 6 / 6
  1. **Latency P50/P95/P99** — Line chart with SLO annotation at 3 000 ms
  2. **Traffic (Requests)** — Bar chart showing request count per bucket
  3. **Error Rate with Breakdown** — Line chart (fill) + dynamic per-error-type breakdown, SLO at 2 %
  4. **Cost Over Time** — Cumulative + per-interval lines, SLO at $2.50/day
  5. **Tokens In/Out** — Stacked bar chart
  6. **Quality Score (Heuristic Proxy)** — Line chart (fill), SLO at 0.75
- **Auto-refresh**: every 15 seconds
- **Default time range**: 1 hour (selectable: 1 h / 6 h / 24 h)
- **SLO/threshold lines**: visible and labeled via `chartjs-plugin-annotation` on Latency, Error Rate, Cost, Quality panels
- **SLO source**: `config/slo.yaml` — reviewed and enriched with `unit` and `note` fields
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000 ms | 28d | *(live on dashboard)* |
| Error Rate | < 2% | 28d | *(live on dashboard)* |
| Cost Budget | < $2.50/day | 1d | *(live on dashboard)* |
| Quality Score | > 0.75 | 28d | *(live on dashboard)* |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Path to image]
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#L...]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: (e.g., rag_slow)
- [SYMPTOMS_OBSERVED]: 
- [ROOT_CAUSE_PROVED_BY]: (List specific Trace ID or Log Line)
- [FIX_ACTION]: 
- [PREVENTIVE_MEASURE]: 

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: (Link to specific commit or PR)

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### Nguyễn Thế Anh (Member D — Dashboard & SLO Owner)
- [TASKS_COMPLETED]:
  - **Step 7 — Dashboards**: Implemented the full 6-panel observability dashboard
  - Created `app/dashboard.py` — self-contained HTML dashboard served at `/dashboard` using Chart.js 4.x + `chartjs-plugin-annotation`
  - Enhanced `app/metrics.py` — added `TimeSeriesRecord` / `ErrorTimeRecord` dataclasses and `timeseries_data()` aggregation function for time-bucketed chart data
  - Created `/dashboard/data` API endpoint returning JSON metrics consumed by frontend charts
  - Implemented all 6 required panels: Latency P50/P95/P99, Traffic, Error Rate w/ breakdown, Cost over time, Tokens In/Out, Quality Score
  - Added SLO/threshold annotation lines on relevant panels (Latency: 3000 ms, Error Rate: 2%, Cost: $2.50/day, Quality: 0.75)
  - Auto-refresh every 15 s with selectable time ranges (1 h / 6 h / 24 h)
  - Reviewed and enriched `config/slo.yaml` with `unit` and `note` fields for each SLI
  - Integrated dashboard router into `app/main.py` via `app.include_router(dashboard_router)`
  - Summary cards with live SLO status indicators (green/red) and responsive grid layout
  - Premium dark-theme UI with glassmorphism, Inter/JetBrains Mono fonts, fade-up animations
- [EVIDENCE_LINK]: See `app/dashboard.py`, `app/metrics.py`, `config/slo.yaml`, `app/main.py` (line 15 & 23)

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
