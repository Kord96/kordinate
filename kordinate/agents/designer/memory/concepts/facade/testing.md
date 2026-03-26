---
description: Facade — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test the facade's simplified interface independently from the subsystems it wraps, then verify correct delegation.

### Unit Tests

- Mock the underlying subsystems and verify the facade calls them in the correct order with expected arguments
- Assert that the facade translates subsystem exceptions into its own simplified error types
- Test each facade method covers the documented use case — inputs map to the correct subsystem orchestration
- Verify the facade does not expose subsystem internals (return types, configuration objects) through its public API

### Integration Tests

- Wire the facade to real subsystem implementations and verify end-to-end behavior matches the simplified contract
- Test that subsystem failures are handled gracefully — the facade should provide meaningful errors, not raw subsystem exceptions
- Verify that the facade remains a thin coordination layer — business logic belongs in the subsystems, not the facade
