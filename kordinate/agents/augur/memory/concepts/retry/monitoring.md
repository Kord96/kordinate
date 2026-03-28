---
description: Retry with Backoff — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track retry attempt distribution and dead-letter depth to distinguish transient blips from persistent failures.

### Key Metrics

- `retry_attempts_total` (counter) — retry attempts by operation and attempt number
- `retry_success_after_retry_total` (counter) — operations that succeeded on a retry (not first attempt)
- `retry_exhausted_total` (counter) — operations that exhausted all retries and were sent to dead-letter
- `dead_letter_queue_depth` (gauge) — current number of messages in the dead-letter queue
- `retry_backoff_duration_seconds` (histogram) — actual backoff delay distribution

### Alerts

- Dead-letter queue depth growing without being drained
- Retry exhaustion rate exceeding threshold (persistent downstream failure)
- High ratio of success-after-retry indicating flaky dependency
- Retry storm: sudden spike in retry attempts across multiple callers (thundering herd)
