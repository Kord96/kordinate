---
description: API Gateway architectural pattern
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

## Monitoring

Track request routing, upstream health, and policy enforcement to detect gateway degradation and abuse.

### Key Metrics

- `gateway_request_duration_seconds` (histogram) — end-to-end request latency by route and upstream
- `gateway_upstream_errors_total` (counter) — upstream failures by backend service and error class
- `gateway_rate_limit_rejected_total` (counter) — requests rejected by rate limiting
- `gateway_auth_failures_total` (counter) — authentication/authorization failures by type
- `gateway_upstream_health` (gauge) — health status per upstream backend (1=healthy, 0=down)

### Alerts

- Upstream error rate exceeding threshold for any backend
- Rate-limit rejections spiking (potential abuse or misconfigured limits)
- Authentication failure rate increasing sharply (credential stuffing or misconfiguration)
- Gateway latency p99 exceeding SLA (upstream slowness or gateway overload)

## Deployment

Route changes and upstream health checks during rollout determine whether traffic reaches the correct backends.

### Rollout Implications

- Route configuration changes should deploy separately from backend service changes — avoid deploying both simultaneously
- During rolling updates of backend services, the gateway must detect unhealthy upstream pods and stop routing to them
- Rate limit and auth policy changes take effect immediately on reload — verify new limits do not inadvertently block legitimate traffic
- Gateway reload or restart drops in-flight connections — use graceful reload mechanisms that drain existing connections

### Pre-deploy Checklist

- Verify upstream backend services are healthy and have sufficient capacity before deploying gateway route changes
- Confirm rate limit and auth policy changes have been tested against expected traffic patterns
- Check that health check intervals and thresholds are tuned for the rollout speed (avoid marking healthy pods as down during restart)

## Testing

Verify routing rules, cross-cutting policy enforcement, and graceful handling of upstream failures.

### Unit Tests

- Test routing rules: given a request path and method, assert it routes to the correct upstream backend
- Verify auth enforcement — requests with missing or invalid tokens are rejected before reaching any backend
- Test rate limiting logic: assert that requests exceeding the configured limit receive 429 responses
- Verify request/response transformation rules produce the expected output format

### Integration Tests

- Send requests through the gateway to real backend services and verify end-to-end routing correctness
- Test auth + rate limiting together: authenticated requests within limits succeed; over-limit requests are throttled regardless of valid auth
- Verify gateway behavior with multiple backends — route to each and confirm correct upstream selection under load

### Failure Injection

- Take a backend service down and verify the gateway returns a meaningful error (502/503) rather than hanging
- Simulate slow backend responses and verify gateway timeouts fire, returning errors to clients within SLA
- Kill the auth service and verify the gateway's fail-open or fail-closed policy matches its configuration
