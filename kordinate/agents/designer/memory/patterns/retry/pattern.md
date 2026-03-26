---
description: Retry architectural pattern
curated: true
scope: global
preloaded: none
---
# Retry with Backoff

## Recognition

How to identify this pattern in code.

### Signatures

- `tenacity` imports and decorators in Python (`@retry`, `wait_exponential`, `stop_after_attempt`)
- `polly` policies in .NET (`Policy.Handle<Exception>().WaitAndRetryAsync()`)
- `resilience4j-retry` configuration in Java (`RetryConfig`, `RetryRegistry`)
- `retry` package usage in Go (`retry.Do()`, `retry.Attempts()`)
- `backoff` decorator with exponential delay configuration (`@backoff.on_exception`)
- `max_retries` configuration parameters on client or operation config
- `retry_on_exception` predicates distinguishing retryable from non-retryable errors
- Dead letter queue routing on retry exhaustion (`DLQ`, `dead_letter`)

### Confidence

- **high** -- Library-specific imports (`tenacity`, `polly`, `resilience4j-retry`) with exponential backoff configuration and max retry bounds
- **medium** -- `max_retries` and `retry_on_exception` logic with dead letter queue on exhaustion, but using custom retry loops instead of a library
- **low** -- Simple retry loops with fixed delays or unbounded retries, without explicit backoff or DLQ handling

## Architecture

Look for bounded retries with exponential backoff, jitter, and a dead-letter path.

### Review Checklist

- Max retry count is configured and bounded — no infinite retry loops
- Backoff is exponential with jitter (not fixed delay — avoids thundering herd)
- Retryable vs. non-retryable errors are distinguished (don't retry 400s)
- Dead-letter queue or equivalent captures permanently failed operations
- Retry state is observable (metrics on attempt count and DLQ depth)

### Anti-patterns

- Fixed-delay retries — all clients retry simultaneously after an outage
- Retrying non-idempotent operations without deduplication
- No max retry limit — stuck requests consume resources indefinitely
- Silent discard of failed operations (no dead-letter, no alert)

## Monitoring

Track retry attempt distribution and dead-letter depth to distinguish transient blips from persistent failures.

### Key Metrics

- `retry_attempts_total` (counter) — retry attempts by operation and attempt number
- `retry_success_after_retry_total` (counter) — operations that succeeded on a retry (not first attempt)
- `retry_exhausted_total` (counter) — operations that exhausted all retries and were sent to dead-letter
- `dead_letter_queue_depth` (gauge) — current number of messages in the dead-letter queue
- `retry_backoff_duration_seconds` (histogram) — actual backoff delay distribution

### Alerts

- Dead-letter queue depth growing without being drained
- Retry exhaustion rate exceeding threshold (persistent downstream failure)
- High ratio of success-after-retry indicating flaky dependency
- Retry storm: sudden spike in retry attempts across multiple callers (thundering herd)

## Deployment

Retry configuration changes and DLQ backlog must be managed carefully to avoid retry storms during rollout.

### Rollout Implications

- Lowering max retry counts during rollout causes in-flight retries to DLQ sooner than expected — monitor DLQ depth during transition
- Changing backoff parameters while retries are in progress may cause a burst of simultaneous retries from pods on different configurations
- Rolling restart of consumers with pending retries may lose retry state if it is held in memory — persist retry state externally
- Deploying new retry policies alongside a degraded dependency amplifies load — consider pausing retries until the dependency recovers

### Pre-deploy Checklist

- Verify DLQ consumers are healthy and processing before deploying retry config changes
- Confirm retry state is persisted externally (not in-memory) so rolling restarts do not lose pending retries
- Check that backoff parameters include jitter to prevent thundering herd after fleet-wide restart

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
