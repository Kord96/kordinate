---
description: Look up a specific architectural pattern or anti-pattern
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/designer/memory/concepts/
    - kordinate/agents/designer/memory/anti-patterns/
  threshold: 0.03
  stale_threshold: 0.20
  max_age: 14d
---

## Provider Guidelines

Return the definition, detection rules, and common violations for the requested pattern or anti-pattern. Draw from the patterns and anti-patterns directories. Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Pattern name and category | yes |
| Summary | yes |
| Detection rules or signals | yes |
| Common violations | if anti-pattern or applicable |
| Related patterns | if applicable |
