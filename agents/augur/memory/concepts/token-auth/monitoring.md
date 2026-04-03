---
description: Token-Based Authentication (JWT) — monitoring guidance
---
## Monitoring

Track token validation outcomes, key infrastructure health, and refresh token lifecycle for security visibility.

### Key Metrics

- `token_validation_total` (counter) — token verifications partitioned by result (valid, expired, invalid_signature, malformed)
- `token_algorithm_mismatch_total` (counter) — tokens presenting an unexpected or disallowed algorithm (none, algorithm confusion)
- `token_refresh_total` (counter) — refresh token usage partitioned by outcome (success, expired, reuse_detected)
- `token_jwks_fetch_latency_seconds` (histogram) — time to retrieve signing keys from the JWKS endpoint
- `token_revocation_list_size` (gauge) — entries in the token blacklist/revocation store
- `token_revocation_lookup_latency_seconds` (histogram) — time to check a token against the revocation list

### Alerts

- Token validation failure rate spike (mass expiry, key rotation issue, or attack)
- Algorithm mismatch or `none` algorithm detected (algorithm confusion attack attempt)
- Rotated refresh token reused (token theft indicator)
- JWKS endpoint unavailable (blocks all token verification)
- Tokens with abnormally long TTLs bypassing the short-lived access token policy
