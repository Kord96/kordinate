---
description: API Gateway architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# API Gateway


## Recognition

How to identify this pattern in code.

### Signatures

- Kong, Envoy, NGINX Ingress, or Traefik as the gateway runtime
- AWS API Gateway or similar managed gateway service
- `Ingress` or `IngressRoute` CRDs in Kubernetes manifests
- `HTTPRoute` resources from the Gateway API spec
- Zuul or Spring Cloud Gateway in Java service configurations
- Rate limiting middleware configured at the gateway layer
- Auth middleware (JWT validation, API key checks) applied at the gateway before backend routing

### Confidence

- **high** -- dedicated gateway service with `Ingress`/`HTTPRoute` CRDs, rate limiting, and auth middleware all present
- **medium** -- gateway runtime (Kong, Envoy, Traefik) deployed with routing rules but cross-cutting concerns partially handled elsewhere
- **low** -- reverse proxy configuration (NGINX, HAProxy) performing routing without explicit rate limiting or auth enforcement

## Architecture

Look for the gateway being a thin routing/policy layer with no business logic.

### Review Checklist

- Gateway handles cross-cutting concerns only: auth, rate limiting, routing
- No business logic in the gateway — it delegates to backend services
- Timeouts and circuit breakers configured for each upstream backend
- Request/response transformation is minimal and well-documented
- Gateway failure mode is defined (fail open vs. fail closed)

### Anti-patterns

- Business logic creeping into the gateway (becomes a monolith bottleneck)
- Gateway as single point of failure with no redundancy or health checks
- Tight coupling between gateway routing rules and backend implementation details
