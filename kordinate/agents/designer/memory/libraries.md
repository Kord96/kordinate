---
description: Index of shared libraries that implement patterns across projects
curated: true
scope: global
---
# Shared Libraries Index

Libraries that implement patterns or provide shared tooling across projects.

## Owned

| Library | Repo | Pattern | Description |
|---------|------|---------|-------------|
| stoik | [Kord96/stoik](https://github.com/Kord96/stoik) | stream-to-store | StoicConsumer, StoicBuffer, StoicProducer for Kafka-to-DuckDB pipelines. |
| orchestrator | [Kord96/orchestrator](https://github.com/Kord96/orchestrator) | service manager | ServiceManager, HealthCheck, RetryPolicy for process lifecycle. |
| klog | [Kord96/klog](https://github.com/Kord96/klog) | — | Structured logging with structlog. JSON (prod) / console (dev). stdlib bridge. |
| nokrashi-tools | [Kord96/nokrashi-tools](https://github.com/Kord96/nokrashi-tools) | — | Code validation, standards testing, metric coverage analysis. |

## Third-party

| Library | Install | Pattern | Description |
|---------|---------|---------|-------------|
| tenacity | `pip install tenacity` | retry with backoff | Configurable retries with exponential backoff, jitter, and stop conditions. |
| pybreaker | `pip install pybreaker` | circuit breaker | Circuit breaker implementation with configurable thresholds and listeners. |
