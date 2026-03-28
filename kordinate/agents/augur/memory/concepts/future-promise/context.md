## Testing

Verify that async computations resolve correctly, propagate errors, and compose without deadlocks or lost results.

### Unit Tests

- Resolve a future with a value and assert the continuation receives the expected result
- Reject a future with an error and assert the error handler is invoked with the correct error
- Test chaining: future.then(a).then(b) should apply transformations in order and propagate the final result
- Verify that an unhandled rejection is surfaced (logged, thrown) rather than silently swallowed
- Test timeout: a future that never resolves should be cancellable or should trigger a timeout error

### Composition Tests

- Combine multiple futures with all/when-all and verify the result contains all resolved values in order
- Test any/race semantics: the first future to resolve wins, and remaining futures are cancelled or ignored
- Verify that a single failure in an all-composition rejects the aggregate with the correct error

### Concurrency Tests

- Resolve a future from one thread and await it from another — verify cross-thread delivery without races
- Test that completing a future multiple times is either idempotent or raises an explicit error

