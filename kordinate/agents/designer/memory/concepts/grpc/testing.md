---
description: gRPC/RPC — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Test RPC handlers, proto compatibility, and streaming behavior with both unit and integration approaches.

### Unit Tests

- Test each RPC handler with a request message and assert the response message matches expected values and status code
- Verify input validation: malformed or missing required fields should return INVALID_ARGUMENT, not INTERNAL
- Test error mapping: domain errors should translate to appropriate gRPC status codes (NOT_FOUND, PERMISSION_DENIED, etc.)
- Assert that server-side interceptors (auth, logging, metrics) fire in the correct order

### Integration Tests

- Stand up a real gRPC server in-process, call it via a client stub, and verify end-to-end behavior
- Test streaming RPCs: server-stream, client-stream, and bidirectional — verify message ordering and stream completion signals
- Verify deadline propagation: set a tight deadline on the client and assert the server receives and respects it

### Compatibility Tests

- Generate client stubs from the previous proto version and call the new server to verify backward compatibility
- Test that unknown fields in requests are ignored (not rejected) to support forward compatibility
