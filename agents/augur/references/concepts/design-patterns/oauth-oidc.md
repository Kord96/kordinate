---
kind: concept
name: oauth-oidc
signatures:
  concept: oauth-oidc
  positive:
    strong:
    - authorization-code or OIDC discovery flows with delegated identity provider
      integration
    - token validation tied to issuer, audience, and client configuration
    medium:
    - OAuth libraries plus redirect or callback handling
    weak:
    - JWT validation alone with no visible delegation flow
  negative:
  - local session or API-key auth mislabeled as OAuth
  - generic token-auth with no identity provider contract
  notes:
  - Keep this distinct from token-auth; OAuth/OIDC is about delegated identity and
    authorization flows.
source:
  memory_concept: memory/catalog/concepts/oauth-oidc.md
type: pattern
abstraction:
- security
scope: backend
status: primary
review_questions:
  threshold: 5
  entries:
  - id: oauth-oidc-delegated-flow
    prompt: Does the code implement or consume an OAuth or OIDC authorization flow
      with client credentials, redirect URIs, or discovery metadata?
    weight: 3
    signals:
    - create_authorization_url
    - fetch_token
    - openid-configuration
  - id: oauth-oidc-token-validation
    prompt: Are access or ID tokens validated as part of a delegated identity flow
      rather than just generic JWT auth?
    weight: 2
    signals:
    - id_token
    - client_id
    - NextAuth
monitoring:
  applies_to:
  - component
  - dependency
  - flow
  health_signals:
  - name: oauth.login.error.rate
    description: Failures during authorization or callback handling.
  - name: oauth.token.refresh.error.rate
    description: Failures refreshing or rotating delegated tokens.
  business_metrics: []
  gaps:
  - Missing callback and token-refresh visibility hides identity-provider integration
    issues.
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Authorization code flow endpoints: `/authorize`, `/token`, `/callback`
- Configuration fields: `client_id`, `client_secret`, `redirect_uri`, `scope`
- JWT validation logic parsing `id_token` or `access_token` with signature verification
- Bearer token extraction from `Authorization` header
- OIDC discovery endpoint: `/.well-known/openid-configuration`
- Libraries: `authlib`, `passport` (Node), `jose`, `python-jose`, `next-auth`, `oauthlib`
- Token refresh logic with `refresh_token` grant type

### Confidence

- **high** -- authorization code flow with `/authorize` and `/token` endpoints, JWT validation, and OIDC discovery URL configured
- **medium** -- `client_id`/`client_secret` in config with bearer token middleware but flow details unclear
- **low** -- JWT parsing present but no OAuth flow visible (could be custom auth)

## Architecture

Look for correct implementation of the OAuth2 authorization flow with proper token validation and secure credential handling.

### Relationship To Other Concepts

- `oauth-oidc` adds delegated identity-provider flows on top of token validation.
- It often coexists with `token-auth` because the resulting access tokens are still bearer tokens.
- Prefer `session-auth` or `api-key-auth` when no delegated identity provider is involved.

### Review Checklist

- Authorization code flow is used (not implicit flow) for server-side applications
- Token validation checks signature, expiry, issuer, and audience claims
- Client secrets are stored securely (not hardcoded in source, use env vars or secret stores)
- PKCE is used for public clients (SPAs, mobile apps) that cannot keep a client secret
- Refresh tokens are stored securely and rotated on use
- Scopes follow least-privilege principle

### Anti-patterns

- Using implicit flow for new applications (deprecated in OAuth 2.1)
- Skipping token signature verification or not validating issuer/audience claims
- Storing tokens in localStorage (vulnerable to XSS) instead of httpOnly cookies
- Hardcoding client secrets in source code or frontend bundles

### Boundary

Use `oauth-oidc` when the important observation is this specific architectural concern within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
