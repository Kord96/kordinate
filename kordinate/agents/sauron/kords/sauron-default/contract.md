---
description: General monitoring and observability questions
requester: any
mode: stateful
curated: true
scope: global
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

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/sauron/memory/`
