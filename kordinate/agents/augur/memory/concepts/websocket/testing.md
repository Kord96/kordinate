---
description: WebSocket — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test the full connection lifecycle: open, send/receive messages, error handling, and graceful close
- Verify ping/pong heartbeat keeps connections alive and detects silent drops
- Test client reconnection with exponential backoff after server disconnection
- Test authentication during the upgrade handshake — unauthenticated upgrades must be rejected
- Load test with many concurrent connections to verify server connection limits and backpressure
- Test message serialization format (JSON, protobuf) with schema validation on both sides
- Verify that the server detects and cleans up abandoned connections (no heartbeat response)
- Test rate limiting: clients sending messages faster than the server can process are throttled
