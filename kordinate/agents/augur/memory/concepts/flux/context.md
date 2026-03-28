## Testing

Test reducers as pure functions and verify the unidirectional data flow from action dispatch through state update to view render.

### Unit Tests

- Test each reducer with a given state and action, asserting the exact new state returned
- Verify reducers return the previous state unchanged for unknown action types
- Assert that reducers are pure: no mutations to the input state, no side effects, no API calls
- Test action creators produce correctly typed and shaped action objects
- Verify selectors compute derived state correctly from the store shape

### Integration Tests

- Dispatch a sequence of actions and assert the final store state matches the expected cumulative result
- Test middleware (thunks, sagas, epics) by dispatching an action and verifying the resulting async action sequence
- Verify that connected components re-render with the correct props when relevant state slices change

### State Management Tests

- Test that dispatching the same action sequence from the same initial state always produces identical final state (deterministic replay)
- Verify that large state trees remain performant — selectors with memoization should not recompute on unrelated state changes

