---
description: Retry architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- resilience
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - circuit-breaker
  - timeout
  - dead-letter
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
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

### Relationship To Other Concepts

- Related to [circuit-breaker](/concepts/circuit-breaker) because retries and breakers are often paired, though careless retries can worsen dependency stress.
- Related to [timeout](/concepts/timeout) because retries only make sense with bounded attempt duration.
- Related to [dead-letter](/concepts/dead-letter) when failed work is retried a fixed number of times before being quarantined.

### Boundary

Use `retry` when failed operations are intentionally attempted again according to explicit policy such as backoff, jitter, and maximum attempts.

Do not use it for generic loops or polling. The key signal is resilience-oriented reattempt policy around failure.
