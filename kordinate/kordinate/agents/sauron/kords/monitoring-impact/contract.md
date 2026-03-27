---
description: Monitoring impact assessment for infrastructure changes
requester: deployer
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/sauron/memory/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Assess monitoring coverage for the affected service.
Report gaps, not what's already working.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Gaps by severity (blocking, warning, info) | yes |
| Missing dashboards or metrics | yes |
| Missing alerts | yes |
| Summary | no |
