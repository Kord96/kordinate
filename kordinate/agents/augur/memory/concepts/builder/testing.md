---
description: Builder — testing guidance
type: supplementary
---
## Testing

Verify that step-by-step construction produces correct objects and that invalid build sequences are rejected.

### Unit Tests

- Build an object with all required steps and assert all fields are set correctly
- Test optional steps: omit optional configuration and verify sensible defaults
- Assert that calling build() without required steps raises a clear error

### Integration Tests

- Use the builder in its real context (e.g., constructing request objects, configs) and verify end-to-end
- Test director sequences if present: verify the director orchestrates builder steps in the correct order

### Failure Injection

- Supply conflicting configuration steps and verify the builder detects and rejects the inconsistency
