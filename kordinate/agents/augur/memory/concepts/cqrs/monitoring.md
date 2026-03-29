---
description: CQRS — monitoring guidance
---
## Monitoring

Track read/write path health and projection lag to catch sync divergence before it becomes user-visible.

### Key Metrics

- `projection_lag_seconds` (gauge) — delay between write model update and read model sync
- `command_processed_total` (counter) — commands handled by the write path
- `query_processed_total` (counter) — queries served by the read path
- `projection_errors_total` (counter) — failures during read model projection/sync
- `projection_rebuild_duration_seconds` (histogram) — time to rebuild read model from scratch

### Alerts

- Projection lag exceeding acceptable consistency window
- Projection error rate spiking (sync mechanism broken)
- Read model rebuild taking longer than maintenance window allows
- Write-to-read ratio diverging unexpectedly (indicates stale projections or lost events)
