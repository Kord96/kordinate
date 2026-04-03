---
description: Timeout — monitoring guidance
---
## Monitoring

Track timeout rates per dependency and monitor latency relative to configured thresholds.

### Key Metrics

- `timeout_errors_total` (counter) — timeout occurrences partitioned by dependency and timeout type (connect, read, write)
- `dependency_latency_seconds` (histogram) — request latency per dependency with configured timeout value as reference
- `timeout_deadline_remaining_seconds` (histogram) — remaining deadline at each service hop, detects tight propagation
- `timeout_unconfigured_calls_total` (counter) — external calls detected with no explicit timeout set (silent hang risk)
- `timeout_rate_ratio` (gauge) — fraction of requests timing out per dependency over a sliding window

### Alerts

- Timeout rate spike on any dependency (upstream latency or capacity degradation)
- Latency p99 approaching the configured timeout value (near-miss, threshold too tight)
- Deadline already expired or near-zero when reaching a downstream service (propagation too tight)
- External calls detected without explicit timeout configuration (silent hang risk)
- Connection timeout and read/write timeout errors conflated in the same metric (mask different root causes)
