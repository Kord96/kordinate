---
description: <Project> — Metrics
curated: true
scope: global
---
# <Project> — Metrics

> **Maintain this document when metrics are added, removed, or renamed in the codebase.**

## Metrics

Group metrics by tier or domain. Each group gets a table:

### <Group Name>

| Metric | Type | Description |
|--------|------|-------------|
| `metric_name` | Counter/Gauge/Histogram | What it measures |

## Port Assignments

| Component | Port |
|-----------|------|
| component-name | 9100 |

## Dashboards

| Dashboard | Content |
|-----------|---------|
| **Name** | What it shows |

## Label Mapping

Document how k8s labels map to Prometheus and Loki labels for this project's metrics. Include any relabel quirks (e.g., federation renaming).
