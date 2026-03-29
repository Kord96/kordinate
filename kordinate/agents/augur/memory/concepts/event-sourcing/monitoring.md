---
description: Event Sourcing — monitoring guidance
---
## Monitoring

Track event store throughput, replay performance, and snapshot health to prevent unbounded growth from degrading the system.

### Key Metrics

- `event_store_append_total` (counter) — events written per aggregate type
- `event_store_append_duration_seconds` (histogram) — write latency to the event store
- `event_replay_duration_seconds` (histogram) — time to rebuild aggregate state from events
- `snapshot_age_seconds` (gauge) — time since last snapshot per aggregate type
- `events_since_snapshot` (gauge) — event count since last snapshot per aggregate

### Alerts

- Event replay duration exceeding acceptable threshold (snapshot may be stale or missing)
- Events-since-snapshot count growing beyond configured limit
- Event store append latency degrading (storage pressure)
- Snapshot creation failures accumulating
