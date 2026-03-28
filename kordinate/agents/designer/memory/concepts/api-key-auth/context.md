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

## Monitoring

Track authentication outcomes, key usage patterns, and abuse signals.

### Key Metrics

- `api_auth_requests_total` (counter) — authentication attempts by outcome (success, invalid, expired)
- `api_key_usage_total` (counter) — requests per API key for usage tracking
- `api_auth_latency_seconds` (histogram) — time spent validating keys
- `api_rate_limit_exceeded_total` (counter) — rate limit hits per key

### Alerts

- Spike in invalid key attempts (potential credential stuffing)
- Single key exceeding rate limits repeatedly
- Expired key still receiving traffic (client misconfiguration)

