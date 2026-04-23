---
kind: concept
name: tick-simulation
signatures: {}
type: pattern
abstraction:
- lifecycle
- realtime
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `tick()` or `step()` method called at a fixed rate with a tick counter
- Discrete time steps where all state advances atomically per tick
- `fixed_update()` distinct from frame-based rendering updates
- Tick counter or tick number used for ordering, replay, and synchronization
- Deterministic update functions: same inputs at same tick produce same outputs
- Lockstep networking where clients exchange inputs per tick
- Replay systems that record and replay per-tick inputs
- Simulation rate constants (e.g., `TICKS_PER_SECOND = 20`)

### Confidence

- **high** — `tick()` method with a tick counter, deterministic state updates, and replay or lockstep networking
- **medium** — fixed-rate `step()` function with discrete state transitions and a simulation clock
- **low** — periodic timer advancing state in uniform increments without explicit tick numbering

## Architecture

Look for deterministic discrete-time state progression with explicit tick ordering.

### Review Checklist

- Tick updates are deterministic: identical inputs at the same tick always produce the same state
- Tick rate is decoupled from frame rate (simulation runs independently of rendering)
- State snapshots or input logs enable replay from any tick
- Tick counter is monotonic and used as the canonical time reference
- Network synchronization uses tick-aligned input exchange, not wall-clock timestamps
- Late or missing inputs are handled explicitly (prediction, rollback, or pause)

### Anti-patterns

- Using wall-clock time instead of tick numbers for simulation ordering
- Non-deterministic operations (random without seed, floating-point inconsistencies) inside tick updates
- Coupling tick rate to frame rate, causing simulation speed to vary with performance
- No mechanism to handle missed or late ticks in networked scenarios

### Relationship To Other Concepts

- Related to [game-loop](/concepts/game-loop) because many realtime systems execute one simulation tick per main-loop update step.
- Related to [entity-component-system](/concepts/entity-component-system) because ECS worlds are often advanced in deterministic ticks.
- Related to [spatial-partitioning](/concepts/spatial-partitioning) when tick updates repeatedly query nearby entities or regions.

### Boundary

Use `tick-simulation` when state advances in explicit discrete ticks that provide the canonical simulation timeline.

Do not use it for generic schedulers or wall-clock-driven periodic jobs without simulation semantics.
