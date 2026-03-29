---
description: Template for project metrics documentation
---
# <Project> — Metrics

> **Maintain this document when metrics are added, removed, or renamed in the codebase.**

## The `app` Label

The `app` Kubernetes label is the universal key. Alloy copies it to every metric and log, making all data queryable by application.

## Infra Metrics (Automatic)

Infra metrics come free from kubelet/cAdvisor for all pods — no instrumentation needed. CPU, memory, network, disk are always available via Alloy.

## App Metrics (Pod-Level)

Pods that expose `/metrics` with `prometheus.io/scrape` annotation. Group by domain:

### <Group Name>

| Metric | Type | Description |
|--------|------|-------------|
| `metric_name` | Counter/Gauge/Histogram | What it measures |

## Vitals Metrics (App-Level)

Health gauges and derived metrics produced by the vitals pod. These are app-level evaluations, not per-pod.

### Health Gauges

| Metric | Check Labels | What it evaluates |
|--------|-------------|-------------------|
| `vitals_process` | `process` | Process liveness |
| `vitals_<section>` | `check` | Section-specific concern |

### Derived Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `metric_name` | Gauge | What it computes from pod-level data |

## Port Assignments

| Component | Port |
|-----------|------|
| vitals | 9131 |
| component-name | ... |

## Dashboards

| Dashboard | Content |
|-----------|---------|
| **Name** | What it shows |

## Label Mapping

Document how k8s labels map to Prometheus and Loki labels for this project's metrics. The `app` label is relabeled by Alloy onto all collected data.
