---
description: Micro-Frontend — testing guidance
type: supplementary
---
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
