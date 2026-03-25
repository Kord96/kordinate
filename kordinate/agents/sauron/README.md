# Sauron

Monitoring, observability, and code validation — ensures projects are observable and correct.

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| [scan](skills/scan/SKILL.md) | `/sauron:scan <project>` | Scan a project for all observability signals — metrics, logs, health checks |
| [diagnose](skills/diagnose/SKILL.md) | `/sauron:diagnose <symptom>` | Debug a production issue using the observability catalog |

## Kords Provided

| Kord | Mode | Requesters | Description |
|------|------|-----------|-------------|
| [sauron-default](../../kords/sauron-default/contract.md) | stateful | any | General monitoring and observability questions — metrics, health checks, dashboards, alerts |
| [monitoring-impact](../../kords/monitoring-impact/contract.md) | stateful | deployer | Monitoring impact assessment for infrastructure changes — gaps, missing dashboards/metrics/alerts |

## Memory

| File | Description |
|------|-------------|
| [monitoring.md](memory/monitoring.md) | Four-layer monitoring model — physical, application, business, alerting |
| [logging.md](memory/logging.md) | Structured logging standards across all projects |
| [tools.md](memory/tools.md) | Tools reference — klog, nokrashi-tools, Grafana MCP |
| [grafana_renderer.md](memory/grafana_renderer.md) | Prioritize Grafana renderer for visual dashboard auditing |
| [workflow.md](memory/workflow.md) | Workflow — understand, implement, validate, report |
| [scratchpad.md](memory/scratchpad.md) | Working notes and observations |

## Rules

- Consult designer for monitoring perspective on recognized patterns
- After editing dashboard JSON, auto-deploy to Grafana immediately
