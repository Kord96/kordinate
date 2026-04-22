---
kind: concept
name: sidecar
signatures: {}
source:
  memory_concept: memory/catalog/concepts/sidecar.md
type: pattern
abstraction:
- lifecycle
- infrastructure
- deployment
scope: cross-cutting
status: primary
---

# Explanation

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

### Relationship To Other Concepts

- Related to [service-mesh](/concepts/service-mesh) because mesh data planes are commonly implemented as sidecars.
- Related to [sidecar-mesh](/concepts/sidecar-mesh) when the structural pattern is not only one sidecar but a repeated sidecar-plus-service topology across the fleet.
- Related to [service-manager](/concepts/service-manager) because sidecars often participate in startup, readiness, and shutdown coordination for one service unit.

### Boundary

Use `sidecar` when auxiliary cross-cutting behavior is deployed as a co-located companion process or container next to the main workload.

Do not use it for any adjacent helper service. The key signal is tight co-location and lifecycle coupling with one main workload.
