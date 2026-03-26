---
description: API Key Authentication architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# API Key Authentication

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
