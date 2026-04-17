---
description: API Gateway architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- integration
- infrastructure
- security
status: primary
scope: cross-cutting
relationships:
  related_to:
  - bff
  - rate-limiting
  - server-route-registration
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
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

### Relationship To Other Concepts

- Related to [bff](/concepts/bff) because both sit in front of backend services, but a gateway is usually shared ingress infrastructure rather than frontend-specific shaping.
- Related to [rate-limiting](/concepts/rate-limiting) because gateways often enforce quota and throttling policies at ingress.
- Related to [server-route-registration](/concepts/server-route-registration) because gateway rules ultimately expose or route traffic to backend handlers.

### Boundary

Use `api-gateway` when the key architectural role is centralized ingress routing and cross-cutting policy enforcement for downstream services.

Do not use it for every reverse proxy or every backend API layer. If the logic mainly reshapes responses for one frontend or client family, prefer [bff](/concepts/bff).
