## Testing

Verify that components receive dependencies through injection and that swapping implementations works without code changes.

### Unit Tests

- Inject mock dependencies and verify the component under test calls them with expected arguments
- Test constructor injection: missing required dependencies should fail fast at construction, not at first use
- Verify that components do not create their own dependencies internally — they should be purely injectable
- Test scoped lifetimes: request-scoped dependencies should produce distinct instances per scope

### Integration Tests

- Wire the real DI container and verify the full dependency graph resolves without circular dependency errors
- Swap a real implementation for a test double via the container and confirm the component behaves accordingly
- Test that the container disposes/cleans up dependencies in the correct order on shutdown

### Anti-pattern Detection

- Assert that service locator calls (container.resolve inside business logic) are absent — dependencies should be injected, not fetched

