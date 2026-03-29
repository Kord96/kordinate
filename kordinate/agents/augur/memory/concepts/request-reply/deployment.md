---
description: Request-Reply — deployment guidance
type: supplementary
---
## Deployment

Coordinate requester and responder lifecycle to avoid lost replies during rollouts.

### Rollout Implications

- Rolling restart of the requester may orphan reply queues on the broker -- ensure temporary queues have auto-delete or TTL
- Deploying the responder first is safer: new responder can handle both old and new request formats
- If requester and responder are co-deployed, stagger restarts to avoid both sides being unavailable simultaneously
- Timeout values must account for deployment-induced latency (briefly increased round-trip during pod replacement)

### Pre-deploy Checklist

- Verify the broker is healthy and reply queues are being created and cleaned up correctly
- Confirm correlation ID generation produces unique values (no collisions across requester instances)
- Check that timeout values on the requester side are appropriate for the responder's expected processing time
- Ensure temporary reply queues have TTL or auto-delete configured to prevent resource leaks on the broker
