---
description: Metrics Instrumentation architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Metrics Instrumentation

## Recognition

How to identify this pattern in code.

### Signatures

- Prometheus client usage: `prometheus_client` (Python), `prom-client` (Node), `prometheus/client_golang` (Go)
- Metric type classes: `Counter`, `Gauge`, `Histogram`, `Summary`
- Metric registration: `register()`, `MustRegister()`, `new Counter({})`, `@metrics.counter()`
- `/metrics` endpoint exposed via HTTP for scraping
- Micrometer (Java/Spring): `MeterRegistry`, `@Timed`, `Counter.builder()`
- Label/tag definitions on metric declarations: `labels=["method", "status"]`, `ConstLabels`
- Histogram bucket configuration: `buckets=[.01, .05, .1, .5, 1, 5]`

### Confidence

- **high** -- Prometheus client imported, metric types registered, and `/metrics` endpoint exposed
- **medium** -- metric library in dependencies and some counters declared but no histogram or `/metrics` endpoint
- **low** -- custom numeric tracking (incrementing counters in code) without a metrics library

## Architecture

Look for well-named metrics with appropriate types, consistent labels, and a scrape-ready endpoint.

### Review Checklist

- Metric names follow the convention: `<namespace>_<subsystem>_<name>_<unit>` (e.g., `http_requests_total`, `request_duration_seconds`)
- Correct metric type for each measurement: counters for totals, gauges for current values, histograms for distributions
- Label cardinality is bounded -- no user IDs, request IDs, or unbounded strings as label values
- Histogram buckets are tuned to the expected distribution, not left at defaults
- All metrics are registered at startup, not created on-the-fly per request
- A `/metrics` endpoint is exposed and returns Prometheus exposition format

### Anti-patterns

- High-cardinality labels that cause metric explosion (e.g., `user_id`, `url_path` with path parameters)
- Using gauges where counters are appropriate (losing monotonicity breaks rate calculations)
- Metrics created inside request handlers instead of registered once at module level
- No histogram for latency measurements -- only averages with no percentile visibility
