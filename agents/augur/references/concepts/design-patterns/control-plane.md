---
kind: concept
name: control-plane
signatures: {}
source:
  memory_concept: memory/catalog/concepts/control-plane.md
type: pattern
abstraction:
- infrastructure
- architectural
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Central management layer distributing policy, configuration, topology, or identity information
- APIs or controllers reconciling desired state into many runtime components
- Mesh, cluster, or platform controllers pushing config to proxies, agents, or workers
- Separation between management concerns and high-volume request handling

### Confidence

- **high** -- one management layer governs configuration and policy for many runtime components without serving the main workload traffic itself
- **medium** -- central controllers exist, but boundaries between management and workload routing are only partially separated
- **low** -- admin endpoints or config services exist without clear plane separation

## Architecture

Look for a management authority that configures runtime behavior rather than directly carrying user workload traffic.

### Review Checklist

- Control responsibilities are clearly distinct from request-serving responsibilities
- Policy distribution and convergence are observable
- Control plane outages degrade safely rather than corrupting active runtime traffic
- Authn/authz for management actions is stricter than ordinary data traffic

### Anti-patterns

- Control plane also serving hot-path user traffic
- Opaque policy propagation with no visibility into version drift
- Runtime components tightly blocked on every control-plane request

### Relationship To Other Concepts

- Related to [data-plane](/concepts/data-plane) because the control plane configures or governs the runtime path that carries workload traffic.
- Related to [service-mesh](/concepts/service-mesh) when a mesh control layer distributes policy to proxies.
- Related to [service-discovery](/concepts/service-discovery) when a management layer maintains routable service identity and topology.

### Boundary

Use `control-plane` when management, policy, and coordination responsibilities are explicitly separated from workload execution.

Do not use it for any admin service. The key signal is authoritative runtime governance.
