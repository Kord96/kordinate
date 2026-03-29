---
description: WebSocket — monitoring guidance
type: supplementary
---
# Monitoring

- Track concurrent WebSocket connection count per server and alert when approaching capacity limits
- Monitor ping/pong heartbeat success rates — failures indicate silent connection drops
- Alert on connection churn: high connect/disconnect frequency may indicate client-side instability
- Track message throughput (messages/sec) and sizes per connection for backpressure detection
- Monitor server memory and file descriptor usage — each WebSocket holds an open connection and buffer
- Dashboard showing active connections, reconnection rates, and message latency distribution
- Alert on authentication failures during the upgrade handshake
