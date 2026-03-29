---
description: Flyweight — testing guidance
type: supplementary
---
## Testing

Verify that shared intrinsic state is reused across instances and that extrinsic state is correctly separated.

### Unit Tests

- Request the same flyweight key twice and assert both references point to the same object (identity equality)
- Request different flyweight keys and assert distinct objects are returned
- Verify intrinsic (shared) state is immutable — attempts to modify it should fail or have no effect on other consumers
- Test that extrinsic state passed at call time does not contaminate the shared flyweight instance

### Memory Tests

- Create a large number of flyweight instances with the same key and verify memory usage remains constant (not linear)
- Compare memory footprint with and without flyweight sharing to confirm the pattern provides measurable savings

### Thread Safety Tests

- Access the flyweight factory from multiple threads concurrently and verify no duplicate instances are created for the same key
- Assert that concurrent reads of shared intrinsic state produce consistent results without synchronization from the caller
