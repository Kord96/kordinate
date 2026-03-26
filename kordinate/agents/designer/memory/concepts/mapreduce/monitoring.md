---
description: MapReduce — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track job progress, task failures, and data skew to detect stalled or inefficient computations.

### Key Metrics

- `map_tasks_completed` / `reduce_tasks_completed` (counters) — progress through the job
- `task_failures_total` (counter) — map or reduce task failures requiring retry
- `shuffle_bytes_total` (counter) — intermediate data volume between map and reduce phases
- `partition_skew_ratio` (gauge) — ratio of largest to smallest partition size

### Alerts

- Job runtime exceeding expected duration (straggler tasks or data skew)
- Task failure rate above threshold (bad input data or resource exhaustion)
- Shuffle volume disproportionately large relative to input (inefficient map output or missing combiner)
- Single reducer receiving significantly more data than others (hot key skew)
