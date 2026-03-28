# Testing

- Test the full connection lifecycle: open, send/receive messages, error handling, and graceful close
- Verify ping/pong heartbeat keeps connections alive and detects silent drops
- Test client reconnection with exponential backoff after server disconnection
- Test authentication during the upgrade handshake — unauthenticated upgrades must be rejected
- Load test with many concurrent connections to verify server connection limits and backpressure
- Test message serialization format (JSON, protobuf) with schema validation on both sides
- Verify that the server detects and cleans up abandoned connections (no heartbeat response)
- Test rate limiting: clients sending messages faster than the server can process are throttled

# Monitoring

- Track concurrent WebSocket connection count per server and alert when approaching capacity limits
- Monitor ping/pong heartbeat success rates — failures indicate silent connection drops
- Alert on connection churn: high connect/disconnect frequency may indicate client-side instability
- Track message throughput (messages/sec) and sizes per connection for backpressure detection
- Monitor server memory and file descriptor usage — each WebSocket holds an open connection and buffer
- Dashboard showing active connections, reconnection rates, and message latency distribution
- Alert on authentication failures during the upgrade handshake

# Deployment

- Deploy with connection draining: allow existing WebSocket connections to close gracefully before terminating pods
- Verify load balancer configuration supports WebSocket upgrade headers and sticky sessions if needed
- Deploy message format changes with backward compatibility — clients may be on older versions
- Test reconnection behavior during rolling deployments to ensure clients reconnect seamlessly
- Configure server connection limits and backpressure before scaling up client-facing capacity
- Verify authentication during the upgrade handshake works correctly after auth infrastructure changes
- Monitor connection counts during deployment to verify clients reconnect to new instances

