---
description: General architecture and design questions
requester: any
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Answer concisely — the caller needs facts, not explanations.
Include specific file paths when referencing components.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Component topology | if applicable |
| Design patterns in use | if applicable |
| Data flow | if applicable |
| Failure modes | if applicable |

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/designer/memory/`
