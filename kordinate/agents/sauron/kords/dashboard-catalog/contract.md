---
description: Available dashboards, metrics, and alert rules
requester: any
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Return the catalog of configured dashboards, scraped metrics, and active alert rules. Draw from sauron memory and deployer infra manifests. Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Dashboard names and purpose | yes |
| Metric names and types | yes |
| Alert rules and conditions | yes |
| Scrape targets | if applicable |

## Cache Inputs

Hash these paths to detect staleness:
- `$KORDINATE_HOME/kordinate/agents/sauron/memory/`
- `$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/manifests/`
- `$KORDINATE_HOME/kordinate/agents/deployer/skills/infra/dashboards/`
