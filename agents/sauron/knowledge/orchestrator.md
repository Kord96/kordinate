# orchestrator — Monitoring Perspective

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
