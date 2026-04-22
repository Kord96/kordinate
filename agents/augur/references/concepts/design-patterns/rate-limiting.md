---
kind: concept
name: rate-limiting
signatures:
  concept: rate-limiting
  positive:
    strong:
    - explicit limiter middleware or shared-state counters enforcing request thresholds
    - 429 responses and client-facing limit metadata
    medium:
    - throttle decorators or per-client counters with visible enforcement
    weak:
    - delays or sleeps that resemble naive throttling
  negative:
  - logging or metrics only, with no actual enforcement
  - one-off backpressure code mistaken for a reusable rate-limiting system
  notes:
  - Rate limiting is about enforced policy, not merely observing request volume.
source:
  memory_concept: memory/catalog/concepts/rate-limiting.md
type: pattern
abstraction:
- security
- resilience
scope: cross-cutting
status: primary
review_questions:
  threshold: 5
  entries:
  - id: rate-limiting-enforced-thresholds
    prompt: Does the system enforce explicit request thresholds with a client-facing
      denial behavior such as HTTP 429?
    weight: 3
    signals:
    - rateLimit
    - Limiter
    - 429
  - id: rate-limiting-shared-state
    prompt: In distributed deployments, is rate-limit state shared rather than isolated
      per instance?
    weight: 2
    signals:
    - Redis
    - INCR
    - windowMs
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: rate_limit.rejection.rate
    description: Rate of requests denied by throttling policy.
  - name: rate_limit.backend.error.rate
    description: Failures in the shared counter or limiter backend.
  business_metrics: []
  gaps:
  - Missing reject-rate and backend-health signals makes throttling effectiveness
    hard to trust.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Request counters per client/IP with time window tracking
- Algorithm implementations: sliding window, token bucket, leaky bucket, fixed window
- HTTP `429 Too Many Requests` response status code
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`
- Libraries: `ratelimit` (Python), `express-rate-limit` (Node), `rack-attack` (Ruby)
- Redis-based counters with TTL for distributed rate limiting (`INCR` + `EXPIRE`, `SETNX`)
- Nginx `limit_req` / `limit_conn` directives in configuration

### Confidence

- **high** -- rate limit middleware with configurable thresholds, 429 responses with rate limit headers, and a counter store (Redis/in-memory)
- **medium** -- request counting logic or throttle decorators present but no standard rate limit headers returned
- **low** -- delays or sleep calls injected to slow down processing (naive throttling without proper rate limiting)

## Architecture

Look for consistent enforcement at the API gateway or middleware layer with configurable limits per client or endpoint.

### Review Checklist

- Rate limits are applied at the correct granularity (per user, per API key, per IP, per endpoint)
- Distributed deployments share rate limit state (Redis or equivalent) to prevent per-instance limits
- Rate limit responses include standard headers so clients can self-throttle
- Different tiers or endpoints have appropriate limits (auth endpoints stricter, read endpoints more lenient)
- Rate limiting is applied before expensive operations (not after processing the request)

### Anti-patterns

- Per-instance rate limiting in a multi-replica deployment (each replica allows the full limit)
- No rate limit headers in responses (clients cannot adapt their request rate)
- Applying the same limit to all endpoints regardless of cost or sensitivity
- Rate limiting only by IP (breaks for clients behind NAT or shared proxies)

### Relationship To Other Concepts

- Related to [api-gateway](/concepts/api-gateway) because gateways often enforce ingress rate limits centrally.
- Related to [backpressure](/concepts/backpressure) because both protect downstream capacity, though backpressure is usually flow-control while rate limiting is quota enforcement.
- Related to [circuit-breaker](/concepts/circuit-breaker) when both are used to prevent overload and cascading failures.

### Boundary

Use `rate-limiting` when the system explicitly enforces quotas over time or tokens for requests, events, or client operations.

Do not use it for generic retries, queue backlogs, or concurrency caps unless there is a real rate or quota policy.
