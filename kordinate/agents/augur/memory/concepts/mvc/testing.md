---
description: MVC — testing guidance
type: supplementary
---
## Testing

Verify layer separation by testing models, views, and controllers independently.

### Unit Tests

- Test models in isolation: business logic and data access without importing views or controllers
- Test controllers with mock models: assert correct delegation, input validation, and response selection
- Test views/templates with known model data and assert rendered output matches expectations

### Integration Tests

- Send HTTP requests through the full stack and verify the response body, status code, and headers
- Verify that invalid input is caught at the controller layer, not deep in the model
- Test that model changes propagate correctly to the view (no stale data in rendered output)

### Architectural Tests

- Assert that model modules have no imports from view or controller modules (enforce layer direction)
- Verify controllers are thin: no database queries or business logic in controller test files
- Check that views contain no data mutation or business logic
