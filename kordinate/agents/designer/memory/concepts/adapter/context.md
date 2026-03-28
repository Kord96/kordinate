## Testing

Verify that the adapter correctly translates between the target interface and the adaptee's API.

### Unit Tests

- Assert every method on the target interface delegates to the correct adaptee method
- Test data transformation: input to the adapter produces correctly mapped output from the adaptee
- Verify edge cases in translation (nulls, empty collections, type mismatches)

### Integration Tests

- Wire the adapter with a real adaptee and verify end-to-end behavior matches the target contract
- Swap adapters for different backends and verify the client code works identically

### Failure Injection

- Simulate adaptee failures and verify the adapter surfaces errors through the target interface cleanly

