---
description: WebSocket — monitoring guidance
---
## Monitoring

Track connection lifecycle, message throughput, and server resource consumption for WebSocket channels.

### Key Metrics

- `websocket_active_connections` (gauge) — concurrent WebSocket connections per server instance
- `websocket_connections_total` (counter) — connections opened, partitioned by outcome (established, auth_failed, rejected)
- `websocket_disconnections_total` (counter) — disconnections partitioned by reason (client_close, server_close, error, timeout)
- `websocket_heartbeat_failures_total` (counter) — ping/pong heartbeats that failed, indicating silent connection drops
- `websocket_messages_total` (counter) — messages sent and received, partitioned by direction (inbound, outbound)
- `websocket_message_size_bytes` (histogram) — per-message payload size for backpressure detection

### Alerts

- Active connection count approaching server capacity or file descriptor limits
- Heartbeat failure rate elevated (silent connection drops going undetected)
- High connection churn (rapid connect/disconnect cycling indicates client instability)
- Authentication failures during upgrade handshake (potential unauthorized access attempts)
- Message throughput or size anomalies indicating abuse or backpressure issues
