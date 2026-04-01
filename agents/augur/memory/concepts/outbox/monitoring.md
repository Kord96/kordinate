---
description: Outbox — monitoring guidance
type: supplementary
---
## Monitoring

Track outbox table health and publisher lag to detect delivery stalls before they impact downstream consumers.

### Key Metrics

- `outbox_unpublished_count` (gauge) -- number of rows pending publication (should stay near zero)
- `outbox_publish_latency_seconds` (histogram) -- time from insert to successful broker delivery
- `outbox_publish_errors_total` (counter) -- failed publish attempts by error type (broker unavailable, serialization error)
- `outbox_table_size_rows` (gauge) -- total row count including published rows awaiting cleanup

### Alerts

- Unpublished event count exceeds threshold (publisher stalled or broker unreachable)
- Oldest unpublished event age exceeds SLA (events stuck in outbox beyond acceptable latency)
- Outbox table row count growing unboundedly (cleanup job not running or failing)
- Publisher error rate spike (broker connectivity issue or schema incompatibility)
