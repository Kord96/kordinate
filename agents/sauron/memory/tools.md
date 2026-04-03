---
description: Sauron tools reference
---
# Tools

| Tool | Type | Purpose |
|------|------|---------|
| Grafana MCP | MCP server | Dashboard queries and management (requires auth) |
| Prometheus | query endpoint | Query metrics — master at prometheus.master.svc.cluster.local:9191 |
| Loki | query endpoint | Query logs — master at loki.master.svc.cluster.local:3100 |
| Atlas (augur) | project memory | Read project atlas for failure_modes.detection and component topology |
| Infra-atlas | global memory | Cluster config, observability endpoints, workload contract |
| Gemini CLI | CLI | Validate complex monitoring decisions |
