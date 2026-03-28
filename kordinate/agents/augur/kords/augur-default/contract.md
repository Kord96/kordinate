---
description: General architecture and design questions
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/designer/memory/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
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
