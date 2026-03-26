---
description: Idempotent Consumer — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track deduplication effectiveness and the growth of the processed-ID store.

### Key Metrics

- `messages_deduplicated_total` (counter) — duplicate messages detected and skipped
- `idempotency_store_size` (gauge) — number of entries in the processed-ID table or set
- `idempotency_check_duration_seconds` (histogram) — latency of the dedup lookup
- `idempotency_store_cleanup_total` (counter) — expired entries purged per cleanup cycle

### Alerts

- Deduplication rate spike (upstream producing excessive retries)
- Idempotency store size approaching capacity or TTL cleanup stalled
- Dedup check latency increasing (index degradation or store overload)
- Zero deduplications over an extended period when at-least-once delivery is expected (check broken)
