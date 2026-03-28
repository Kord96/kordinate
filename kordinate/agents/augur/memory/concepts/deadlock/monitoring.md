---
description: Deadlock — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Detect lock contention and deadlock occurrences before they cascade into widespread request failures.

### Key Metrics

- `lock_wait_duration_seconds` (histogram) — time threads spend waiting to acquire locks
- `deadlock_detected_total` (counter) — deadlocks detected by the database or application runtime
- `lock_timeout_total` (counter) — lock acquisition attempts that exceeded the timeout threshold
- `active_locks` (gauge) — number of currently held locks, broken down by resource

### Alerts

- Any deadlock detection event (every occurrence warrants investigation)
- Lock wait duration exceeding p99 baseline (emerging contention before deadlock)
- Rising lock timeout rate (callers giving up, likely degraded throughput)
