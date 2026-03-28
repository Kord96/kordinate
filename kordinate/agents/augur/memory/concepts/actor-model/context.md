## Testing

Test actor behavior in isolation by sending messages and asserting responses, then verify supervision and concurrency.

### Unit Tests

- Send a message to an actor and assert the correct response or state change
- Verify that actors process messages sequentially — no concurrent state mutation
- Test supervision strategy: a failing child actor is restarted with correct initial state

### Integration Tests

- Wire multiple actors together and verify end-to-end message flow
- Test actor persistence: kill an actor, restart it, and verify state recovery from journal
- Verify dead letter handling for messages sent to stopped actors

### Failure Injection

- Inject exceptions in message handlers and verify the supervisor restarts the actor
- Flood an actor mailbox and verify backpressure or bounded-mailbox rejection behavior

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

## Deployment

Drain actor mailboxes before shutdown and ensure supervision trees restart cleanly on new instances.

### Rollout Implications

- Drain in-flight messages before terminating pods — actors with non-empty mailboxes lose unprocessed work
- Rolling restarts redistribute actors across nodes; verify cluster membership protocol handles rejoins
- Persistent actors must recover state from journal/snapshot before accepting new messages

### Pre-deploy Checklist

- Verify terminationGracePeriodSeconds allows full mailbox drain
- Confirm actor serialization format is backward-compatible with in-flight messages

