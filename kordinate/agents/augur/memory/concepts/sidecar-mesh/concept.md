---
description: Sidecar mesh structure — services with co-located helper processes for cross-cutting concerns
type: structure-shape
abstraction: [infrastructure, deployment]
---
# Sidecar Mesh

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
