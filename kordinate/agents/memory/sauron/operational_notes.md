---
name: operational-notes
description: General infrastructure monitoring facts (not project-specific)
type: user
---

- Grafana unreachable from sandbox — audit dashboards from source JSON files instead
- For project-specific notes, use `/scribe:update-subagent-memory` to write to `.claude/agent-memory/<name>/` instead of native memory
- After editing any dashboard JSON, always auto-deploy it to Grafana immediately — never wait for the user to ask
