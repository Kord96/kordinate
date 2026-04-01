---
description: Bridge — testing guidance
type: supplementary
---
## Testing

Verify that abstraction and implementation vary independently and all combinations work correctly.

### Unit Tests

- Test each implementation through the abstraction interface and verify correct delegation
- Swap implementations at runtime and assert the abstraction behavior changes accordingly
- Verify new implementations can be added without modifying the abstraction

### Integration Tests

- Test all abstraction-implementation combinations to ensure cross-product compatibility
- Wire via DI and verify the correct implementation is selected per configuration

### Failure Injection

- Inject a failing implementation and verify the abstraction surfaces errors cleanly to callers
