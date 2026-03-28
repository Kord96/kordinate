## Testing

Verify preflight handling, allowed origins enforcement, and header propagation for cross-origin requests.

### Unit Tests

- Send an OPTIONS preflight and verify Access-Control-Allow-Origin matches the allowed origin
- Verify disallowed origins receive no CORS headers (request is rejected)
- Test Access-Control-Allow-Methods and Access-Control-Allow-Headers match the configured whitelist
- Verify Access-Control-Max-Age is set to reduce preflight frequency

### Integration Tests

- Make cross-origin requests from a browser-like client and verify the full preflight-then-request flow
- Test credentialed requests: verify Access-Control-Allow-Credentials is set and wildcard origin is not used

### Failure Injection

- Send a request with a spoofed Origin header not in the allow list and verify it is rejected

