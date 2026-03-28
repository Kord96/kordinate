## Testing

Verify that null objects satisfy the full interface contract and behave identically to real implementations from the caller's perspective.

### Unit Tests

- Assert every interface method is implemented and returns the expected neutral value (empty list, zero, no-op)
- Verify null objects are stateless: calling methods multiple times produces the same result with no side effects
- Confirm call sites work identically whether injected with the real implementation or the null object
- Test that null objects do not throw on any valid input, including edge cases like empty strings or None arguments

### Integration Tests

- Wire null objects into the DI container and verify the application starts and runs without null-pointer errors
- Substitute null loggers/metrics in integration tests to confirm no code path depends on logging side effects
- Validate that partial null implementations (if any exist) are caught by interface conformance tests

### Design Verification

- Ensure no code path inspects the concrete type to distinguish null objects from real ones (breaks polymorphism)
- Confirm null objects used in production defaults do not silently hide failures that should surface

