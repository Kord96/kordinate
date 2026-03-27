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

## Provider State Invalidation

Invalidate when:
- profile/config.yaml is modified
- Pass store entries are added, removed, or rotated
- Kustomize overlays are regenerated
- New clusters are added to config
