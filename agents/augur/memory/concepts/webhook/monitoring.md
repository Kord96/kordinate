---
description: Webhook — monitoring guidance
type: supplementary
---
# Monitoring

- Track delivery success/failure rates per registered webhook endpoint
- Alert on rising retry counts — sustained retries indicate a persistently failing receiver
- Monitor delivery latency from event generation to successful HTTP POST acknowledgment
- Track dead-letter queue depth — growing DLQ indicates permanently failing deliveries
- Alert on payload signing failures or signature verification mismatches
- Dashboard showing active webhook registrations, delivery rates, and per-endpoint health
- Monitor webhook dispatch queue depth to detect backlog from slow consumers or high event volume
