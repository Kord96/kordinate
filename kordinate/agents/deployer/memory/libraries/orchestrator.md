# orchestrator — Deployment Perspective

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
