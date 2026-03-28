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

## Monitoring

Track RPC latency, error codes, and connection health to maintain visibility into service-to-service communication.

### Key Metrics

- `grpc_server_handled_total` (counter) — RPCs completed by the server, by service, method, and gRPC status code
- `grpc_server_handling_seconds` (histogram) — server-side RPC duration, by service and method
- `grpc_client_handled_total` (counter) — RPCs completed from the client perspective, by service, method, and status code
- `grpc_active_streams` (gauge) — number of currently open streaming RPCs

### Alerts

- Elevated rate of non-OK status codes for a specific method (backend regression or upstream issue)
- Server handling latency p99 exceeding SLO for critical methods
- Client-side deadline exceeded errors rising (server too slow or deadline too tight)

## Deployment

Manage proto schema compatibility and connection draining to avoid broken RPCs during rollouts.

### Rollout Implications

- gRPC uses persistent HTTP/2 connections — clients may not discover new server pods until connections are recycled or load balancer drains them
- Deploy backward-compatible proto changes first (additive fields only); breaking changes require a versioned service or two-phase rollout
- Drain in-flight RPCs before terminating pods — configure preStop hooks and terminationGracePeriodSeconds to allow streams to complete
- If using client-side load balancing, clients must re-resolve DNS or endpoints after server pods roll

### Pre-deploy Checklist

- Verify proto compatibility: new server can handle requests from old clients and vice versa
- Confirm health check and reflection services are registered on the new build
- Check that TLS certificates (if using mTLS) are valid and match the new pod identity

