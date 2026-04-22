---
kind: concept
name: load-balancer
signatures: {}
source:
  memory_concept: memory/catalog/concepts/load-balancer.md
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

- Reverse proxy or platform component distributing requests across many backends
- Algorithms such as round-robin, least-connections, weighted routing, or consistent hashing
- Health-checked upstream pools with instance add/remove behavior
- Layer 4 or Layer 7 balancing via NGINX, HAProxy, Envoy, ALB, ELB, or ingress controllers
- Client-side balancing libraries selecting one endpoint from a discovered set

### Confidence

- **high** -- explicit balancing configuration or client-side policy distributes traffic across multiple equivalent instances
- **medium** -- platform ingress or proxy layer performs balancing but policies are mostly implicit
- **low** -- failover or static primary/secondary routing exists without ongoing distribution

## Architecture

Look for a component or policy that spreads traffic over interchangeable upstream targets.

### Review Checklist

- Health checks remove unhealthy targets promptly
- Balancing strategy matches traffic and workload characteristics
- Session affinity is used intentionally, not accidentally
- Observability exists for per-target error rate, latency, and saturation

### Anti-patterns

- Static target lists with no health awareness
- Uneven routing that overloads a subset of instances
- Layering many balancers without clear ownership of retry and failover behavior

### Relationship To Other Concepts

- Related to [service-discovery](/concepts/service-discovery) because discovery often provides the target set that balancing acts on.
- Related to [api-gateway](/concepts/api-gateway) when one ingress component both routes and balances traffic.
- Related to [rate-limiting](/concepts/rate-limiting) when edge traffic shaping and balancing interact under load.

### Boundary

Use `load-balancer` when request distribution across equivalent upstream targets is architecturally visible and important.

Do not use it for any reverse proxy. The key signal is active traffic distribution.
