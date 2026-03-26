---
description: Server-Sent Events — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test the SSE wire format: verify `data:`, `event:`, `id:`, and `retry:` fields are correctly formatted
- Simulate client disconnection and verify the server detects it and cleans up resources
- Test resume after reconnection by sending `Last-Event-ID` and verifying missed events are replayed
- Load test with many concurrent SSE clients to verify connection limits and backpressure behavior
- Test named event types by subscribing to specific `event:` values and ignoring others
- Verify that the `Content-Type: text/event-stream` header is set on the response
- Test that the server streams incrementally, not buffering the entire response before sending
- Assert connection cleanup under error conditions (server crash, network timeout)
