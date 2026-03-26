---
description: Message Queue — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track queue depth, consumer throughput, and dead-letter activity to detect processing bottlenecks.

### Key Metrics

- `queue_depth` (gauge) — number of messages waiting to be consumed
- `messages_consumed_total` (counter) — messages successfully processed and acknowledged
- `messages_dead_lettered_total` (counter) — messages routed to the dead-letter queue after retry exhaustion
- `message_processing_duration_seconds` (histogram) — time from dequeue to acknowledgment

### Alerts

- Queue depth growing monotonically (consumers not keeping up with producers)
- Dead-letter queue receiving messages (poison messages or persistent processing failures)
- Processing duration exceeding the visibility timeout (risk of duplicate delivery)
- Consumer count dropping to zero (all consumers crashed or disconnected)
