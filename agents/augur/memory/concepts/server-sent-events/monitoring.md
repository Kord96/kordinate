---
description: Server-Sent Events — monitoring guidance
---
## Monitoring

Track connection lifecycle, event delivery throughput, and per-instance resource usage for SSE streams.

### Key Metrics

- `sse_active_connections` (gauge) — concurrent SSE connections per server instance
- `sse_event_delivery_latency_seconds` (histogram) — time from event generation to client receipt
- `sse_disconnections_total` (counter) — client disconnections partitioned by reason (client-close, timeout, error)
- `sse_reconnections_total` (counter) — reconnection attempts tracked via Last-Event-ID header
- `sse_events_sent_total` (counter) — events pushed to clients, partitioned by event type
- `sse_event_backlog` (gauge) — queued events not yet delivered to consumers

### Alerts

- Active connection count approaching server or file descriptor limits
- Event delivery latency exceeding acceptable threshold for the use case
- High disconnection rate indicating network instability or server resource pressure
- Event backlog growing (server producing faster than clients can consume)
- Server memory or file descriptor usage elevated due to connection accumulation
