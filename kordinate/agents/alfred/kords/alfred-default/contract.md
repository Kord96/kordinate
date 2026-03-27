---
description: Environment state questions — profile config, pass store, overlays, readiness
requester: any
mode: stateful
curated: true
scope: global
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

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/profile/config.yaml`
- `$KORDINATE_HOME/profile/overlays/`
