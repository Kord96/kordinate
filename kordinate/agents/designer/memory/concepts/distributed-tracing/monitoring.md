---
description: Distributed Tracing Instrumentation — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track trace pipeline health and sampling coverage to ensure traces are actually reaching the backend.

### Key Metrics

- `traces_exported_total` (counter) — traces successfully sent to the collector
- `traces_dropped_total` (counter) — traces dropped due to sampling, buffer overflow, or export failure
- `trace_export_latency_seconds` (histogram) — time to flush trace batches to the collector
- `span_count_per_trace` (histogram) — number of spans per trace to detect over-instrumentation or missing spans

### Alerts

- Trace drop rate exceeding threshold (data loss in the observability pipeline)
- Export latency spike (collector or network backpressure)
- Services with zero trace output (instrumentation broken or sampling misconfigured)
