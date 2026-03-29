---
description: State Machine — testing guidance
type: supplementary
---
# Testing

- Test every valid transition in the transition table: correct source state + event = expected target state
- Test that invalid transitions are rejected with clear errors, not silently ignored
- Verify entry/exit actions fire on the correct transitions and in the correct order
- Test guard conditions: transition should only occur when guards evaluate to true
- Test that state is persisted correctly if the machine must survive restarts
- Verify that terminal states are reachable from the initial state via valid transition paths
- Test concurrent transitions on the same entity to verify race condition protection
- Assert that direct state assignment bypassing the transition mechanism is impossible
