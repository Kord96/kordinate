---
kind: concept
name: sidecar-mesh
signatures: {}
source:
  memory_concept: memory/catalog/concepts/sidecar-mesh.md
type: structure-shape
abstraction:
- infrastructure
- deployment
scope: backend
status: primary
---

# Explanation

## Recognition

### Signatures

- Istio, Linkerd, or Consul Connect service mesh
- Envoy proxy sidecars injected into k8s pods
- Pod specs with multiple containers: main app + sidecar(s)
- Init containers for configuration or certificate injection
- mTLS between services handled by sidecar, not application
- Distributed tracing headers injected by sidecar proxy
- Traffic management (retries, timeouts, circuit breaking) at mesh level
- `istio-proxy` or `envoy` container in pod definitions
- Service mesh configuration: VirtualService, DestinationRule, AuthorizationPolicy

### Confidence

- **high** — service mesh (Istio/Linkerd) with sidecar injection, mTLS, and traffic management policies
- **medium** — sidecar containers for logging or monitoring but no service mesh control plane
- **low** — multi-container pods but sidecars are for unrelated purposes (e.g., log shipping only)

### Relationship To Other Concepts

- Related to [sidecar](/concepts/sidecar) because sidecar-mesh is a fleet-wide topology built from repeated sidecar deployment.
- Related to [service-mesh](/concepts/service-mesh) because service meshes are the most common reason to adopt this topology.
- Related to [mtls](/concepts/mtls) when identity and encryption are offloaded into the mesh sidecars.

### Boundary

Use `sidecar-mesh` when the important observation is a repeated topology where service workloads are paired with co-located sidecars to provide mesh behavior.

Do not use it for isolated sidecars or generic multi-container pods. The key signal is mesh-like repeated co-location across many services.
