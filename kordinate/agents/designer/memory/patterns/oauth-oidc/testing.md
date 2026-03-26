---
description: OAuth2/OpenID Connect — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test the full authorization flow, token validation logic, and edge cases around expiry and revocation.

### Unit Tests

- Verify JWT validation rejects tokens with wrong issuer, wrong audience, expired `exp`, and invalid signature
- Test PKCE code verifier/challenge generation and verification for public clients
- Assert that missing or malformed Authorization headers return 401, not 500
- Verify scope enforcement: requests with insufficient scopes are denied even with a valid token

### Integration Tests

- Run the full authorization code flow against a local IdP (Keycloak, mock OIDC server) and verify token exchange
- Test refresh token rotation: use a refresh token, verify a new pair is issued, and confirm the old refresh token is invalidated
- Verify callback handler rejects state parameter mismatches (CSRF protection)
- Test token caching: repeated requests with the same token do not re-validate against the IdP on every call

### Security Tests

- Attempt token reuse after revocation and verify rejection
- Send tokens signed with an unknown key and verify they are rejected, not silently accepted
- Verify tokens in localStorage are not accessible (httpOnly cookie enforcement)
