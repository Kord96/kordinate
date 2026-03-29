---
description: OAuth2/OpenID Connect — monitoring guidance
type: supplementary
---
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
