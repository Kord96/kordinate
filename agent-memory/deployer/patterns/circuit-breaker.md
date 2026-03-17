# Circuit Breaker — Deployment Perspective

Consider dependency health and connection draining during rollouts.

## Rollout Implications

- Drain existing connections before terminating pods — open circuits may not recover if pod dies mid-request
- Health gate: do not mark new pods as ready until circuit breakers for critical dependencies are in closed state
- Rolling restart may temporarily spike circuit opens — expected, but monitor for cascading failures
- If a dependency is already degraded, pause rollout to avoid all pods opening circuits simultaneously

## Pre-deploy Checklist

- Verify circuit breaker recovery timeouts are shorter than readiness probe intervals
- Check that pod terminationGracePeriodSeconds allows in-flight requests to complete
