## Testing

Verify that factories produce correct product families and that products from different families are not mixed.

### Unit Tests

- Assert each concrete factory returns the correct product types for its family
- Verify products created by the same factory are compatible with each other
- Test that swapping the factory implementation changes all created products consistently

### Integration Tests

- Wire factories via DI container and verify the correct family is resolved per environment/configuration
- Test factory selection logic end-to-end with real configuration sources

### Failure Injection

- Supply an unknown family identifier and verify a clear error rather than a null product

