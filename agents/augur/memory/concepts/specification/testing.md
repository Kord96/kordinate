---
description: Specification Pattern — testing guidance
type: supplementary
---
# Testing

- Unit test each specification independently with `is_satisfied_by()` against positive and negative cases
- Test composed specifications (`and`, `or`, `not`) to verify correct boolean logic
- Verify that specifications are side-effect free — calling `is_satisfied_by()` does not modify state
- Test that the same specification works for both in-memory filtering and query generation (dual-purpose)
- Assert that complex business rules expressed as named compositions produce expected results
- Test edge cases: null candidates, empty collections, boundary values for numeric specifications
- Verify that adding a new specification does not require modifying existing ones (open-closed principle)
