---
description: General documentation and template questions
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/scribe/memory/
  threshold: 0.05
  stale_threshold: 0.30
  max_age: 7d
---

## Provider Guidelines

Return full template content as a structure guide.
If no template exists, say so.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Template content | yes |
| Usage notes | if applicable |
