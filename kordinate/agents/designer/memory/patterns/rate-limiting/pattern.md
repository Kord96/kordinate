---
description: Rate Limiting/Throttling architectural pattern
curated: true
scope: global
preloaded: none
---
# Rate Limiting/Throttling

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
