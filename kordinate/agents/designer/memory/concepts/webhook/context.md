# Testing

- Test payload signing: verify HMAC-SHA256 signature generation and receiver-side verification
- Test retry behavior: simulate 4xx/5xx responses and verify exponential backoff and max retry limits
- Verify idempotency: deliver the same event twice and confirm the receiver deduplicates correctly
- Test dead-letter handling: exhaust retries and verify the event lands in the DLQ for manual review
- Test webhook registration validation: reject invalid or unreachable callback URLs
- Verify that webhook dispatch is asynchronous and does not block the event producer
- Test payload size limits: payloads exceeding the bound are rejected or truncated
- Integration test the full cycle: event occurs, webhook dispatched, receiver processes, acknowledgment returned

# Monitoring

- Track delivery success/failure rates per registered webhook endpoint
- Alert on rising retry counts — sustained retries indicate a persistently failing receiver
- Monitor delivery latency from event generation to successful HTTP POST acknowledgment
- Track dead-letter queue depth — growing DLQ indicates permanently failing deliveries
- Alert on payload signing failures or signature verification mismatches
- Dashboard showing active webhook registrations, delivery rates, and per-endpoint health
- Monitor webhook dispatch queue depth to detect backlog from slow consumers or high event volume

# Deployment

- Deploy webhook payload format changes with backward compatibility — add fields, do not rename or remove
- Rotate signing secrets with a dual-validation window: accept both old and new secrets during transition
- Deploy dispatch queue workers with enough capacity to handle the registered webhook volume
- Verify webhook endpoint validation (URL reachability or ownership proof) after any registration changes
- Test delivery retry behavior in staging before deploying retry policy changes to production
- Coordinate webhook deprecation with consumers: announce timeline, monitor old endpoint usage, then remove
- Ensure dead-letter handling is deployed and tested before increasing webhook volume

