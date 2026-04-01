---
description: Change Data Capture (CDC) — monitoring guidance
type: supplementary
---
## Monitoring

Track replication lag, connector health, and event throughput from source to consumers.

### Key Metrics

- `cdc_lag_seconds` (gauge) — delay between source commit and event availability to consumers
- `cdc_events_total` (counter) — events captured by table/collection and operation type
- `cdc_connector_status` (gauge) — connector health (0=failed, 1=running, 2=paused)
- `cdc_snapshot_progress` (gauge) — initial snapshot completion percentage

### Alerts

- Replication lag exceeding acceptable threshold
- Connector failure or repeated restart
- Event throughput drop to zero (silent connector failure)
