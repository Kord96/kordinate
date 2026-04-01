---
description: Unit of Work — testing guidance
type: supplementary
---
# Testing

- Test that commit flushes all tracked changes atomically — partial commits should not be possible
- Test that rollback on failure reverts all changes, not just the last write
- Verify that all repository operations within a use case share the same UoW instance
- Test nested units of work: ensure savepoints are used or nesting is explicitly prohibited
- Assert that the UoW lifetime is scoped to the request or use case, not a singleton
- Test exception handling: an error in one repository operation should trigger full rollback
- Verify that no individual repository method commits independently of the UoW boundary
- Test that long-lived UoW instances are detected and prevented (session leak protection)
