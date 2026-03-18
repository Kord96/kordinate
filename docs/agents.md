# Agents

## Overview

| Agent | Triggers | What it does |
|-------|----------|-------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff` | Rolls deployments between environments, manages infrastructure |
| sauron | `add monitoring`, `health check`, `dashboard`, `run tests`, ... | Adds monitoring, validates code, manages dashboards |
| designer | `review architecture`, `design review` | Reviews architecture, owns design patterns |
| scribe | `update docs`, `add api key`, `add mcp`, ... | Sole editor of `.md` files |

## How Requests Flow

```
User message
 │
 ├── matches trigger ──► spawn agent
 │   │
 │   │  every tool call passes through hooks:
 │   │
 │   ├── deployer ──► kubectl, docker, redis  (guard-kubectl, guard-git, guard-redis)
 │   ├── sauron ────► grafana MCP             (guard-grafana)
 │   ├── designer ──► read-only analysis
 │   └── scribe ────► .md file edits          (guard-md)
 │
 └── /consult <agent> "question"
     └── agent reads its memory ──► returns answer
```

## Safety Hooks

Hooks fire on every tool call. Registered in `settings.json`.

### Guards

Each guard enforces that only the authorized agent can perform certain operations. Agents authenticate by copying a lock file before operating:

1. Agent copies `profile/locks/<agent>` → `/tmp/.<agent>-auth`
2. Hook reads both files, allows if they match
3. Agent removes `/tmp/.<agent>-auth` after completing work

| Hook | Agent | What it guards |
|------|-------|---------------|
| `guard-kubectl.sh` | deployer | kubectl writes via SSH. Master namespace needs bootstrap auth. Workstation always blocked. |
| `guard-git.sh` | deployer | git push to test/prod branches |
| `guard-redis.sh` | deployer | Redis MCP access |
| `guard-grafana.sh` | sauron | Grafana MCP and dashboard JSON edits |
| `guard-md.sh` | scribe | All `.md` file edits |

### Automation

| Hook | When | What it does |
|------|------|-------------|
| `auto-merge-to-dev.sh` | After git push | Fast-forwards main if a session branch was pushed |
| `agent-memory.sh` | Before agent spawn | Regenerates agent's MEMORY.md if source files changed |

## Consultation

Ask an agent a question without transferring full control:

```
/consult deployer "Is logbd healthy on vandc?"
```

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, versions, networking |

## Commands

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/deployer:roll` | Roll between environments |
| `/deployer:stop` | Scale down an environment |
| `/deployer:clean` | Clean up environment data |
| `/deployer:diff` | Stage incremental data changes |
| `/deployer:bootstrap` | Bootstrap cluster infrastructure |
