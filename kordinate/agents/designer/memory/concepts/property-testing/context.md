## Testing

Validate that property tests express genuine invariants, strategies model the domain, and shrinking produces actionable counterexamples.

### Unit Tests

- Verify properties assert meaningful invariants (round-trip, idempotency, commutativity) not just "does not crash"
- Test custom strategies generate values within the expected domain constraints (valid ranges, formats, non-empty)
- Run a property that is known to fail and verify shrinking produces a minimal counterexample
- Confirm the seed is logged on failure so the exact counterexample is reproducible

### Strategy Validation

- Generate a sample of values from each custom strategy and verify the distribution covers edge cases (boundaries, empty, max-length)
- Compose strategies for complex domain objects and verify generated instances satisfy class invariants
- Verify strategies do not silently filter out too many values (high rejection rate signals an over-constrained strategy)

### CI Integration

- Run property tests with a reduced example count in fast CI, with periodic full runs (higher count) on schedule
- Verify that a failing property test in CI includes the shrunk counterexample and seed in the output
- Test stateful properties (sequences of operations) where applicable to catch order-dependent bugs

