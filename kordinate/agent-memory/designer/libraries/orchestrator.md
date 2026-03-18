# orchestrator — Design Perspective

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
