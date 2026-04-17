---
description: gRPC/RPC architectural pattern
type: pattern
testable: true
observable: true
distributed: true
graphable: true
abstraction:
- api
- integration
status: primary
scope: backend
relationships:
  related_to:
  - server-route-registration
  - rest
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: rich
examples: []
---
# gRPC/RPC

## Recognition

How to identify this pattern in code.

### Signatures

- `.proto` files with `service` and `rpc` declarations
- Protobuf `message` definitions for request/response types
- Generated stub files (`*_pb2.py`, `*_pb2_grpc.py`, `*.pb.go`, `*_grpc.pb.go`)
- Bidirectional streaming: `stream` keyword in `.proto` rpc definitions
- Libraries: `grpcio` (Python), `@grpc/grpc-js` (Node), `tonic` (Rust), `google.golang.org/grpc` (Go)
- Channel creation and stub instantiation in client code
- gRPC server setup with `add_servicer_to_server` or equivalent registration

### Confidence

- **high** -- `.proto` files with service definitions, generated stubs, server/client setup using gRPC libraries
- **medium** -- protobuf message definitions present but service layer uses a different transport (gRPC-Web, Twirp)
- **low** -- binary serialization in use but no `.proto` files or gRPC imports visible

## Architecture

Look for well-defined service contracts in proto files with proper error handling and streaming where appropriate.

### Relationship To Other Concepts

- `grpc` is the contract-and-transport concept for protobuf-defined RPC services.
- Use `server-route-registration` for exposure mechanics generally; use `grpc` when the service contract style itself matters.
- Prefer `rest` when the public surface is resource-oriented HTTP rather than procedure-oriented RPC.

### Review Checklist

- Proto files are versioned and backward-compatible (no renumbering or removing fields, use `reserved`)
- Deadlines/timeouts are set on all RPC calls (no unbounded waits)
- Error handling uses gRPC status codes correctly (not just `UNKNOWN` or `INTERNAL` for everything)
- Streaming RPCs have proper flow control and cancellation handling
- Proto files live in a shared location or are distributed via a proto registry
- Health checking service is implemented (`grpc.health.v1.Health`)

### Anti-patterns

- Breaking proto compatibility by renumbering or removing fields without `reserved`
- No deadlines on RPC calls (risk of hanging connections consuming resources)
- Sending large payloads over gRPC without chunking or streaming (default 4MB message limit)
- Generating client stubs in the same repo as the server instead of distributing proto files

### Boundary

Do not use `grpc` for every protobuf payload or internal client library. Prefer it only when protobuf-defined RPC service contracts shape inter-service communication.

### Relationship To Other Concepts

- Related to [server-route-registration](/concepts/server-route-registration) because gRPC services still expose a server-side contract, even if the registration style differs from HTTP routing.
- Related to [rest](/concepts/rest) as another API style for service-to-service or client-to-service communication with different transport and contract semantics.
