---
kind: concept
name: long-polling
signatures: {}
type: pattern
abstraction:
- integration
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Client sends HTTP request, server holds it open until data is available or timeout expires
- Immediate re-request loop after receiving a response or timeout
- `timeout` parameter on server-side request handling (30s, 60s typical)
- Polling loop with configurable delay or immediate retry
- `setTimeout` or `setInterval` wrapping fetch/XHR calls on the client
- Fallback logic from WebSocket or SSE to long polling
- `ETag` or `If-None-Match` headers for change detection
- `304 Not Modified` responses when no new data is available

### Confidence

- **high** -- Server explicitly holds requests with a timeout, client immediately re-requests on completion
- **medium** -- Polling loop with a delay that adjusts based on server response
- **low** -- Periodic HTTP requests without explicit hold-and-wait semantics (may be simple polling)

## Architecture

Look for correct request lifecycle with timeout handling and efficient re-request logic.

### Review Checklist

- Server-side timeout is configured and does not hold connections indefinitely
- Client re-requests immediately after receiving data or a timeout response
- Error handling includes backoff to avoid hammering the server on failures
- Server can detect and clean up abandoned long-poll connections
- Response includes a version token or cursor so the client requests only new data

### Anti-patterns

- No timeout on the server side -- connections held open forever if no data arrives
- Fixed-interval polling disguised as long polling (missing the hold-until-data-available behavior)
- No backoff on errors -- client floods server with retries during outages
- Using long polling when WebSocket or SSE is available and supported by the client

### Relationship To Other Concepts

- Related to [server-sent-events](/concepts/server-sent-events) and [websocket](/concepts/websocket) as alternative realtime delivery mechanisms.
- Related to [polling-flow](/concepts/polling-flow) because long polling is a more efficient variant of poll-based interaction.

### Boundary

Use `long-polling` when clients hold a request open until data is available or a timeout occurs, then immediately reissue the request.

Do not use it for ordinary short-interval polling. The key signal is open-held request semantics.
