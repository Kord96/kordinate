---
description: OAuth2/OpenID Connect architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# OAuth2/OpenID Connect

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
