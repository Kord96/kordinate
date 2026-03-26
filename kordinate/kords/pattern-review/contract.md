---
description: Architecture review for deployment and monitoring changes
requester: deployer, sauron
provider: designer
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Review the proposed change against established patterns and anti-patterns.
Designer uses a 218-entry catalog (157 patterns + 61 anti-patterns across 20 categories).
Include specific file paths and what should change.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Violations by severity (blocking, warning, info) | yes |
| Anti-pattern findings | if applicable |
| Affected files + suggested changes | yes |
| Summary | no |

## Provider State Invalidation

Invalidate when:
- Pattern library is updated
- Architecture documentation changes
- New patterns are added
