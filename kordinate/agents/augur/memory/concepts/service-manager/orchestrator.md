---
description: orchestrator library reference
curated: true
scope: global
preloaded: none
---
# orchestrator

Service lifecycle framework for k8s. Scheduling, health checks, retry logic, process management. `pip install k8s-orchestrator`.

## Architecture

Pattern: `scheduler -> runner -> health -> retry`.

| Class | Role |
|-------|------|
| ServiceManager | Lifecycle manager for multiple services |
| Scheduler | Cron-based task scheduling |
| HealthCheck | HTTP/TCP/process health monitoring |
| RetryPolicy | Configurable retry with backoff |
| ProcessRunner | Subprocess management with signal handling |

Review: ServiceManager for multi-process coordination? HealthChecks on all external deps? RetryPolicy with appropriate backoff? Scheduler instead of sleep loops? Graceful shutdown (SIGTERM)?

## Monitoring

Prefix: `orchestrator_`

| Metric | Type | Meaning |
|--------|------|---------|
| orchestrator_services_running | gauge | Active services |
| orchestrator_services_healthy | gauge | Services passing health checks |
| orchestrator_restarts_total | counter | Restart frequency (high = instability) |
| orchestrator_health_check_duration_seconds | histogram | Health check latency (spikes = dependency issues) |
| orchestrator_task_executions_total | counter | Scheduled task runs |

Dashboard patterns: service status matrix, restart rate over time, health check latency (p50/p95), task execution timeline.

## Deployment

ServiceManager handles graceful shutdown — set terminationGracePeriodSeconds. HealthCheck endpoints wired to k8s readiness/liveness probes. Scheduler tasks are in-process (no external cron). RetryPolicy backoff may delay recovery — check restart counts after deploys.

Deploy method: git-branch (trusted publishing via GitHub Actions OIDC).

## Testing

Config file: `config.py`. Use nokrashi-tools TestSuite. Verify all orchestrator_* metrics exposed and scraped.
