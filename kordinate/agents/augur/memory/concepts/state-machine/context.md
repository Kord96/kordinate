# Testing

- Test every valid transition in the transition table: correct source state + event = expected target state
- Test that invalid transitions are rejected with clear errors, not silently ignored
- Verify entry/exit actions fire on the correct transitions and in the correct order
- Test guard conditions: transition should only occur when guards evaluate to true
- Test that state is persisted correctly if the machine must survive restarts
- Verify that terminal states are reachable from the initial state via valid transition paths
- Test concurrent transitions on the same entity to verify race condition protection
- Assert that direct state assignment bypassing the transition mechanism is impossible

# Monitoring

- Track state transition counts per (source_state, event, target_state) tuple to detect unexpected paths
- Alert on rejected transitions — high rejection rates indicate callers sending invalid events
- Monitor time spent in each state to detect entities stuck in non-terminal states
- Track concurrent transition attempts on the same entity (race condition indicator)
- Alert on entities that have not progressed from a given state within an expected time window
- Dashboard showing state distribution: count of entities in each state over time
- Monitor guard condition evaluation failures to detect misconfigurations or data issues

