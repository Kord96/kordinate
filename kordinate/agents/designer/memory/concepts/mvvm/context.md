## Testing

Verify that ViewModels are testable without views and that data binding keeps UI and state in sync.

### Unit Tests

- Test ViewModels in isolation without instantiating any view or UI framework
- Modify a ViewModel property and assert that observable notifications fire with the correct value
- Test commands/actions on the ViewModel and verify state transitions without touching the view layer

### Integration Tests

- Bind a view to a ViewModel, trigger a user action, and verify the view updates reflect the ViewModel state
- Verify two-way binding: modify the view input and assert the ViewModel property updates accordingly
- Test that disposing a view cleans up all subscriptions (no leaked observers)

### Architectural Tests

- Assert that ViewModel classes have no imports from the view or UI framework (decoupling check)
- Verify that the ViewModel is the single source of truth: no parallel state stored in the view layer

