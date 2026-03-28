---
description: Strategy — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test each concrete strategy independently against the shared interface contract
- Verify that strategy selection logic (config, factory, runtime parameter) picks the correct implementation
- Test that the context class delegates correctly without knowing which strategy is active
- Assert that adding a new strategy does not require modifying existing strategies or the context
- Test strategy interchangeability: swap implementations and verify the context still works correctly
- Verify that strategies are stateless or that their state is scoped to a single execution
- Test edge cases for each strategy where behavior diverges from the others
