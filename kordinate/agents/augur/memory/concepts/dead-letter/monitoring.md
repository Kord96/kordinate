---
description: Dead Letter Queue — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track DLQ depth and message age to catch processing failures before they accumulate silently.

### Key Metrics

- `dlq_depth` (gauge) — number of messages currently in the dead letter queue
- `dlq_enqueue_total` (counter) — messages moved to DLQ after exhausting retries
- `dlq_oldest_message_age_seconds` (gauge) — age of the oldest unprocessed DLQ message
- `dlq_reprocessed_total` (counter) — messages successfully replayed from the DLQ

### Alerts

- DLQ depth exceeding threshold (messages accumulating faster than they are being triaged)
- Oldest message age beyond SLA — stale messages indicate nobody is reviewing the DLQ
- Sudden spike in DLQ enqueue rate (upstream processing regression)
