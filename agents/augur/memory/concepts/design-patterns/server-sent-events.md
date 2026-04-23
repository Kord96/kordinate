---
kind: concept
name: server-sent-events
signatures: {}
type: pattern
abstraction:
- infrastructure
- integration
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `Content-Type: text/event-stream` response header
- `EventSource` constructor on the client side
- Lines prefixed with `data:`, `event:`, `id:`, or `retry:` in the response stream
- HTTP streaming response with `Transfer-Encoding: chunked` or `Connection: keep-alive`
- `@SseEmitter` or `SseEmitter` in Spring, `StreamingResponse` in FastAPI/Starlette
- `res.write()` in a long-lived Node HTTP response with `text/event-stream`
- `Last-Event-ID` header for resuming missed events
- `onmessage`, `onopen`, `onerror` event listeners on `EventSource`

### Confidence

- **high** -- `text/event-stream` content type with `data:` prefixed lines and `EventSource` client
- **medium** -- HTTP streaming response with event-like formatting but no explicit `EventSource` usage
- **low** -- Long-lived HTTP response that pushes data without standard SSE framing

## Architecture

Look for correct one-way server push with proper event framing and automatic reconnection.

### Review Checklist

- Response uses `text/event-stream` content type and follows the SSE wire format
- Events include `id:` fields so clients can resume via `Last-Event-ID` after reconnection
- `retry:` field is set to a reasonable reconnection interval
- Server handles client disconnection gracefully (detects closed connection, cleans up resources)
- Named event types (`event:` field) are used to multiplex different message kinds on one stream
- Connection count is bounded -- server tracks and limits concurrent SSE clients

### Anti-patterns

- Missing `id:` fields making resume-after-disconnect impossible
- Buffering the entire response instead of streaming (defeats the purpose of SSE)
- Using SSE for bidirectional communication instead of switching to WebSocket
- No connection cleanup when clients disconnect silently

### Relationship To Other Concepts

- Related to [websocket](/concepts/websocket) as another real-time delivery transport, though SSE is one-way server-to-client over HTTP.
- Related to [long-polling](/concepts/long-polling) because SSE is often adopted as a cleaner streaming alternative to repeated poll cycles.
- Related to [event-driven](/concepts/event-driven) when server-side events are streamed directly to browsers or clients.

### Boundary

Use `server-sent-events` when the server streams a one-way sequence of events to clients over an HTTP connection using SSE semantics.

Do not use it for any streaming response. The key signal is SSE event framing and client reconnection behavior.
