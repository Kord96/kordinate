---
description: Property-Based Testing architectural pattern
type: pattern
testable: true
graphable: true
abstraction:
- testing
status: primary
scope: backend
relationships:
  related_to:
  - fixture-builder
  - result-type
  - fuzz-testing
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Property-Based Testing

## Recognition

How to identify this pattern in code.

### Signatures

- `@given` decorator with `hypothesis` strategies in Python tests
- `hypothesis.strategies` imports (`st.integers()`, `st.text()`, `st.lists()`)
- `QuickCheck` and `Arbitrary` instances in Haskell tests
- `fast-check` or `jsverify` imports in JavaScript/TypeScript tests
- `@Property` annotations with `jqwik` in Java tests
- Strategy-based input generation (`st.builds()`, `fc.record()`, custom strategy composition)
- Shrinking on failure: test output shows minimized counterexamples

### Confidence

- **high** — `@given` or equivalent decorator with strategy composition, and tests assert invariants rather than specific input/output pairs
- **medium** — Property testing library imported but tests use fixed seeds or narrow strategies that behave like example-based tests
- **low** — Randomized test data generation (e.g., `random.randint` in a loop) without a property testing framework or shrinking

## Architecture

Look for tests that assert universal properties (invariants) over generated inputs rather than checking specific examples.

### Review Checklist

- Properties express genuine invariants (idempotency, round-trip, commutativity) not just "does not throw"
- Custom strategies model the actual domain constraints (valid email formats, bounded integers, non-empty lists)
- Shrinking is enabled so failures produce minimal reproducible counterexamples
- Test database or seed is logged for reproducibility when a property fails
- Stateful property tests cover sequences of operations where applicable

### Anti-patterns

- Writing property tests that only assert the function does not crash, without checking meaningful output properties
- Overly constrained strategies that reduce to a handful of fixed inputs, defeating the purpose of generation
- Ignoring shrunk counterexamples and debugging against the original large input
- No CI integration for property tests because they are "too slow" -- use smaller example counts with periodic full runs

### Relationship To Other Concepts

- Related to [fixture-builder](/concepts/fixture-builder) as another testing aid, though property testing generates inputs from properties rather than hand-assembling cases.
- Related to [result-type](/concepts/result-type) when functions expose invariants that property tests can exercise across success and failure shapes.
- Related to [fuzz-testing](/concepts/fuzz-testing) because both generate inputs, though property testing asserts domain invariants rather than only crashing behavior.

### Boundary

Use `property-testing` when behavior is tested by generating many inputs and asserting invariants or algebraic properties over the outputs.

Do not use it for ordinary parameterized tests. The key signal is generated input space plus property assertions.
