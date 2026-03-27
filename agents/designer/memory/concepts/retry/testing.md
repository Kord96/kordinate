---
description: Retry with Backoff — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Validate backoff timing, retry bounds, dead-letter routing, and idempotency safety across retry attempts.

### Unit Tests

- Test backoff timing: assert delays follow exponential progression with jitter and do not exceed max backoff
- Verify max retry enforcement: after N configured attempts, assert the operation is not retried and routes to DLQ
- Test retryable vs non-retryable classification: assert 5xx errors trigger retry while 4xx errors fail immediately
- Verify idempotency: assert that retrying the same operation with the same idempotency key produces no duplicate side effects

### Integration Tests

- Fail an operation repeatedly until it hits max retries, then verify the message lands in the actual DLQ with correct metadata
- Test end-to-end retry with a flaky dependency that succeeds on the third attempt — verify the operation completes successfully
- Verify DLQ consumption: read from the DLQ and confirm failed messages contain the original payload and failure reason

### Failure Injection

- Simulate a dependency that fails indefinitely and verify retry exhaustion routes to DLQ within bounded time (no infinite loop)
- Inject clock skew to test that jitter produces varied delays across concurrent retriers (no thundering herd)
- Kill the DLQ broker and verify the retry mechanism surfaces the DLQ write failure rather than silently discarding the message
