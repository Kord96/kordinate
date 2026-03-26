---
description: Sidecar — testing guidance
curated: true
scope: global
preloaded: none
---
## Testing

Verify inter-container communication, lifecycle ordering, and main container resilience when the sidecar degrades.

### Unit Tests

- Test sidecar interface contract: assert the main container can communicate with the sidecar over localhost or shared volume as expected
- Verify sidecar configuration parsing: inject invalid config and assert the sidecar fails with a descriptive error, not silent misconfiguration
- Test main container degraded mode: disable the sidecar interface and assert the main container continues operating with reduced functionality
- Assert sidecar resource isolation: verify the sidecar respects its own CPU and memory limits independent of the main container

### Integration Tests

- Deploy the full pod (main + sidecar) and verify end-to-end request flow through the sidecar proxy to the main container
- Test lifecycle ordering: verify the sidecar starts and is ready before the main container begins accepting traffic
- Verify that sidecar upgrades (new image version) can be rolled out independently without restarting the main container if supported

### Failure Injection

- Crash the sidecar process and verify the main container detects the failure and operates in degraded mode
- Introduce latency in the sidecar proxy and verify the main container's timeout handling prevents cascading slowdowns
- Simulate sidecar OOM kill and verify the pod's restart policy recovers the sidecar while the main container remains running
