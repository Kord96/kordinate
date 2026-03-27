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

## Provider State Invalidation

Invalidate when:
- Dashboard definitions are modified
- Alert rules are updated
- Monitoring stack configuration changes
