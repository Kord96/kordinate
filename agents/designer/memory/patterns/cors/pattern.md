---
description: CORS architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
---
# CORS (Cross-Origin Resource Sharing)

## Recognition

How to identify this pattern in code.

### Signatures

- `Access-Control-Allow-Origin` response headers
- CORS middleware in the HTTP pipeline (`flask-cors`, `cors()` in Express, `@CrossOrigin` in Spring)
- Preflight `OPTIONS` request handling
- `allowed_origins`, `allow_methods`, `allow_headers` configuration
- `Access-Control-Allow-Credentials: true` for cookie-based auth
- Origin whitelist or regex matching logic
- `Vary: Origin` header in responses

### Confidence

- **high** -- explicit CORS middleware with a configured origin allowlist and preflight handling
- **medium** -- CORS headers present but using wildcard `*` origin without credential restrictions
- **low** -- scattered `Access-Control-*` headers set manually in individual route handlers

## Architecture

Look for centralized CORS policy enforcement with explicit origin allowlisting.

### Review Checklist

- Origins are explicitly allowlisted -- no wildcard `*` when credentials are enabled
- CORS configuration is centralized in middleware, not scattered across handlers
- Preflight `OPTIONS` requests are handled correctly with appropriate cache headers
- `Access-Control-Max-Age` is set to reduce preflight request frequency
- Allowed methods and headers are restricted to what the API actually uses

### Anti-patterns

- `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true`
- Reflecting the request Origin header back without validation (open relay)
- CORS headers set inconsistently across different endpoints
- No `Vary: Origin` header causing incorrect caching of CORS responses
