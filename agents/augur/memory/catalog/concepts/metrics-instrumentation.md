---
description: Metrics Instrumentation architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- observability
status: primary
scope: cross-cutting
relationships:
  related_to:
  - distributed-tracing
  - structured-logging
  - health-check
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
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

### Relationship To Other Concepts

- Related to [distributed-tracing](/concepts/distributed-tracing) because both are part of the observability stack, but metrics summarize behavior while traces reconstruct individual flows.
- Related to [structured-logging](/concepts/structured-logging) because logs, metrics, and traces are often correlated to observe one system from different angles.
- Related to [health-check](/concepts/health-check) when metrics drive automated health decisions or alerting thresholds.

### Boundary

Use `metrics-instrumentation` when the system emits quantitative counters, gauges, histograms, or summaries as a first-class observability surface.

Do not use it for plain logging or one-off timing prints. The key signal is structured metric emission meant for scraping or aggregation.
