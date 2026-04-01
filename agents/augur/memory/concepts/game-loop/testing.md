---
description: Game Loop — testing guidance
type: supplementary
---
## Testing

Test update and render steps independently with controlled time inputs to verify deterministic behavior.

### Unit Tests

- Call the update step with a fixed delta time and assert game state changes match expected physics/logic
- Verify fixed-timestep accumulation: passing a large delta should invoke multiple fixed steps, not one large step
- Test that the render step interpolates between previous and current state for smooth visual output
- Assert that the loop handles zero delta time gracefully (no division by zero, no redundant updates)

### Determinism Tests

- Run the same input sequence with the same initial state and fixed timesteps, and assert identical final state (replay determinism)
- Verify that variable frame rates produce the same game-logic outcome when using fixed-step update with accumulator
- Test that serializing and restoring game state mid-loop produces identical subsequent behavior

### Performance Tests

- Measure frame time variance under load to detect update steps that exceed the target frame budget
- Verify the loop gracefully handles a "spiral of death" — when updates cannot keep up, it should cap catch-up iterations
