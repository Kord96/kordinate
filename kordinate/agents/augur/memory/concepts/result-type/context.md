## Testing

Verify both success and error paths are exercised, error variants are typed, and result composition chains work correctly.

### Unit Tests

- Test the happy path returns `Ok`/`Right` with the expected value
- Test each known failure mode returns the correct typed error variant in `Err`/`Left`
- Verify `match`/`fold` at the call site handles all error variants exhaustively (no unhandled cases)
- Test `.map()` and `.flatMap()` / `.and_then()` chains: verify the chain short-circuits on the first error

### Composition Tests

- Chain multiple result-returning functions and verify the final result propagates the first error encountered
- Test error mapping at module boundaries: low-level errors are transformed into domain-appropriate errors
- Verify `.unwrap()` or `.get()` is not used in production code paths (only in tests where failure means test failure)

### Design Verification

- Verify domain errors are represented as typed variants, not generic strings or unstructured exceptions
- Confirm exceptions are reserved for truly unexpected errors (panics, programming bugs), not domain-level failures
- Test that result types are propagated through the call chain without premature unwrapping at intermediate layers

