---
kind: concept
name: data-plane
signatures: {}
source:
  memory_concept: memory/catalog/concepts/data-plane.md
type: pattern
abstraction:
- infrastructure
- networking
scope: cross-cutting
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Runtime path that carries user, service, or event traffic at high volume
- Proxies, sidecars, workers, or forwarding components executing policies pushed from elsewhere
- Hot-path routing, filtering, encryption, or transformation on live traffic
- Explicit contrast with a management or control layer

### Confidence

- **high** -- one runtime layer handles live traffic while receiving configuration from a separate management authority
- **medium** -- request-serving components clearly differ from management components, but plane terminology is implicit
- **low** -- operational docs mention data-plane behavior without stable architectural separation

## Architecture

Look for the execution path that actually carries workload traffic, distinct from the layer that configures it.

### Review Checklist

- Data-plane responsibilities are clearly bounded to runtime traffic handling
- Hot-path latency, throughput, and failure behavior are observable
- Configuration changes can roll out safely without breaking active traffic
- Runtime components fail independently of management features when possible

### Anti-patterns

- Runtime traffic dependent on synchronous control-plane lookups for every request
- No clear ownership of hot-path policy enforcement
- Management and traffic components bundled together with conflicting availability requirements

### Relationship To Other Concepts

- Related to [control-plane](/concepts/control-plane) because the data plane carries workload behavior that the control plane governs.
- Related to [service-mesh](/concepts/service-mesh) when sidecar proxies form the traffic-carrying path.
- Related to [sidecar](/concepts/sidecar) because many data-plane implementations are attached to workloads as co-located proxies or agents.

### Boundary

Use `data-plane` when the traffic-carrying runtime path is architecturally distinct and important.

Do not use it for any service that processes data. The key signal is plane separation in runtime architecture.
