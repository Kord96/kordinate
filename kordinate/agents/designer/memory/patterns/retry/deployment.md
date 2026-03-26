---
description: Retry with Backoff — deployment guidance
curated: true
scope: global
preloaded: none
---
## Deployment

Retry configuration changes and DLQ backlog must be managed carefully to avoid retry storms during rollout.

### Rollout Implications

- Lowering max retry counts during rollout causes in-flight retries to DLQ sooner than expected — monitor DLQ depth during transition
- Changing backoff parameters while retries are in progress may cause a burst of simultaneous retries from pods on different configurations
- Rolling restart of consumers with pending retries may lose retry state if it is held in memory — persist retry state externally
- Deploying new retry policies alongside a degraded dependency amplifies load — consider pausing retries until the dependency recovers

### Pre-deploy Checklist

- Verify DLQ consumers are healthy and processing before deploying retry config changes
- Confirm retry state is persisted externally (not in-memory) so rolling restarts do not lose pending retries
- Check that backoff parameters include jitter to prevent thundering herd after fleet-wide restart
