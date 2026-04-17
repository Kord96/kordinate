---
description: Service Mesh architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction:
- infrastructure
- integration
status: primary
scope: cross-cutting
relationships:
  related_to:
  - service-discovery
  - mtls
  - retry
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Service Mesh

## Recognition

How to identify this pattern in code.

### Signatures

- Sidecar proxy containers: Envoy, Linkerd-proxy, Consul Connect proxy
- Istio CRDs: `VirtualService`, `DestinationRule`, `PeerAuthentication`, `AuthorizationPolicy`
- Linkerd CRDs: `ServiceProfile`, `TrafficSplit`, `Server`, `ServerAuthorization`
- Automatic sidecar injection annotations (`sidecar.istio.io/inject: "true"`, `linkerd.io/inject: enabled`)
- mTLS configuration between services (mesh-wide or per-service)
- Traffic policy definitions (retries, timeouts, circuit breaking at the mesh level)

### Confidence

- **high** -- sidecar proxies injected into pods, mesh CRDs managing traffic policies, mTLS enforced between services
- **medium** -- mesh control plane installed but sidecar injection is selective or traffic policies are minimal
- **low** -- Envoy or similar proxy present but configured manually without a mesh control plane

## Architecture

Look for transparent network-level service communication management via sidecar proxies controlled by a central control plane.

### Review Checklist

- mTLS is enforced mesh-wide (not just optional or permissive mode in production)
- Traffic policies (retries, timeouts) are set at the mesh level to avoid conflicting with application-level settings
- Sidecar resource limits are configured to prevent proxies from starving application containers
- Observability is leveraged (mesh provides metrics, traces, and access logs without application changes)
- Namespace-level policies control which services can communicate (zero-trust networking)
- Mesh upgrades have a tested rollout plan (control plane first, then data plane sidecars)

### Anti-patterns

- Leaving mTLS in permissive mode in production (allows plaintext bypass)
- Duplicate retry/timeout logic in both the mesh and the application (compounding retries)
- No resource limits on sidecar proxies (Envoy consuming excessive CPU/memory)
- Adding a mesh to a system with only a few services (operational overhead exceeds benefit)

### Relationship To Other Concepts

- Related to [service-discovery](/concepts/service-discovery) because mesh data planes typically rely on dynamic service identity and routing metadata.
- Related to [mtls](/concepts/mtls) because mTLS is one of the most common security capabilities moved into a service mesh.
- Related to [retry](/concepts/retry) when the mesh centrally applies traffic policies such as retries and timeouts.

### Boundary

Use `service-mesh` when cross-service networking concerns like mTLS, retries, routing, and observability are offloaded into a dedicated sidecar or data-plane layer.

Do not use it for any service-to-service communication stack. The key signal is an explicit mesh control/data plane managing inter-service traffic.
