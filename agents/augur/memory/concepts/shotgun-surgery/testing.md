---
description: Shotgun Surgery — testing guidance
type: supplementary
---
# Testing

- Measure change coupling: track which files are modified together across git history to identify scattered concerns
- Write regression tests for each location where the scattered concern appears before consolidating
- After remediation, test that the consolidated module covers all previous behavior with a single test suite
- Use architectural linting (ArchUnit, import-linter) to enforce that the concern does not re-scatter
- Test cross-cutting concerns (auth, logging, validation) in isolation once centralized
- Verify that removing duplicated logic from satellite files does not break callers via integration tests
- Run mutation testing on the consolidated module to confirm test coverage at the new single location
