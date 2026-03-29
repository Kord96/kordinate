---
description: Token-Based Authentication (JWT) — monitoring guidance
type: supplementary
---
# Monitoring

- Track token validation failure rates — spikes indicate expired tokens, key rotation issues, or attacks
- Alert on `none` algorithm or algorithm mismatch in token verification (algorithm confusion attack)
- Monitor refresh token usage rates and alert on anomalous patterns (bulk refresh, reuse of rotated tokens)
- Track JWKS endpoint availability — key fetch failures block all token verification
- Alert on tokens with abnormally long TTLs that bypass the expected short-lived access token policy
- Dashboard showing token issuance rate, validation success/failure ratio, and refresh frequency
- Monitor token revocation/blacklist size and lookup latency to ensure it does not become a bottleneck
