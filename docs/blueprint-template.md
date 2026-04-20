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
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | |
| Error Rate | < 2% | 28d | |
| Cost Budget | < $2.5/day | 1d | |

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
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: [Link to commit](https://github.com/TheSyx04/Lab13-Observability/commit/4117b11384c3bab91330df5c45b843a7b270b1ae)

### [Nguyễn Thế Anh]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

### [Ngô Quang Tăng]
- [TASKS_COMPLETED]: 
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
