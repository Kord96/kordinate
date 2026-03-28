---
description: gRPC/RPC architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [api, integration]
---
# gRPC/RPC

## Recognition

How to identify this pattern in code.

### Signatures

- `.proto` files with `service` and `rpc` declarations
- Generated stub files (`*_pb2.py`, `*_pb2_grpc.py`, `*.pb.go`, `*_grpc.pb.go`)
- Python: `grpcio` library import (`import grpc`)
- Node: `@grpc/grpc-js` library import
- Go: `google.golang.org/grpc` in `go.mod` or import statements
- Java: `io.grpc` package imports (`io.grpc.ManagedChannel`, `io.grpc.ServerBuilder`, `io.grpc.stub`)
- Java: `StreamObserver` interface usage in service implementations
- gRPC server setup with `add_servicer_to_server` or equivalent registration

### Negative signals (not sufficient for detection)

- The word `proto` alone (protocol, prototype, HTTP protocol version) is NOT gRPC. Look for `.proto` files or gRPC library imports.
- `protobuf` used only for serialization without gRPC services (e.g., Protocol Buffers for storage, configuration, or wire format) indicates protobuf usage, not gRPC specifically.
- `net/textproto` in Go is the text protocol package, not gRPC.
- WAF rule files referencing "protocol_violation" or "protocol version" are HTTP protocol analysis, not gRPC.

### Confidence

- **high** -- `.proto` files with service definitions, generated stubs, server/client setup using gRPC libraries
- **medium** -- protobuf message definitions present but service layer uses a different transport (gRPC-Web, Twirp)
- **low** -- binary serialization in use but no `.proto` files or gRPC imports visible

## Architecture

Look for well-defined service contracts in proto files with proper error handling and streaming where appropriate.

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
