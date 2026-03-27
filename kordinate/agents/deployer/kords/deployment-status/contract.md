---
description: Live deployment status — pods, versions, health
requester: any
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Return the current live state of the cluster: running pods, image versions, resource usage, and health. This is always a live query — never return stale data. Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Pod status per namespace | yes |
| Image versions | yes |
| Resource usage (CPU, memory) | if available |
| Unhealthy pods or recent restarts | yes |

## Cache Inputs

None. This kord queries live state and is always considered stale.
