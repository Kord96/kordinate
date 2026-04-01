---
description: Event-Driven — monitoring guidance
type: supplementary
---
## Monitoring

Track event throughput, consumer lag, and processing errors to maintain visibility into asynchronous workflows.

### Key Metrics

- `events_published_total` (counter) — events emitted by producers, by event type
- `events_consumed_total` (counter) — events successfully processed by consumers
- `consumer_lag` (gauge) — offset difference between latest published and last consumed event
- `event_processing_duration_seconds` (histogram) — time from event receipt to processing completion

### Alerts

- Consumer lag exceeding threshold (consumers falling behind producers)
- Event processing error rate spike (poison messages or downstream failures)
- Zero events published for an expected event type over a time window (producer may be down)
