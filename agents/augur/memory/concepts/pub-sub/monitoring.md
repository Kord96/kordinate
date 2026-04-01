---
description: Publish-Subscribe — monitoring guidance
type: supplementary
---
## Monitoring

Track message delivery health, subscriber lag, and topic throughput to detect delivery failures and slow consumers.

### Key Metrics

- `pubsub_messages_published_total` (counter) -- messages published per topic
- `pubsub_messages_delivered_total` (counter) -- messages delivered per subscriber per topic
- `pubsub_subscriber_lag` (gauge) -- number of undelivered messages per subscriber (backlog depth)
- `pubsub_delivery_latency_seconds` (histogram) -- time from publish to subscriber acknowledgment
- `pubsub_dead_letter_total` (counter) -- messages moved to dead-letter after max delivery attempts

### Alerts

- Subscriber lag exceeds threshold (consumer falling behind or stalled)
- Delivery latency exceeds SLA for a sustained period
- Dead-letter queue depth growing (messages consistently failing processing)
- Zero publish rate on a topic that should have steady traffic (publisher down or misconfigured)
