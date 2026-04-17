---
description: Token-Based Authentication (JWT) architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction:
- security
status: primary
scope: backend
relationships:
  disambiguates:
  - session-auth
  - api-key-auth
  related_to:
  - oauth-oidc
  - route-guard
  - rbac
aliases: []
disambiguates_from:
- session-auth
- api-key-auth
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# Token-Based Authentication (JWT)

## Recognition

How to identify this pattern in code.

### Signatures

- `Authorization: Bearer <token>` header extraction in middleware
- JWT decode/verify calls (`jwt.decode()`, `jwt.verify()`, `jwt.encode()`)
- Token claims parsing: `exp`, `iat`, `sub`, `iss`, `aud`
- Refresh token flow with separate `/refresh` or `/token` endpoint
- Stateless validation against a signing key or JWKS endpoint
- `jsonwebtoken` (Node), `PyJWT` (Python), `jose` (JS/Rust), `golang-jwt` (Go) library imports
- JWKS URI configuration for key rotation (`/.well-known/jwks.json`)
- Token blacklist or revocation check for logout support

### Confidence

- **high** -- `Authorization: Bearer` extraction, JWT signature verification with `exp`/`iss`/`aud` claim validation, and refresh token flow implemented
- **medium** -- JWT decode present with expiry check but no signature verification or refresh flow visible
- **low** -- Bearer token in headers but no JWT-specific parsing (could be opaque tokens or API keys)

## Architecture

Look for stateless token validation with proper signing, claim verification, and secure token lifecycle management.

### Relationship To Other Concepts

- `token-auth` is the generic bearer-token or JWT auth pattern.
- Prefer `oauth-oidc` when delegated identity-provider flows and authorization-code exchanges are central.
- Prefer `api-key-auth` when the credential is an API key rather than a user or session token.

### Review Checklist

- Tokens are signed with a strong algorithm (RS256/ES256 for asymmetric, HS256 minimum for symmetric)
- Signature is always verified before trusting claims (never decode-only)
- Expiry (`exp`), issuer (`iss`), and audience (`aud`) claims are validated on every request
- Access tokens have short TTL (minutes, not hours) with refresh tokens for renewal
- Refresh tokens are stored securely and rotated on use (one-time use)
- Token revocation mechanism exists for logout and compromise scenarios

### Anti-patterns

- Using `none` algorithm or allowing algorithm switching in verification (algorithm confusion attack)
- Storing JWTs in localStorage (vulnerable to XSS) instead of httpOnly cookies or memory
- Long-lived access tokens with no refresh flow (hours or days without rotation)
- Including sensitive data (PII, secrets) in token payload (JWTs are base64-encoded, not encrypted)

### Boundary

Use `token-auth` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
