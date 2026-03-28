---
description: Test Doubles — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Verify that doubles implement the same interface/protocol as the real dependency (type check in tests)
- Test that mocks verify meaningful behavior (method called with correct args), not implementation details
- Verify stubs return realistic values — stubs that always succeed hide real failure paths
- Test that fakes for external services (database, API) behave consistently with the real implementation
- Assert that test doubles live in test directories and are never imported by production code
- Test spy assertions on observable outcomes, not internal call ordering
- Verify that double setup is extracted into reusable fixtures to avoid repetition across tests
- Test that production code works correctly when doubles are replaced with real dependencies (integration test)
