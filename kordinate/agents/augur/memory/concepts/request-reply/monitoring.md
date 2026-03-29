---
description: Request-Reply — monitoring guidance
type: supplementary
---
## Monitoring

Track correlation success rates, reply latencies, and timeout frequency to detect broken request-reply flows.

### Key Metrics

- `request_reply_sent_total` (counter) -- request messages sent, by destination
- `request_reply_received_total` (counter) -- reply messages received with matching correlation ID
- `request_reply_timeout_total` (counter) -- requests that timed out waiting for a reply
- `request_reply_latency_seconds` (histogram) -- round-trip time from request send to reply receipt
- `reply_queue_depth` (gauge) -- number of pending replies on temporary reply queues

### Alerts

- Timeout rate exceeds threshold (responder down, network issue, or reply queue misconfigured)
- Reply latency exceeds SLA for a sustained period (responder degraded or overloaded)
- Orphaned reply queues accumulating (queues not cleaned up after timeout or response)
- Correlation ID mismatch rate nonzero (reply routing broken, possible message interleaving)
