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

## Monitoring

Track token lifecycle health and authentication flow success rates.

### Key Metrics

- `oauth_token_issued_total` (counter) -- tokens issued by grant type (authorization_code, refresh_token, client_credentials)
- `oauth_token_validation_errors_total` (counter) -- failed validations by reason (expired, invalid_signature, wrong_audience)
- `oauth_authorization_latency_seconds` (histogram) -- end-to-end authorization code flow duration
- `oauth_refresh_failures_total` (counter) -- refresh token failures (expired, revoked, reuse detected)
- `oidc_discovery_fetch_errors_total` (counter) -- failures fetching the well-known configuration or JWKS

### Alerts

- Token validation error rate exceeds baseline (possible key rotation issue or misconfigured audience)
- Refresh token failure spike (may indicate mass token revocation or IdP outage)
- OIDC discovery endpoint unreachable for more than one polling interval
- Authorization flow latency exceeds SLA threshold (IdP or callback handler degraded)

## Deployment

Coordinate with IdP configuration and ensure secrets are rotated safely during rollouts.

### Rollout Implications

- Client secrets must be available in the new deployment before the old one is terminated (use Kubernetes Secrets, not env vars baked into images)
- JWKS key rotation at the IdP can invalidate cached keys -- ensure the service refetches JWKS on signature validation failure
- Redirect URI changes must be registered with the IdP before deploying the code that uses them
- Rolling deployments with mixed old/new pods must agree on the same token validation rules (audience, issuer, scopes)

### Pre-deploy Checklist

- Confirm client_id and client_secret are present in the secret store for the target environment
- Verify redirect_uri registered at the IdP matches the new deployment's callback URL
- Test OIDC discovery endpoint reachability from the deployment network
- Ensure JWKS cache TTL is short enough to pick up key rotations within the expected window

