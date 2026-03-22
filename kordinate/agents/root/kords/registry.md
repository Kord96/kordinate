# Agent Registry

All agents in the kordinate system.

| Agent | Purpose | Triggers |
|-------|---------|----------|
| deployer | GitOps deployments across environments | "roll", "migrate", "stop", "clean", "diff" |
| designer | Architecture review + pattern authority | "review architecture", "design review" |
| sauron | Monitoring & validation | "add monitoring", "add metrics", "health check", "dashboard", "run tests" |
| scribe | Documentation (sole .md editor) | "update docs", "add api key", "add mcp", "write readme" |

## Kords

| Kord | Requester | Provider | Purpose |
|------|-----------|----------|---------|
| `pattern-review` | deployer, sauron | designer | Architecture review for deployment/monitoring changes |
| `monitoring-impact` | deployer | sauron | Monitoring impact assessment for infrastructure changes |
| `deployer-default` | any | deployer | General deployment/cluster questions |
| `designer-default` | any | designer | General architecture/design questions |
| `sauron-default` | any | sauron | General monitoring/observability questions |
| `scribe-default` | any | scribe | General documentation/template questions |
