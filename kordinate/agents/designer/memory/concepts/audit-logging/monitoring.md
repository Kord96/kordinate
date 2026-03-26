---
description: Audit Logging — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track audit log ingestion rates, gaps, and storage health.

### Key Metrics

- `audit_events_total` (counter) — events written by action type and outcome
- `audit_write_latency_seconds` (histogram) — time to persist each audit entry
- `audit_lag_seconds` (gauge) — delay between event occurrence and log persistence
- `audit_storage_bytes` (gauge) — audit log storage consumption

### Alerts

- Audit write failures (compliance risk if events are lost)
- Ingestion lag exceeding acceptable window
- Gap in expected periodic events (missing heartbeat entries)
