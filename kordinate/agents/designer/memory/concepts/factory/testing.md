---
description: Factory Method — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that the factory produces correctly configured instances and that all registered types are constructable.

### Unit Tests

- Call the factory with each supported type identifier and assert the returned object is the correct concrete type
- Test that factory-created objects are fully initialized — no nil fields or missing dependencies
- Verify that requesting an unknown type produces a clear error, not a nil return or panic
- Test parameterized factories: different configuration inputs should produce objects with correspondingly different behavior

### Registration Tests

- Assert that all expected types are registered with the factory at startup — catch missing registrations early
- If the factory supports runtime registration, verify that newly registered types are immediately available
- Test that duplicate registration is handled explicitly (error or override, not silent last-wins)

### Isolation Tests

- Verify factory-created objects are independent instances — mutating one does not affect another created by the same factory
