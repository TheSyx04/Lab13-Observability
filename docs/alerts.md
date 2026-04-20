# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 5m`
- Impact: tail latency breaches SLO
- Signal source: dashboard latency panel (`/dashboard/data`, p95 series)
- First checks:
  1. Metrics: confirm sustained p95 spike in the last 5-10 minutes.
  2. Traces: open the slowest traces and compare RAG span vs LLM span.
  3. Logs: filter `event=request_received|response_sent` by same `correlation_id`.
  4. Control plane: verify whether `rag_slow` is enabled in `/health`.
- Mitigation:
  - disable incident toggle: `python scripts/inject_incident.py --scenario rag_slow --disable`
  - truncate long queries
  - fallback retrieval source
  - lower prompt size
- Recovery criteria:
  - p95 returns under 3000 ms for 10 minutes
  - no newly created slow traces with dominant RAG span

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: users receive failed responses
- Signal source: dashboard error-rate panel + error breakdown
- First checks:
  1. Metrics: verify error rate and top error bucket.
  2. Logs: group failed requests by `error_type`.
  3. Traces: inspect failed traces around the same time window.
  4. Check whether `tool_fail` incident was enabled.
- Mitigation:
  - disable incident toggle: `python scripts/inject_incident.py --scenario tool_fail --disable`
  - rollback latest change
  - disable failing tool
  - retry with fallback model
- Recovery criteria:
  - error rate below 2% for at least 10 minutes
  - no repeated `request_failed` bursts in logs

## 3. Cost budget spike
- Severity: P2
- Trigger: `avg_cost_usd > 0.004 for 10m OR tokens_out_total growth > 2x baseline`
- Impact: burn rate exceeds budget
- Signal source: dashboard cost and tokens panels
- First checks:
  1. Metrics: confirm jump in average cost and tokens out.
  2. Traces: split by feature/model and inspect heavy token traces.
  3. Logs: compare `tokens_in` and `tokens_out` for the same correlation IDs.
  4. Check whether `cost_spike` incident was enabled.
- Mitigation:
  - disable incident toggle: `python scripts/inject_incident.py --scenario cost_spike --disable`
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache
- Recovery criteria:
  - avg cost returns to baseline range
  - tokens_out distribution normalizes for 15 minutes

## Alert Test Drill (Step 8 evidence)
1. Start service and generate baseline traffic:
   - `python scripts/load_test.py --concurrency 5`
2. Enable one incident scenario:
   - Latency: `python scripts/inject_incident.py --scenario rag_slow`
   - Error: `python scripts/inject_incident.py --scenario tool_fail`
   - Cost: `python scripts/inject_incident.py --scenario cost_spike`
3. Generate traffic again and capture:
   - dashboard screenshots,
   - one trace waterfall,
   - matching logs by `correlation_id`.
4. Disable the incident and verify recovery:
   - `python scripts/inject_incident.py --scenario <name> --disable`
5. Document one full root-cause path in `docs/blueprint-template.md`:
   - Metrics -> Traces -> Logs -> Fix -> Prevention.
