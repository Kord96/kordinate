---
description: General architecture and design questions
requester: any
provider: designer
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Answer concisely — the caller needs facts, not explanations.
Include specific file paths when referencing components.
Keep under 50 lines.

### Response Format

Designer identifies patterns across 20 categories and detects anti-patterns from a 218-entry catalog (157 patterns + 61 anti-patterns).

| Field | Required |
|-------|----------|
| Component topology | if applicable |
| Design patterns in use | if applicable |
| Anti-patterns detected | if applicable |
| Data flow | if applicable |
| Failure modes | if applicable |

## Provider State Invalidation

Invalidate when:
- Architecture documentation is updated
- Pattern library changes
- Project structure changes
