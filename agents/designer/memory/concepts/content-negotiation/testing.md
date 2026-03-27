---
description: Content/Protocol Negotiation — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that responses match the client's requested format and unsupported types are rejected cleanly.

### Unit Tests

- Send Accept: application/json and assert the response is JSON with correct Content-Type header
- Send Accept: application/xml and assert the response is XML (if supported)
- Send an unsupported Accept header and verify a 406 Not Acceptable response

### Integration Tests

- Test all supported media types end-to-end and verify response serialization is correct for each
- Verify quality-value negotiation: send Accept with multiple types and q-values, assert the highest-priority supported type wins

### Failure Injection

- Send a malformed Accept header and verify the server returns a clear error rather than crashing
