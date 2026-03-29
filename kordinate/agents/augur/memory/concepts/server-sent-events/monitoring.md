---
description: Server-Sent Events — monitoring guidance
type: supplementary
---
# Monitoring

- Track concurrent SSE connection count per server instance and alert when approaching limits
- Monitor event delivery latency from generation to client receipt
- Alert on connection drop rates — high disconnection frequency indicates network or server issues
- Track reconnection attempts via `Last-Event-ID` to measure resume reliability
- Monitor server memory and file descriptor usage — each SSE connection holds an open connection
- Dashboard showing active connections, events/second, and client distribution across instances
- Alert when event backlog grows (server generating faster than clients can consume)
