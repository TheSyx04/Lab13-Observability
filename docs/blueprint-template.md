# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME] : 26
- [REPO_URL] : https://github.com/TheSyx04/Lab13-Observability.git
- [MEMBERS] : 
  - Member A: [Trần Sỹ Minh Quân] | Role: Platform and Correlation ID Owner
  - Member B: [Vũ Đức Minh] | Role: Logging Enrichment and PII Owner
  - Member C: [Phạm Minh Khôi] | Role: Verification and Tracing Owner
  - Member D: [Nguyễn Thế Anh] | Role: Dashboard and SLO Owner
  - Member E: [Ngô Quang Tăng] | Role: Alerting, Incident Response, and Submission Owner

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE] : 100/100
- [TOTAL_TRACES_COUNT] : 10
- [PII_LEAKS_FOUND] : 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Path to image]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Path to image]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [evidence\trace_waterfall.jpg]
- [TRACE_WATERFALL_EXPLANATION] : In the Langfuse run detail, one waterfall shows total latency 0.15s, with output metrics `latency_ms=142`, `tokens_in=29`, `tokens_out=120`, `cost_usd=0.001887`, and `quality_score=0.9`.

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

### [Trần Sỹ Minh Quân]
- [TASKS_COMPLETED]: Completed Step 1 (starter app setup and baseline verification) and Step 2 (correlation ID middleware): created and activated virtual environment, installed dependencies, verified `/health` and `/chat`, implemented request correlation propagation (incoming `x-request-id` or generated `req-<8-char-hex>`), ensured response headers `x-request-id` and `x-response-time-ms`, and verified API logs contain non-`MISSING` `correlation_id`.
- [EVIDENCE_LINK]: [Link to commit](https://github.com/TheSyx04/Lab13-Observability/commit/5dcb62c304d147978fc5f8dc014e75e435e16c6a)

### [Vũ Đức Minh]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: [Link to commit](https://github.com/TheSyx04/Lab13-Observability/commit/cb44249cc7d03ec655e611a939361828e09807ac)

### [Phạm Minh Khôi]
- [TASKS_COMPLETED]: Chạy script giả lập tải (load_test.py) và kiểm tra tính hợp lệ của Logs (validate_logs.py), đảm bảo hệ thống đạt 100/100 điểm đánh giá tự động (Không rò rỉ PII, đủ Correlation ID và Context).Phát hiện lỗi không tương thích phiên bản của Langfuse (code cũ v2 vs thư viện v4) khiến hệ thống mất dấu vết. Trực tiếp refactor lại mã nguồn (app/agent.py và app/tracing.py) để tương thích với Langfuse v4. Cấu hình thành công môi trường, thu thập hơn 10 traces hoàn chỉnh với biểu đồ Waterfall trên Langfuse.
- [EVIDENCE_LINK]: [Link to commit](https://github.com/TheSyx04/Lab13-Observability/commit/4117b11384c3bab91330df5c45b843a7b270b1ae)

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

### [Ngô Quang Tăng]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
