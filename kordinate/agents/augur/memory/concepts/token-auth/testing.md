---
description: Token-Based Authentication (JWT) — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test signature verification: a token signed with the wrong key or modified payload must be rejected
- Verify claim validation: expired `exp`, wrong `iss`, wrong `aud` tokens are all rejected
- Test the `none` algorithm attack: a token with `alg: none` must be rejected regardless of payload
- Test refresh token flow: valid refresh produces new access token, expired refresh is rejected
- Verify refresh token rotation: a used refresh token cannot be reused (one-time use)
- Test token revocation: after logout, previously valid tokens are rejected
- Assert that tokens are not stored in localStorage — verify httpOnly cookie or memory-only storage
- Test that token payloads do not contain sensitive data (PII, secrets) by decoding and inspecting
