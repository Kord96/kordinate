---
description: Test Fixture / Data Builder — testing guidance
type: supplementary
---
## Testing

Verify that builders produce valid, consistent test data and that fixture defaults remain sensible as the domain evolves.

### Unit Tests

- Assert that the default builder produces a valid domain object that passes all invariant checks
- Test each builder override: setting a single field should change only that field, leaving all others at defaults
- Verify that builders for related entities maintain referential integrity (e.g., an order builder references a valid customer)
- Test that builders fail fast when given invalid combinations rather than producing subtly broken objects

### Maintenance Tests

- When adding a required field to a domain object, assert that the builder is updated with a sensible default — compilation alone may not catch runtime validation failures
- Verify that randomized builders (faker-based) still produce valid objects — run the builder in a loop and validate each output

### Anti-pattern Detection

- Assert that tests use builders rather than raw constructors with magic values — builders make test intent explicit
- Verify fixture data does not leak between tests: each test should get a fresh builder instance
