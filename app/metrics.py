from __future__ import annotations

import datetime
import time
from collections import Counter
from dataclasses import dataclass
from statistics import mean

# ---------------------------------------------------------------------------
# Time-series record types (added for dashboard charts)
# ---------------------------------------------------------------------------

@dataclass
class TimeSeriesRecord:
    """A single successful request record with timestamp."""
    timestamp: float
    latency_ms: int
    cost_usd: float
    tokens_in: int
    tokens_out: int
    quality_score: float


@dataclass
class ErrorTimeRecord:
    """A single error record with timestamp."""
    timestamp: float
    error_type: str


# ---------------------------------------------------------------------------
# Aggregate storage (original interface — kept for backward compatibility)
# ---------------------------------------------------------------------------
REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []

# ---------------------------------------------------------------------------
# Time-series storage
# ---------------------------------------------------------------------------
TIMESERIES: list[TimeSeriesRecord] = []
ERROR_TIMESERIES: list[ErrorTimeRecord] = []


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    # Also record for time-series dashboard
    TIMESERIES.append(TimeSeriesRecord(
        timestamp=time.time(),
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        quality_score=quality_score,
    ))



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1
    # Also record for time-series dashboard
    ERROR_TIMESERIES.append(ErrorTimeRecord(
        timestamp=time.time(),
        error_type=error_type,
    ))



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }


# ---------------------------------------------------------------------------
# Time-series aggregation for dashboard
# ---------------------------------------------------------------------------

def timeseries_data(window_seconds: int = 3600, bucket_seconds: int = 30) -> dict:
    """Return time-bucketed metrics for dashboard charts.

    Args:
        window_seconds: Time window to look back (default: 3600 = 1 hour).
        bucket_seconds: Size of each time bucket (default: 30 seconds).

    Returns:
        Dictionary with time-series data for all 6 dashboard panels plus SLOs.
    """
    now = time.time()
    start = now - window_seconds
    num_buckets = max(1, window_seconds // bucket_seconds)

    # Initialize buckets
    bucket_records: list[list[TimeSeriesRecord]] = [[] for _ in range(num_buckets)]
    bucket_errors: list[list[ErrorTimeRecord]] = [[] for _ in range(num_buckets)]

    # Assign records to buckets
    for record in TIMESERIES:
        if record.timestamp < start:
            continue
        idx = min(int((record.timestamp - start) / bucket_seconds), num_buckets - 1)
        if idx >= 0:
            bucket_records[idx].append(record)

    # Assign errors to buckets
    for error in ERROR_TIMESERIES:
        if error.timestamp < start:
            continue
        idx = min(int((error.timestamp - start) / bucket_seconds), num_buckets - 1)
        if idx >= 0:
            bucket_errors[idx].append(error)

    # Build per-bucket data arrays
    labels: list[str] = []
    latency_p50: list[float] = []
    latency_p95: list[float] = []
    latency_p99: list[float] = []
    traffic_counts: list[int] = []
    error_rates: list[float] = []
    error_breakdown_map: dict[str, list[int]] = {}
    cost_per_bucket: list[float] = []
    cost_cumulative: list[float] = []
    tokens_in_arr: list[int] = []
    tokens_out_arr: list[int] = []
    quality_avg_arr: list[float] = []

    running_cost = 0.0

    for i in range(num_buckets):
        # Time label
        bucket_time = start + i * bucket_seconds
        dt = datetime.datetime.fromtimestamp(bucket_time)
        labels.append(dt.strftime("%H:%M:%S"))

        records = bucket_records[i]
        errors = bucket_errors[i]

        # --- Panel 1: Latency P50 / P95 / P99 ---
        lats = [r.latency_ms for r in records]
        latency_p50.append(percentile(lats, 50))
        latency_p95.append(percentile(lats, 95))
        latency_p99.append(percentile(lats, 99))

        # --- Panel 2: Traffic ---
        traffic_counts.append(len(records) + len(errors))

        # --- Panel 3: Error rate with breakdown ---
        total = len(records) + len(errors)
        rate = (len(errors) / total * 100) if total > 0 else 0
        error_rates.append(round(rate, 2))

        for err in errors:
            if err.error_type not in error_breakdown_map:
                # Back-fill previous buckets with zeros
                error_breakdown_map[err.error_type] = [0] * i
            error_breakdown_map[err.error_type].append(
                error_breakdown_map[err.error_type][-1] + 1
                if len(error_breakdown_map[err.error_type]) > i
                else 1,
            )

        # Pad breakdown arrays that didn't have errors in this bucket
        for key in error_breakdown_map:
            while len(error_breakdown_map[key]) <= i:
                error_breakdown_map[key].append(0)

        # Count per-bucket errors by type
        bucket_err_counts: dict[str, int] = {}
        for err in errors:
            bucket_err_counts[err.error_type] = bucket_err_counts.get(err.error_type, 0) + 1
        for key in error_breakdown_map:
            error_breakdown_map[key][i] = bucket_err_counts.get(key, 0)

        # --- Panel 4: Cost over time ---
        bucket_cost = sum(r.cost_usd for r in records)
        cost_per_bucket.append(round(bucket_cost, 6))
        running_cost += bucket_cost
        cost_cumulative.append(round(running_cost, 6))

        # --- Panel 5: Tokens in / out ---
        tokens_in_arr.append(sum(r.tokens_in for r in records))
        tokens_out_arr.append(sum(r.tokens_out for r in records))

        # --- Panel 6: Quality proxy ---
        scores = [r.quality_score for r in records]
        quality_avg_arr.append(round(mean(scores), 4) if scores else 0.0)

    return {
        "labels": labels,
        "latency": {
            "p50": latency_p50,
            "p95": latency_p95,
            "p99": latency_p99,
        },
        "traffic": {
            "counts": traffic_counts,
        },
        "errors": {
            "rates": error_rates,
            "breakdown": error_breakdown_map,
        },
        "cost": {
            "per_bucket": cost_per_bucket,
            "cumulative": cost_cumulative,
        },
        "tokens": {
            "in": tokens_in_arr,
            "out": tokens_out_arr,
        },
        "quality": {
            "avg": quality_avg_arr,
        },
        "summary": snapshot(),
        "slo": {
            "latency_p95_ms": 3000,
            "error_rate_pct": 2,
            "daily_cost_usd": 2.5,
            "quality_score_avg": 0.75,
        },
    }
