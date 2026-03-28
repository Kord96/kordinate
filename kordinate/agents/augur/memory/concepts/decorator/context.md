## Testing

Test each decorator in isolation and verify that stacking multiple decorators composes behavior correctly.

### Unit Tests

- Test the decorator independently by wrapping a mock/stub of the inner component and asserting the added behavior
- Verify the decorator delegates to the wrapped component — calls pass through and return values are forwarded
- Assert that the decorator does not alter the interface contract (same inputs produce expected outputs plus the decoration)
- Test decorator with a null or no-op inner component to verify the decoration logic works even when the inner does nothing

### Composition Tests

- Stack multiple decorators and verify behaviors compose in the correct order (e.g., logging wraps caching wraps validation)
- Test that removing a decorator from the chain does not break the remaining decorators
- Verify that decorator ordering matters where expected — swapping order should produce observably different behavior

