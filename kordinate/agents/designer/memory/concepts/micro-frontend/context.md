## Testing

Test each micro-frontend in isolation and verify correct composition within the shell application.

### Unit Tests

- Test each micro-frontend's components in isolation with its own test suite
- Verify that no direct imports exist between micro-frontends (module boundary enforcement)
- Assert that shared state contracts (events, shared store) match the expected schema

### Integration Tests

- Load the micro-frontend within the shell and verify routing, rendering, and inter-module communication
- Test that failure in one micro-frontend does not crash the shell or other micro-frontends (error boundary)
- Validate that shared dependencies are loaded once, not duplicated per micro-frontend

### Visual Regression Tests

- Capture screenshots of each micro-frontend in isolation and composed in the shell
- Assert that CSS from one micro-frontend does not leak into another (scoping validation)

## Deployment

Deploy micro-frontends independently while ensuring shared dependencies and the shell remain compatible.

### Rollout Implications

- Each micro-frontend should be independently deployable without requiring a full application redeploy
- Shared dependency versions (React, Angular) must be compatible across all deployed micro-frontends
- The shell application must handle missing or failed micro-frontend loads gracefully (error boundaries)
- Version the contract between shell and micro-frontends to detect breaking changes before deployment

### Pre-deploy Checklist

- Verify shared dependency versions are aligned across all micro-frontends and the shell
- Test the new micro-frontend version in isolation and composed within the shell before production
- Confirm import map or Module Federation remote URLs point to the correct deployment target
- Validate that CSS scoping prevents style leaks between the new version and existing micro-frontends

