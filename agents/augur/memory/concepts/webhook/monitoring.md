---
description: Webhook — monitoring guidance
---
## Monitoring

Track delivery reliability, retry behavior, and per-endpoint health for outbound webhook dispatch.

### Key Metrics

- `webhook_deliveries_total` (counter) — delivery attempts partitioned by endpoint and result (success, client_error, server_error)
- `webhook_delivery_latency_seconds` (histogram) — time from event generation to successful HTTP POST acknowledgment
- `webhook_retry_total` (counter) — retry attempts per endpoint, indicates receiver reliability
- `webhook_dead_letter_queue_depth` (gauge) — permanently failed deliveries awaiting manual review
- `webhook_dispatch_queue_depth` (gauge) — pending events in the dispatch queue, detects backlog from slow consumers
- `webhook_signature_failures_total` (counter) — payload signing or signature verification mismatches

### Alerts

- Sustained retries for a specific endpoint (persistently failing receiver)
- Dead-letter queue depth growing (permanently failed deliveries accumulating)
- Dispatch queue backlog building beyond acceptable threshold
- Delivery latency exceeding SLA for time-sensitive events
- Signature verification mismatch (potential payload tampering or secret rotation issue)
