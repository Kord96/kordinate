---
kind: concept
name: retry
signatures:
  concept: retry
  positive:
    strong:
    - tenacity or backoff decorators with bounds
    - retry library calls with retries or maxRetries options
    medium:
    - custom retry wrapper with explicit retry count
    - DLQ or retry exhaustion handling
    weak:
    - simple retry loop without backoff
  negative:
  - infinite retry loop
  - fixed-delay retries with no jitter or bound
  notes:
  - Broad retry-like loops should remain candidates until bounded behavior is confirmed.
type: pattern
abstraction:
- resilience
- integration
scope: cross-cutting
status: primary
review_questions:
  threshold: 6
  entries:
  - id: retry-bounded-attempts
    prompt: Is the retry behavior bounded by an explicit attempt or deadline limit?
    weight: 3
    signals:
    - stop_after_attempt
    - retries: null
    - maxRetries
  - id: retry-backoff
    prompt: Is there exponential backoff or jitter rather than a fixed-delay loop?
    weight: 2
    signals:
    - wait_exponential
    - backoff
    - jitter
  - id: retry-idempotent-or-dlq
    prompt: Is the retried operation idempotent or routed to a dead-letter path on
      exhaustion?
    weight: 1
    signals:
    - dead letter
    - idempotent
monitoring:
  applies_to:
  - component
  - dependency
  - flow
  health_signals:
  - name: retry.attempts
    description: Distribution of retry attempts before success or terminal failure.
  - name: retry.exhausted.rate
    description: Rate at which retries are exhausted without recovery.
  - name: downstream.retryable_error.rate
    description: Rate of retryable downstream failures that trigger the retry path.
  business_metrics: []
  gaps:
  - If retries are invisible, transient downstream instability can silently consume
    latency budgets.
family: design-patterns
---

# Explanation

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
