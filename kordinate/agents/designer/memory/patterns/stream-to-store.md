# Stream-to-Store


## Architecture

Look for correct offset management — commits only after successful flush.

### Review Checklist

- Offsets are committed after the store write succeeds, not before
- Buffer has both size and time-based flush triggers
- Flush failures trigger retry with backoff before giving up
- Consumer group rebalancing is handled without data loss or duplication
- Store writes are idempotent (safe to replay on reprocessing)

### Anti-patterns

- Auto-commit enabled — offsets advance regardless of flush success
- Unbounded buffer with no size limit (memory exhaustion on slow stores)
- No dead-letter handling for permanently unprocessable messages

## Monitoring

TODO

## Deployment

TODO

## Testing

TODO
