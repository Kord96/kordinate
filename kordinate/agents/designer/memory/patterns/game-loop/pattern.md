---
description: Game Loop architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Game Loop

## Recognition

How to identify this pattern in code.

### Signatures

- Main loop structure: `while running: process_input(); update(dt); render()`
- Delta time (`dt`) calculation between frames for frame-rate independence
- Fixed timestep accumulator pattern separating physics/logic updates from rendering
- Tick rate or update rate constants (e.g., `TICK_RATE = 60`, `FIXED_DT = 1/60`)
- `requestAnimationFrame` in browser-based implementations
- Sleep or vsync calls to cap frame rate
- Interpolation between previous and current state for smooth rendering
- Separate `fixed_update()` and `update()` methods

### Confidence

- **high** — explicit `while` loop with input/update/render phases and delta time tracking
- **medium** — `requestAnimationFrame` callback with `dt` parameter and state update logic
- **low** — periodic timer or interval calling an update function with elapsed time

## Architecture

Look for a well-structured main loop with clear phase separation and proper timestep handling.

### Review Checklist

- Input processing is separated from state updates and rendering
- Fixed timestep used for deterministic simulation (physics, game logic)
- Variable timestep or interpolation used for rendering smoothness
- Delta time is capped to prevent spiral-of-death on long frames
- Loop handles pause, resume, and graceful shutdown cleanly
- Frame timing is measured accurately (high-resolution timer, not wall clock)

### Anti-patterns

- Using variable timestep for physics or game logic (non-deterministic behavior)
- No delta time cap, causing simulation explosions after a lag spike
- Mixing input handling, logic updates, and rendering in a single function
- Busy-waiting without sleep or vsync (100% CPU for no benefit)
