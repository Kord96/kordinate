## Testing

Verify monadic laws, chain composition, and correct error propagation through pipelines.

### Unit Tests

- Verify left identity: `unit(a).bind(f)` equals `f(a)` for representative values and functions
- Verify right identity: `m.bind(unit)` equals `m` for representative monadic values
- Verify associativity: `m.bind(f).bind(g)` equals `m.bind(x -> f(x).bind(g))`

### Pipeline Tests

- Compose a multi-step pipeline and verify the happy path produces the expected final value
- Introduce a failure at each step and verify the error short-circuits through the remaining steps
- Assert that error types carry enough context to diagnose which step failed and why

### Edge Cases

- Test with `None`/`Nothing` input to an `Option`/`Maybe` chain and verify clean propagation
- Verify that `unwrap()` or `get()` on a failure value raises an appropriate error, not a silent default
- Test nested monads (e.g., `Option<Result>`) and verify correct flattening via `bind`/`flatMap`

