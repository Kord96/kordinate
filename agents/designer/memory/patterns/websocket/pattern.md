---
description: WebSocket architectural pattern
type: pattern
testable: true
observable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
---
# WebSocket

## Recognition

How to identify this pattern in code.

### Signatures

- `ws://` or `wss://` URL schemes in connection strings or config
- `on_message`, `on_connect`, `on_close`, `on_error` handler callbacks
- HTTP `Upgrade: websocket` and `Connection: Upgrade` headers
- Ping/pong frame handling for keepalive
- Import of `websockets` (Python), `ws` or `socket.io` (Node), `gorilla/websocket` (Go)
- Spring `@MessageMapping` or `@EnableWebSocket` annotations
- `WebSocketHandler`, `WebSocketServer`, `WebSocketClient` class names
- `STOMP` or `SockJS` fallback configuration

### Confidence

- **high** -- `ws://`/`wss://` URLs combined with message handler callbacks and upgrade headers
- **medium** -- WebSocket library imports with handler registration but no visible connection lifecycle
- **low** -- Generic bidirectional messaging code without explicit WebSocket protocol references

## Architecture

Look for correct connection lifecycle management and message framing over persistent bidirectional channels.

### Review Checklist

- Connection lifecycle is complete: open, message, error, close handlers all defined
- Ping/pong or application-level heartbeat prevents silent connection drops
- Reconnection logic with backoff exists on the client side
- Message serialization format is consistent (JSON, protobuf) with schema validation
- Connection limits and backpressure are enforced on the server
- Authentication happens during the upgrade handshake, not after

### Anti-patterns

- No reconnection strategy -- single disconnect permanently kills the session
- Sending unbounded messages without flow control or rate limiting
- Performing authentication only via query params in the `ws://` URL (leaks credentials in logs)
- Using WebSocket where SSE or simple polling would suffice (over-engineering)
