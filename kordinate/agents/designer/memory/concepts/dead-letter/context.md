## Testing

Verify that messages land in the DLQ only after retry exhaustion and that replay mechanisms work correctly.

### Unit Tests

- Simulate a message that fails processing and assert it is routed to the DLQ after the configured retry count
- Verify that transient errors trigger retries but do not immediately DLQ the message
- Assert DLQ messages retain the original payload plus failure metadata (error reason, attempt count, timestamp)

### Integration Tests

- Publish a poison message, verify it arrives in the DLQ, replay it after fixing the consumer, and confirm successful processing
- Test that DLQ replay preserves message ordering when order matters downstream
- Verify DLQ depth metrics increment correctly as messages are enqueued

### Failure Injection

- Inject a serialization error and confirm the message is dead-lettered rather than silently dropped
- Simulate a full DLQ (capacity limit) and verify the system applies backpressure or alerts rather than losing messages

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

## Deployment

Ensure DLQ infrastructure is provisioned before consumer changes and that message format compatibility is maintained.

### Rollout Implications

- Deploy DLQ consumers and replay tooling before deploying producer changes that may alter message schemas
- Rolling updates to consumers may temporarily increase DLQ volume if new code rejects messages the old code accepted
- Verify DLQ retention policies are long enough to survive a rollout window plus investigation time
- If changing message format, ensure the DLQ consumer can deserialize both old and new formats during transition

### Pre-deploy Checklist

- Confirm DLQ topic/queue exists and has correct permissions in the target environment
- Verify alerting is active on DLQ depth so new failures are caught immediately post-deploy

