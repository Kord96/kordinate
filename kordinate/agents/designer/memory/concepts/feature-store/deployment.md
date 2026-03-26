---
description: Feature Store — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Coordinate feature pipeline, store, and serving layer deployments to avoid serving stale or incompatible features.

### Rollout Implications

- Deploy feature transformation pipeline updates before model updates that depend on new features — the store must contain the features before the model requests them
- Backfill new features before switching models to use them — missing feature values cause null defaults or inference errors
- Rolling updates to the serving layer may briefly increase latency during cache warming — monitor serving latency during rollout
- If changing feature schemas (new columns, type changes), update offline and online stores in lockstep

### Pre-deploy Checklist

- Verify feature freshness is within SLA for all feature groups the target model depends on
- Confirm online store connectivity and latency from the model serving environment
