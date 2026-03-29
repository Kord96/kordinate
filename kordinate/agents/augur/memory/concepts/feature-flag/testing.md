---
description: Feature Flag/Toggle — testing guidance
type: supplementary
---
## Testing

Test both flag paths to ensure neither the enabled nor disabled code path rots or contains latent bugs.

### Unit Tests

- Test the code path with the flag enabled and assert the new behavior activates correctly
- Test the code path with the flag disabled and assert the old behavior is preserved
- Verify that flag evaluation with no configuration returns the expected safe default
- Test percentage rollouts: for a deterministic user ID, assert the flag resolves to the expected variant

### Integration Tests

- Toggle a flag in the test environment and verify the running application responds to the change within the expected polling interval
- Test flag-dependent features end-to-end with both flag states to prevent regression in either path
- Verify that flag overrides in test environments do not leak to production configuration

### Lifecycle Tests

- After removing a flag from code, assert that references to it no longer exist — catch stale flag evaluations at build time
- Test that the system behaves correctly when the flag service is unreachable (graceful fallback to defaults)
