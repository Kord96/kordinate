---
description: Tick-Based Simulation — testing guidance
type: supplementary
---
# Testing

- Test determinism: identical inputs at the same tick must always produce identical state
- Verify tick rate is decoupled from frame rate — simulation produces the same result at any render speed
- Test replay by recording per-tick inputs, replaying them, and comparing final state to the original run
- Verify that the tick counter is monotonic and never skips or repeats
- Test late or missing input handling: prediction, rollback, or pause behavior under network delay
- Test state snapshots: save at tick N, advance to tick N+10, restore to tick N, and verify state
- Assert that no non-deterministic operations (unseeded random, floating-point inconsistency) exist in tick updates
- Test lockstep synchronization between multiple clients exchanging inputs per tick
