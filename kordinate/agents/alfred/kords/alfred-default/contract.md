---
description: Environment state questions — profile config, pass store, overlays, readiness
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - profile/config.yaml
    - profile/overlays/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Answer questions about profile configuration, credential store state, overlay validity, and deployment readiness. Draw on config.yaml, pass store, and overlay state.

### Response Format

| Field | Required |
|-------|----------|
| status | yes (valid/invalid/stale/missing) |
| detail | yes |
| recommendation | if action needed |
| affected_files | if applicable |
