---
description: Actor Model — monitoring guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Monitoring

Track actor mailbox depth, message throughput, and supervision events.

### Key Metrics

- `actor_mailbox_size` (gauge) — pending messages per actor, signals backpressure
- `actor_messages_processed_total` (counter) — throughput per actor type
- `actor_message_latency_seconds` (histogram) — time from enqueue to processing
- `actor_restarts_total` (counter) — supervisor-triggered restarts per actor

### Alerts

- Mailbox depth exceeding threshold (actor falling behind)
- Restart rate spike (actor crash loop)
- Message processing latency exceeding SLA
