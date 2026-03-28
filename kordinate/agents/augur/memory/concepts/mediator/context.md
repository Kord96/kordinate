## Testing

Verify that components communicate exclusively through the mediator and handlers are isolated.

### Unit Tests

- Send a message through the mediator and assert the correct handler is invoked with the expected payload
- Verify that components have no direct references to other components (only to the mediator)
- Assert that an error in one handler does not prevent the mediator from dispatching to other handlers

### Integration Tests

- Register multiple handlers for different message types and verify each receives only its messages
- Test that unregistered message types produce a clear error or are silently ignored (per design intent)
- Verify message ordering: if ordering matters, assert handlers are invoked in registration order

### Edge Cases

- Send a message with no registered handlers and verify the mediator does not crash
- Register the same handler twice and verify it is invoked once (or twice, per design), not silently dropped

