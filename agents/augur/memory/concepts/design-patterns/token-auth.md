---
kind: concept
name: token-auth
signatures:
  concept: token-auth
  positive:
    strong:
    - bearer-token extraction plus cryptographic verification and claim checks
    - refresh or revocation logic around token lifecycle
    medium:
    - JWT parsing and validation around authenticated requests
    weak:
    - bearer-token handling with incomplete verification
  negative:
  - API keys, sessions, or OAuth callbacks mistaken for generic token auth
  - decode-only token parsing with no signature verification
  notes:
  - Keep this distinct from oauth-oidc, which adds delegated identity-provider flows.
type: pattern
abstraction:
- security
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: token-auth-bearer-verification
    prompt: Does the system authenticate requests with bearer tokens that are parsed
      and cryptographically verified?
    weight: 3
    signals:
    - Authorization
    - jwt.verify
    - jwt.decode
  - id: token-auth-lifecycle
    prompt: Are token expiry, refresh, or revocation part of the design rather than
      ad-hoc token parsing?
    weight: 2
    signals:
    - exp
    - refresh
    - jwks
monitoring:
  applies_to:
  - component
  - flow
  health_signals:
  - name: token_auth.validation.error.rate
    description: Failed token verification or claim-validation rate.
  - name: token_auth.expired.rate
    description: Requests rejected because the token expired or was revoked.
  business_metrics: []
  gaps:
  - Missing verification and expiry visibility hides auth failures and rotation bugs.
family: design-patterns
---

# Explanation

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
