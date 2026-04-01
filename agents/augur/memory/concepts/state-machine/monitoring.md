---
description: State Machine — monitoring guidance
type: supplementary
---
# Monitoring

- Track state transition counts per (source_state, event, target_state) tuple to detect unexpected paths
- Alert on rejected transitions — high rejection rates indicate callers sending invalid events
- Monitor time spent in each state to detect entities stuck in non-terminal states
- Track concurrent transition attempts on the same entity (race condition indicator)
- Alert on entities that have not progressed from a given state within an expected time window
- Dashboard showing state distribution: count of entities in each state over time
- Monitor guard condition evaluation failures to detect misconfigurations or data issues
