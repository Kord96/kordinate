## Testing

Test systems in isolation with minimal component sets and verify that entity composition produces correct emergent behavior.

### Unit Tests

- Test each system with a single entity carrying the minimum required components and assert the expected state mutation
- Verify that systems skip entities missing required components — no errors, just no processing
- Test component addition and removal: adding a component mid-frame should include the entity in the relevant system next tick
- Assert that systems with ordering dependencies process in the declared order

### Integration Tests

- Compose entities with multiple components and verify interacting systems produce correct combined behavior
- Test entity lifecycle: create, add components, process through systems, remove components, destroy — no dangling references
- Verify that archetype/query caches update correctly when entity composition changes dynamically

### Performance Tests

- Benchmark system iteration over large entity counts to catch O(n^2) regressions in query or iteration logic

