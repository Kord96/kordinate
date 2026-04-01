---
description: Feature Envy — testing guidance
type: supplementary
---
## Testing

Use tests to detect and prevent feature envy by verifying methods operate primarily on their own class's data.

### Unit Tests

- Test that methods on a class use its own fields rather than reaching into collaborators for data
- After refactoring to move envious logic to the correct class, verify behavior is preserved with the same test inputs
- Assert that the refactored method requires fewer parameters from external objects (reduced coupling)
- Test the data-owning class's new method independently to confirm it encapsulates the logic correctly

### Code Review Heuristics

- If a test requires mocking more than two methods on a single collaborator, the method under test likely has feature envy
- Tests that break when an unrelated class's internal structure changes are a signal of misplaced behavior
- After extracting the envious logic, the original class's tests should simplify — fewer mocks, fewer setup steps

### Refactoring Verification

- Run the full test suite after moving methods to ensure no behavioral regression
- Verify that the moved method's new home has higher cohesion — it should access mostly local state
