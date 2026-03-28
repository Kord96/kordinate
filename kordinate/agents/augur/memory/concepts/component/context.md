## Testing

Test components in isolation with defined inputs and outputs, then verify composition behavior.

### Unit Tests

- Render/execute the component with known props/inputs and assert the output matches expectations
- Test component lifecycle: initialization, update on input change, and cleanup/teardown
- Verify default behavior when optional inputs are omitted

### Integration Tests

- Compose parent and child components together and verify data flows correctly through the hierarchy
- Test event propagation: child emits an event, parent handles it, and state updates accordingly
- Verify slot/projection content renders in the correct location

### Failure Injection

- Supply invalid input types and verify the component surfaces a validation error rather than crashing

