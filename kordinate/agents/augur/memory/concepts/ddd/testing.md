---
description: Domain-Driven Design — testing guidance
---
## Testing

Validate that aggregates enforce invariants and bounded contexts remain isolated through their public contracts.

### Unit Tests

- Test aggregate invariants by attempting illegal state transitions and asserting they are rejected
- Verify that domain events are published with correct data when aggregate state changes
- Test value objects for equality semantics and validation rules (e.g., invalid email rejected at construction)
- Assert that factory methods produce aggregates in a valid initial state

### Integration Tests

- Test anti-corruption layer translations — send upstream context events and verify downstream context receives correctly mapped domain objects
- Verify that domain events published by one aggregate are consumed and handled by other aggregates without shared internal state
- Test repository implementations against the actual store, asserting aggregate reconstitution preserves invariants

### Failure Injection

- Simulate anti-corruption layer failure and verify the downstream context rejects or queues rather than accepting corrupted data
- Inject duplicate domain events and confirm aggregate handlers are idempotent
- Simulate repository write failure mid-aggregate-update and verify no partial state is persisted
