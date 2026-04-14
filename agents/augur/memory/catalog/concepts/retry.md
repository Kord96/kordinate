---
description: Retry architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction: [resilience, integration]
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
