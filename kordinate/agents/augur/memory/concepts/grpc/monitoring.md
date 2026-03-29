---
description: gRPC/RPC — monitoring guidance
type: supplementary
---
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
