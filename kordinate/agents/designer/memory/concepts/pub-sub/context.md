## Testing

Verify fan-out delivery, subscriber isolation, and correct behavior under failure and duplicate delivery.

### Unit Tests

- Publish a message and verify all registered subscribers receive it with the correct payload
- Subscribe and unsubscribe a handler, then publish and verify the unsubscribed handler is not called
- Verify subscriber failure does not block delivery to other subscribers on the same topic
- Test message filtering: subscribers with topic filters receive only matching messages

### Integration Tests

- Publish through the real broker (Kafka, Redis, NATS) and verify end-to-end delivery to a test subscriber
- Test at-least-once delivery: acknowledge a message, then verify it is not redelivered; nack a message and verify redelivery
- Verify ordering guarantees per partition or subject (where the broker guarantees ordering)
- Publish during a subscriber restart and verify no messages are lost (retained or replayed from offset)

### Idempotency Tests

- Deliver the same message twice and verify the subscriber produces the correct outcome (no duplicate side effects)
- Simulate broker redelivery after ack timeout and verify the subscriber handles it gracefully

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

## Deployment

Coordinate topic configuration and subscriber compatibility during rollouts.

### Rollout Implications

- New message schemas must be backward-compatible -- existing subscribers must handle both old and new formats during rolling deployment
- Adding a new subscriber requires the topic and subscription to exist before the subscriber pod starts consuming
- Removing a subscriber requires draining its pending messages first to avoid silent message loss
- Scaling subscribers horizontally is safe if the broker supports consumer groups; otherwise duplicate delivery occurs

### Pre-deploy Checklist

- Verify topic exists and has the correct partitioning and retention settings for the target environment
- Confirm all subscribers can deserialize the new message format (deploy consumers before producers when adding fields)
- Check subscriber acknowledgment timeout is appropriate for the new processing logic (longer processing needs longer ack deadline)
- Ensure dead-letter topic is configured for all subscriptions to catch processing failures

