---
description: Publish-Subscribe — deployment guidance
type: supplementary
---
## Deployment

Coordinate topic configuration and subscriber compatibility during rollouts.

### Rollout Implications

- New message schemas must be backward-compatible -- existing subscribers must handle both old and new formats during rolling deployment
- Adding a new subscriber requires the topic and subscription to exist before the subscriber pod starts consuming
- Removing a subscriber requires draining its pending messages first to avoid silent message loss
- Scaling subscribers horizontally is safe if the broker supports consumer groups; otherwise duplicate delivery occurs

### Pre-deploy Checklist

- Verify topic exists and has the correct partitioning and retention settings for the target environment
- Confirm all subscribers can deserialize the new message format (deploy consumers before producers when adding fields)
- Check subscriber acknowledgment timeout is appropriate for the new processing logic (longer processing needs longer ack deadline)
- Ensure dead-letter topic is configured for all subscriptions to catch processing failures
