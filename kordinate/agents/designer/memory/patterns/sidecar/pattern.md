---
description: Sidecar architectural pattern
curated: true
scope: global
preloaded: none
---
# Sidecar

## Recognition

How to identify this pattern in code.

### Signatures

- Multi-container pod specs with two or more containers in a single pod definition
- `sidecar.istio.io/inject` annotation on pods or namespaces
- `linkerd.io/inject: enabled` annotation for Linkerd proxy injection
- `emptyDir` shared volumes mounted by both sidecar and main containers
- Container names like `istio-proxy`, `linkerd-proxy`, `envoy`, or `fluentd`
- `initContainers` running setup tasks before the main and sidecar containers start
- Ambassador containers handling outbound proxy or authentication concerns
- Sidecar resource limits defined separately from the main container

### Confidence

- **high** -- Multi-container pod specs with `istio-proxy`/`linkerd-proxy` containers, or `sidecar.istio.io/inject`/`linkerd.io/inject` annotations
- **medium** -- `emptyDir` shared volumes between containers in the same pod with `initContainers`, but without service mesh annotations
- **low** -- Multi-container pod specs where container roles are unclear or all containers appear to run business logic

## Architecture

Look for the sidecar handling only cross-cutting concerns with no business logic.

### Review Checklist

- Sidecar handles a single cross-cutting concern (logging, proxy, auth — not all three)
- Communication with main container uses localhost/shared volume — no network hops
- Sidecar lifecycle is tied to the main container (starts before, stops after)
- Main container functions (possibly degraded) if the sidecar is temporarily unavailable

### Anti-patterns

- Business logic in the sidecar — it should be infrastructure only
- Sidecar and main container with mismatched lifecycle (sidecar outlives the app)
- Too many sidecars per pod — resource overhead exceeds the benefit
- Tight version coupling between sidecar and main container deployments

## Monitoring

Track sidecar health and resource consumption to ensure sidecars do not degrade the main container.

### Key Metrics

- `sidecar_health` (gauge) — health status per sidecar (1=healthy, 0=degraded)
- `sidecar_cpu_usage_ratio` (gauge) — sidecar CPU usage as fraction of pod CPU limit
- `sidecar_memory_usage_bytes` (gauge) — sidecar memory consumption
- `sidecar_request_duration_seconds` (histogram) — latency of requests proxied through the sidecar
- `sidecar_errors_total` (counter) — errors in sidecar-to-main or sidecar-to-external communication

### Alerts

- Sidecar consuming more than expected share of pod resources (resource budget breach)
- Sidecar health check failing while main container is healthy (lifecycle mismatch)
- Sidecar proxy latency adding unacceptable overhead to main container requests
- Sidecar restart count exceeding threshold (unstable sidecar affecting pod stability)

## Deployment

Sidecar and main container version coordination is critical — mismatched versions can break shared interfaces.

### Rollout Implications

- Sidecar and main container images are updated together in a pod spec — ensure both versions are tested as a pair before rollout
- Sidecar must be ready before the main container starts serving if the main container depends on it (e.g., Envoy proxy) — use container startup ordering
- Shared volume mounts between sidecar and main container must have compatible file formats across versions
- Updating the sidecar image across the fleet (e.g., Istio proxy upgrade) restarts every pod — plan for fleet-wide rolling restart impact

### Pre-deploy Checklist

- Verify sidecar and main container version compatibility is tested together in staging
- Confirm shared volume mount paths and file format expectations match between sidecar and main container versions
- Check that pod disruption budgets account for fleet-wide restarts when upgrading a sidecar used across many services

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
