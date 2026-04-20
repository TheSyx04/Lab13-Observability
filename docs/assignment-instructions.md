# Day 13 Observability Lab - 8-Step Assignment Instructions

This version is organized to match the README suggested lab flow exactly.

## Step 1) Run the starter app
Goal: bring up the baseline system and confirm current gaps.

Do:
1. Create and activate virtual env.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env`.
4. (Optional but recommended) fill Langfuse keys in `.env`:
  - `LANGFUSE_PUBLIC_KEY`
  - `LANGFUSE_SECRET_KEY`
5. Run app: `uvicorn app.main:app --reload`.
6. Check `/health` and send a few `/chat` requests.

Observe:
- logs are basic at first
- correlation id may be missing (`MISSING`)

## Step 2) Implement Correlation IDs
Primary file: `app/middleware.py`

Complete all TODOs:
- clear contextvars at request start
- use incoming `x-request-id` or generate one as `req-<8-char-hex>`
- bind `correlation_id` to structlog contextvars
- attach `x-request-id` and `x-response-time-ms` to response headers

Done when:
- each request has a stable correlation id
- API logs include non-`MISSING` `correlation_id`

## Step 3) Enrich logs with request context
Primary file: `app/main.py`

Complete TODO in `/chat` by binding context fields:
- `user_id_hash` (via `hash_user_id`)
- `session_id`
- `feature`
- `model`
- `env`

Done when:
- API logs include enrichment fields required by validator (`user_id_hash`, `session_id`, `feature`, `model`)

## Step 4) Sanitize data (PII scrubbing)
Primary files: `app/logging_config.py`, `app/pii.py`

Complete TODOs:
- register `scrub_event` in logging processor chain before render/output
- extend `PII_PATTERNS` with additional patterns (e.g., passport, VN address keywords)

Done when:
- event text and payload strings are redacted
- no obvious PII appears in logs
- tests still pass (`tests/test_pii.py`)

## Step 5) Verify with script
Primary script: `scripts/validate_logs.py`

Generate traffic first:
- `python scripts/load_test.py`
- optional: `python scripts/load_test.py --concurrency 5`

Run validator:
- `python scripts/validate_logs.py`

Target checks:
- required JSON fields present
- correlation id propagation works
- enrichment fields present
- no PII hits (`@` or test card pattern)
- estimated score reaches at least 80/100

## Step 6) Tracing (Langfuse)
Primary files: `app/agent.py`, `app/tracing.py`

Do:
1. Ensure Langfuse env keys are set.
2. Send 10-20 requests (load test is fine).
3. Verify in Langfuse:
  - at least 10 traces
  - trace metadata/tags present
  - one full waterfall trace is inspectable

Notes:
- `@observe()` is already used in agent pipeline
- if keys are missing, tracing falls back to dummy context

## Step 7) Dashboards
Build exactly these 6 required panels:
1. Latency P50/P95/P99
2. Traffic (count or QPS)
3. Error rate with breakdown
4. Cost over time
5. Tokens in/out
6. Quality proxy

Dashboard quality bar:
- default time range: 1h
- refresh every 15-30s
- include visible SLO/threshold lines
- label units clearly
- keep main view within 6-8 panels

SLO source:
- review/update `config/slo.yaml` and reflect values in your report

## Step 8) Alerting
Primary files: `config/alert_rules.yaml`, `docs/alerts.md`

Do:
- maintain at least 3 alert rules
- each alert includes severity, condition, owner, runbook link
- ensure runbook anchors resolve correctly

Test alert readiness with incident injection:
- enable: `python scripts/inject_incident.py --scenario rag_slow`
- disable: `python scripts/inject_incident.py --scenario rag_slow --disable`
- optional scenarios: `tool_fail`, `cost_spike`

Done when:
- your team can explain debugging flow: Metrics -> Traces -> Logs
- root cause is proven with concrete trace/log evidence

---

## Team split for 5 members (sequential execution)

Use this handoff order so work is parallel-safe but still sequential by dependency.

### Member 1
Role: Platform and Correlation ID Owner

Owns steps:
- Step 1) Run the starter app
- Step 2) Implement Correlation IDs

Handoff to Member 2 when:
- app is running stably
- correlation id appears in API logs and response headers

### Member 2
Role: Logging Enrichment and PII Owner

Owns steps:
- Step 3) Enrich logs with request context
- Step 4) Sanitize data (PII scrubbing)

Handoff to Member 3 when:
- API logs include enrichment fields (`user_id_hash`, `session_id`, `feature`, `model`)
- obvious PII is redacted from event/payload logs

### Member 3
Role: Verification and Tracing Owner

Owns steps:
- Step 5) Verify with script
- Step 6) Tracing (Langfuse)

Handoff to Member 4 when:
- `python scripts/validate_logs.py` reaches at least 80/100
- Langfuse shows at least 10 traces and one valid waterfall trace

### Member 4
Role: Dashboard and SLO Owner

Owns step:
- Step 7) Dashboards

Handoff to Member 5 when:
- dashboard has all 6 required panels
- SLO/threshold lines are visible and units are clearly labeled

### Member 5
Role: Alerting, Incident Response, and Submission Owner

Owns step:
- Step 8) Alerting

Also owns finalization:
- incident injection drill and root-cause narrative
- evidence collection and screenshot completeness
- final report completion in `docs/blueprint-template.md`
- commit/PR evidence check for all members

Final gate before submission:
- all TODOs completed
- score >= 80/100
- >= 10 traces
- 6-panel dashboard
- 3+ alerts with working runbook links

---

## Final deliverables (submit after Step 8)
1. Passing gate:
  - all code TODOs completed
  - `VALIDATE_LOGS_SCORE >= 80/100`
  - >= 10 Langfuse traces
  - dashboard has all 6 required panels

2. Evidence screenshots (from `docs/grading-evidence.md`):
  - trace list (>= 10)
  - one trace waterfall
  - JSON logs with correlation id
  - PII redaction example
  - dashboard with 6 panels
  - alert rules with runbook link

3. Final report:
  - fully fill `docs/blueprint-template.md`
  - include incident response section
  - include individual commit/PR evidence for each member

4. Useful final checks:
  - `pytest`
  - `python scripts/validate_logs.py`
