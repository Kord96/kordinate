---
description: Architecture review for deployment and monitoring changes
requester: deployer, sauron
mode: stateful
curated: true
scope: global
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

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/designer/memory/`
