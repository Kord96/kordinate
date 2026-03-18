# orchestrator

## Designer Perspective

Service lifecycle framework for k8s. Scheduling, health checks, retry logic, and process management.

## Pattern

`scheduler -> runner -> health -> retry`

Manages how services run, start, stop, and recover.

## Key Classes

| Class | Role |
|-------|------|
| ServiceManager | Lifecycle manager for multiple services |
| Scheduler | Cron-based task scheduling |
| HealthCheck | HTTP/TCP/process health monitoring |
| RetryPolicy | Configurable retry with backoff |
| ProcessRunner | Subprocess management with signal handling |

## When to Use

- Managing long-running services with health checks
- Scheduling periodic tasks (cron-like)
- Process supervision with restart policies
- Services that need graceful shutdown and retry logic

## Architecture Review Checklist

- Is ServiceManager used for multi-process coordination (not bare subprocess)?
- Are HealthChecks wired to all external dependencies?
- Is RetryPolicy configured with appropriate backoff for each failure mode?
- Is Scheduler used for periodic tasks instead of sleep loops?
- Is graceful shutdown handled (SIGTERM propagation)?

## Install

```
pip install k8s-orchestrator
```

## Deployer Perspective

Service lifecycle framework for k8s. Used by batch job and managed service components.

## Install

```
pip install k8s-orchestrator
```

PyPI: `k8s-orchestrator`. Deploy method: `git-branch` (trusted publishing via GitHub Actions OIDC).

## Components

Projects using orchestrator typically have a ServiceManager coordinating multiple services (workers, schedulers, health checkers).

## Deployment Notes

- ServiceManager handles graceful shutdown — pods need appropriate terminationGracePeriodSeconds
- HealthCheck endpoints should be wired to k8s readiness/liveness probes
- Scheduler tasks are in-process — no external cron needed
- RetryPolicy backoff may delay service recovery — check restart counts after deploys

## Sauron Perspective

Service lifecycle framework. Key monitoring surface for managed services and batch jobs.

## Metrics

Prefix: `orchestrator_`

| Metric | Type | What it tells you |
|--------|------|-------------------|
| orchestrator_services_running | gauge | How many services are active |
| orchestrator_services_healthy | gauge | How many pass health checks |
| orchestrator_restarts_total | counter | Restart frequency — high means instability |
| orchestrator_health_check_duration_seconds | histogram | Health check latency — spikes indicate dependency issues |
| orchestrator_task_executions_total | counter | Scheduled task runs — compare to expected frequency |

## Health Checks

- Service status: running vs crashed vs restarting
- Health check pass rate: healthy / total services
- Restart rate: frequent restarts indicate crash loops
- Task execution: are scheduled tasks running on time?

## Dashboard Patterns

- Service status matrix (running/healthy/restarting per component)
- Restart rate over time
- Health check latency (p50, p95)
- Task execution timeline (expected vs actual)

## Testing

Config file: `config.py`. Use nokrashi-tools TestSuite. No tests to skip.

Verify all orchestrator_ metrics are exposed and scraped by Alloy.

