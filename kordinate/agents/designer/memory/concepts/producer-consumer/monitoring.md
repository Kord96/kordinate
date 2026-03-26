---
description: Producer-Consumer — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track queue depth, throughput imbalance, and consumer health to detect backlog buildup early.

### Key Metrics

- `queue_depth` (gauge) -- current number of items in the shared buffer
- `queue_capacity_utilization` (gauge) -- queue depth as a percentage of max capacity
- `producer_enqueue_rate` (counter) -- items enqueued per second
- `consumer_dequeue_rate` (counter) -- items dequeued and processed per second
- `consumer_processing_errors_total` (counter) -- items that failed processing in the consumer

### Alerts

- Queue depth exceeds high-water mark (consumers falling behind producers)
- Queue at capacity for more than a sustained period (producers blocking or dropping)
- Consumer dequeue rate drops to zero while queue depth is nonzero (consumer stalled or dead)
- Consumer error rate exceeds threshold (poison messages or downstream failure)
