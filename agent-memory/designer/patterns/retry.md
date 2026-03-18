# Retry with Backoff — Design Perspective

```
                    ┌─────────┐
         ┌────────►│  Call    │
         │         └────┬────┘
         │              │
         │         success / fail?
         │              │
         │     ┌────────┴────────┐
         │     │                 │
         │  success           fail
         │     │                 │
         │     ▼            retries left?
         │   Done                │
         │              ┌───────┴───────┐
         │              │               │
         │             yes              no
         │              │               │
         │          wait (exp           ▼
         │          backoff        ┌──────────┐
         └──── + jitter)          │Dead Letter│
                                  └──────────┘
```

Look for bounded retries with exponential backoff, jitter, and a dead-letter path.

## Review Checklist

- Max retry count is configured and bounded — no infinite retry loops
- Backoff is exponential with jitter (not fixed delay — avoids thundering herd)
- Retryable vs. non-retryable errors are distinguished (don't retry 400s)
- Dead-letter queue or equivalent captures permanently failed operations
- Retry state is observable (metrics on attempt count and DLQ depth)

## Anti-patterns

- Fixed-delay retries — all clients retry simultaneously after an outage
- Retrying non-idempotent operations without deduplication
- No max retry limit — stuck requests consume resources indefinitely
- Silent discard of failed operations (no dead-letter, no alert)
