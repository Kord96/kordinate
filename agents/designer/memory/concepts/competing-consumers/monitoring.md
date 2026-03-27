---
description: Competing Consumers — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track queue depth, consumer throughput, and processing distribution across instances.

### Key Metrics

- `queue_depth` (gauge) — pending messages in the queue
- `consumer_messages_processed_total` (counter) — messages processed per consumer instance
- `consumer_processing_latency_seconds` (histogram) — per-message processing time
- `consumer_redeliveries_total` (counter) — messages redelivered after failed processing

### Alerts

- Queue depth growing steadily (consumers not keeping up with producers)
- Consumer instance processing zero messages (stuck or disconnected)
- Redelivery rate exceeding threshold (poison message or systemic failure)
