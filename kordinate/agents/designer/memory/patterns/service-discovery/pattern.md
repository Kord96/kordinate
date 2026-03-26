---
description: Service Discovery architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
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
