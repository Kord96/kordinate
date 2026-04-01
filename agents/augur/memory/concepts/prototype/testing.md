---
description: Prototype — testing guidance
type: supplementary
---
## Testing

Verify clone correctness, deep-copy isolation, and that cloned objects satisfy all class invariants.

### Unit Tests

- Clone a prototype and verify the clone equals the original in value but is a distinct instance (not same reference)
- Modify the clone and verify the original is not affected (deep-copy isolation for nested mutable objects)
- Clone an object with circular references and verify the clone completes without infinite recursion
- Verify the cloned object satisfies all class invariants and validation rules

### Registry Tests

- Register prototypes in the registry and verify lookup by key returns a fresh clone each time
- Request a prototype for an unregistered key and verify a clear error, not a null or partial object
- Verify the registry's template objects are not mutated by clones (defensive copy on retrieval)

### Edge Cases

- Clone an object with lazy-initialized fields and verify those fields are correctly handled (initialized or deferred)
- Test shallow-copy vs deep-copy boundary: verify which fields are shared and which are independent
- Clone immutable objects and verify the pattern does not add unnecessary overhead (clone can return self)
