---
description: Service Discovery architectural pattern
type: pattern
testable: true
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
  - service-mesh
  - api-gateway
  - load-balancer
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Service Discovery

## Recognition

How to identify this pattern in code.

### Signatures

- Service registry with registration and lookup APIs
- DNS-based discovery (`consul`, `eureka`, CoreDNS, K8s Service + DNS)
- `nslookup`, `dig`, or DNS resolution for service endpoints
- Service mesh with automatic endpoint discovery (Istio, Linkerd)
- Client-side discovery with load balancer (Ribbon, gRPC name resolution)
- Server-side discovery with reverse proxy or API gateway routing
- Health-checked service registration with TTL or heartbeat

### Confidence

- **high** -- Explicit service registry integration (Consul agent, Eureka client) or K8s Service resources with DNS-based resolution
- **medium** -- Environment variables or config pointing to service endpoints with health checking, but no formal registry
- **low** -- Hardcoded hostnames or IP addresses in config files with no dynamic resolution

## Architecture

Look for services registering themselves on startup and consumers resolving endpoints dynamically rather than using static addresses.

### Review Checklist

- Services register on startup and deregister on graceful shutdown
- Health checks are configured so unhealthy instances are removed from the registry
- Consumers resolve endpoints through the registry, not hardcoded addresses
- Stale registrations are cleaned up via TTL or lease expiry
- Discovery mechanism handles network partitions gracefully (cached endpoints, fallback)
- Load balancing strategy is defined (round-robin, least-connections, consistent hashing)

### Anti-patterns

- Hardcoded service addresses that require config changes and redeployment to update
- No health checking -- dead instances remain in the registry and receive traffic
- Registration without deregistration -- registry fills with stale entries over time
- Single point of failure in the discovery infrastructure with no fallback

### Relationship To Other Concepts

- Related to [service-mesh](/concepts/service-mesh) because meshes often rely on service discovery under the hood to route traffic correctly.
- Related to [api-gateway](/concepts/api-gateway) when gateways route to dynamic backend instances discovered at runtime.
- Related to [load-balancer](/concepts/load-balancer) because discovery often feeds the set of viable upstream targets to balance across.

### Boundary

Use `service-discovery` when services locate each other dynamically through a registry, DNS system, or platform control plane rather than fixed addresses.

Do not use it for static endpoint configuration. The defining property is dynamic service lookup.
