# Testing

- Test signature verification: a token signed with the wrong key or modified payload must be rejected
- Verify claim validation: expired `exp`, wrong `iss`, wrong `aud` tokens are all rejected
- Test the `none` algorithm attack: a token with `alg: none` must be rejected regardless of payload
- Test refresh token flow: valid refresh produces new access token, expired refresh is rejected
- Verify refresh token rotation: a used refresh token cannot be reused (one-time use)
- Test token revocation: after logout, previously valid tokens are rejected
- Assert that tokens are not stored in localStorage — verify httpOnly cookie or memory-only storage
- Test that token payloads do not contain sensitive data (PII, secrets) by decoding and inspecting

# Monitoring

- Track token validation failure rates — spikes indicate expired tokens, key rotation issues, or attacks
- Alert on `none` algorithm or algorithm mismatch in token verification (algorithm confusion attack)
- Monitor refresh token usage rates and alert on anomalous patterns (bulk refresh, reuse of rotated tokens)
- Track JWKS endpoint availability — key fetch failures block all token verification
- Alert on tokens with abnormally long TTLs that bypass the expected short-lived access token policy
- Dashboard showing token issuance rate, validation success/failure ratio, and refresh frequency
- Monitor token revocation/blacklist size and lookup latency to ensure it does not become a bottleneck

