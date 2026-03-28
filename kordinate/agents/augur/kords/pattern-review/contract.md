---
description: Architecture review for deployment and monitoring changes
requester: charon, sauron
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/augur/memory/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Review the proposed change against established patterns.
Include specific file paths and what should change.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Violations by severity (blocking, warning, info) | yes |
| Affected files + suggested changes | yes |
| Summary | no |
