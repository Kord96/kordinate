---
description: Template for project vitals documentation
---
# <Project> — Vitals

> **Maintain this document when health checks are added or modified.**

## Architecture

One vitals pod per app per namespace. Vitals queries Prometheus and Loki to evaluate health, producing gauges and derived metrics. Alloy scrapes vitals like any other pod.

Describe how health checks compose: per-process flags -> section flags -> composite status.
Include the section tree diagram.

## Status Values

Document the tri-state gauge and any project-specific status metrics.

| Value | Meaning | Condition |
|-------|---------|-----------|
| 0 | FAIL | ... |
| 1 | WARNING | ... |
| 2 | OK | ... |

## Deployment

Vitals port: 9131. Required env vars: `PROMETHEUS_URL`, `LOKI_URL`.

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9131"
labels:
  app: <app-name>
  component: vitals
```

## Loki Label Schema

Document how to address components in Loki queries for this project. The `app` label is the universal key across all data.

## Start Here

The first query to run when debugging — typically the vitals's own transition logs.

## Sections

For each health check section, combine thresholds and debug info:

### <Section Name>

**Thresholds**

| Check | OK | WARN | FAIL |
|-------|----|------|------|

**Debug**

| Check | Triggers | Loki Query | Key Events |
|-------|----------|------------|------------|

Notes on logging gaps or special behavior for this section.

## Process-Level (Cross-Cutting)

Generic debugging patterns that apply across all components (FAIL, STUCK, crash loops).

## Logging Gaps

Document what CANNOT be diagnosed via logs alone and requires Prometheus or kubectl.
