---
description: General monitoring and observability questions
requester: any
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

Answer with specific metric names, thresholds, and component names.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Metrics (names, types, labels) | if applicable |
| Health checks (endpoints, thresholds) | if applicable |
| Dashboards (names, what they show) | if applicable |
| Alerts (conditions, severity) | if applicable |
