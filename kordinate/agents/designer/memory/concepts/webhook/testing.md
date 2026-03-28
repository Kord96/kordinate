---
description: Webhook — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test payload signing: verify HMAC-SHA256 signature generation and receiver-side verification
- Test retry behavior: simulate 4xx/5xx responses and verify exponential backoff and max retry limits
- Verify idempotency: deliver the same event twice and confirm the receiver deduplicates correctly
- Test dead-letter handling: exhaust retries and verify the event lands in the DLQ for manual review
- Test webhook registration validation: reject invalid or unreachable callback URLs
- Verify that webhook dispatch is asynchronous and does not block the event producer
- Test payload size limits: payloads exceeding the bound are rejected or truncated
- Integration test the full cycle: event occurs, webhook dispatched, receiver processes, acknowledgment returned
