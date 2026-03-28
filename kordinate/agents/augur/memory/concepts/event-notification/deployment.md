---
description: Event Notification — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate notification infrastructure so consumers can fetch full state from the source when notified.

### Rollout Implications

- Deploy the source API changes before the notification schema changes — consumers call back to the source for full data, so the API must serve the new shape first
- Thin events carry minimal payload, so schema changes are less risky than fat events, but routing and type identifiers must remain stable
- Rolling consumer updates may cause brief windows where some consumers fetch old API versions — ensure the source API supports both
- If changing the notification channel (topic rename, new routing key), deploy consumers listening on both old and new channels during transition

### Pre-deploy Checklist

- Verify the source API is healthy and can handle the callback load that notifications will trigger
- Confirm notification topic/exchange exists with correct routing in the target environment
