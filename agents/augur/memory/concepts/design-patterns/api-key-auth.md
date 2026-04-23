---
kind: concept
name: api-key-auth
signatures:
  concept: api-key-auth
  positive:
    strong:
    - explicit API key header extraction with managed validation
    - key lifecycle endpoints or quota enforcement
    medium:
    - middleware validating API keys against storage or cache
    weak:
    - API key checks with unclear lifecycle or rotation behavior
  negative:
  - static key comparison in source code
  - bearer-token or session logic misclassified as API key auth
  notes:
  - Keep this distinct from oauth-oidc and token-auth; API keys are credential tokens,
    not delegated identity flows.
type: pattern
abstraction:
- security
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: api-key-auth-header-validation
    prompt: Are API keys extracted from request headers and validated against a managed
      store rather than compared as hardcoded secrets?
    weight: 3
    signals:
    - X-API-Key
    - APIKeyHeader
    - compare_digest
  - id: api-key-auth-lifecycle-controls
    prompt: Does the system treat keys as first-class credentials with revocation,
      tenant mapping, or quota controls?
    weight: 2
    signals:
    - revoke
    - quota
    - tenant
monitoring:
  applies_to:
  - component
  - dependency
  - flow
  health_signals:
  - name: api_key_auth.failure.rate
    description: Failed API key validation rate for protected endpoints.
  - name: api_key_auth.revocation.hit.rate
    description: Requests rejected because the key is revoked or inactive.
  business_metrics: []
  gaps:
  - Missing auth-failure and revocation visibility hides abuse and misconfigured clients.
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `X-API-Key` header extraction in middleware or gateway configuration
- `?api_key=` or `?key=` query parameter parsing
- API key validation middleware looking up keys in a database or cache
- Key-to-tenant or key-to-user mapping tables
- Rate limiting and quota enforcement per API key
- Key generation and revocation endpoints (`POST /api-keys`, `DELETE /api-keys/{id}`)
- Key rotation support with grace periods for old keys
- Key hashing before storage (keys stored as hashes, not plaintext)

### Confidence

- **high** -- `X-API-Key` header extraction, key lookup against a store with tenant mapping, and rate limiting per key
- **medium** -- API key validation present but keys used only for identification without rate limiting or tenant isolation
- **low** -- Static key comparison in code or config (hardcoded key check without a proper key management system)

## Architecture

Look for API key lifecycle management with secure storage, tenant isolation, and usage controls.

### Relationship To Other Concepts

- `api-key-auth` is for programmatic credentials, not delegated user identity.
- Prefer `oauth-oidc` for delegated authorization flows and `token-auth` for bearer-token user auth.

### Review Checklist

- API keys are generated with sufficient entropy (256+ bits, cryptographically random)
- Keys are hashed before storage (never stored in plaintext in the database)
- Key validation is constant-time to prevent timing attacks
- Rate limiting and quota enforcement are applied per key
- Key revocation is immediate (not cached for extended periods after revocation)
- Keys are transmitted only in headers, never in URLs (URLs are logged by proxies and browsers)

### Anti-patterns

- Hardcoding API keys in source code or configuration files checked into version control
- Storing keys in plaintext in the database (compromised DB exposes all keys)
- Using API keys as the sole authentication for sensitive operations (keys lack identity binding, prefer OAuth for user context)
- Passing keys in URL query parameters (logged in access logs, browser history, and referrer headers)

### Boundary

Use `api-key-auth` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
