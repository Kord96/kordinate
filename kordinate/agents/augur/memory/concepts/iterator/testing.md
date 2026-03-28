---
description: Iterator — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify lazy evaluation, correct termination, and composability of iterator implementations.

### Unit Tests

- Assert that the iterator produces elements on demand without materializing the entire collection
- Verify correct termination: `StopIteration` is raised (or `None` returned) when elements are exhausted
- Test early termination: break out of iteration partway and confirm no resource leaks (generators with `finally` cleanup)

### Composition Tests

- Chain `map`, `filter`, and `take` on the iterator and verify only the expected elements are produced
- Assert that intermediate collections are not materialized during chained operations

### Edge Cases

- Test iteration over an empty collection (immediate termination, no errors)
- Test iteration over a single-element collection
- Verify that iterating the same iterator twice produces no elements on the second pass (single-use semantics)
