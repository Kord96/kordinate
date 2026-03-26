---
description: API Key Authentication — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify key validation, rejection of invalid credentials, and rate limiting behavior.

### Unit Tests

- Assert valid keys are accepted and the correct principal is resolved
- Assert invalid, expired, and revoked keys return 401 with appropriate error messages
- Test rate limiting: verify requests beyond the quota return 429

### Integration Tests

- Issue a real API key, make authenticated requests, and verify access to protected resources
- Test key rotation: old key is rejected after rotation, new key works immediately
- Verify audit trail entries are created for authentication events

### Failure Injection

- Simulate key store unavailability and verify requests fail closed (deny), not open
