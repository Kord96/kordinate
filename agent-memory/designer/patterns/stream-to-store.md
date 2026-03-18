# Stream-to-Store — Design Perspective

```
  ┌────────┐     ┌──────────┐     ┌────────┐     ┌───────┐     ┌───────┐
  │ Broker │────►│ Consumer │────►│ Buffer │────►│ Flush │────►│ Store │
  │(Kafka) │     │  group   │     │(batch) │     │       │     │(DB/S3)│
  └────────┘     └──────────┘     └───┬────┘     └───┬───┘     └───────┘
                                      │              │
                                  size/time       commit
                                  trigger         offset
```

Look for correct offset management — commits only after successful flush.

## Review Checklist

- Offsets are committed after the store write succeeds, not before
- Buffer has both size and time-based flush triggers
- Flush failures trigger retry with backoff before giving up
- Consumer group rebalancing is handled without data loss or duplication
- Store writes are idempotent (safe to replay on reprocessing)

## Anti-patterns

- Auto-commit enabled — offsets advance regardless of flush success
- Unbounded buffer with no size limit (memory exhaustion on slow stores)
- No dead-letter handling for permanently unprocessable messages
