---
description: Available dashboards, metrics, and alert rules
requester: any
mode: stateful
curated: true
scope: global
cache_inputs:
  paths:
    - kordinate/agents/sauron/memory/
    - kordinate/agents/charon/skills/infra/manifests/
    - kordinate/agents/charon/skills/infra/dashboards/
  threshold: 0.05
  stale_threshold: 0.25
  max_age: 5d
---

## Provider Guidelines

Return the catalog of configured dashboards, scraped metrics, and active alert rules. Draw from sauron memory and charon infra manifests. Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Dashboard names and purpose | yes |
| Metric names and types | yes |
| Alert rules and conditions | yes |
| Scrape targets | if applicable |
