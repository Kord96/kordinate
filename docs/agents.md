# Agents

## Overview

| Agent | Triggers | What it does |
|-------|----------|-------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff` | Rolls deployments between environments, manages infrastructure |
| sauron | `add monitoring`, `health check`, `dashboard`, `run tests`, ... | Adds monitoring, validates code, manages dashboards |
| designer | `review architecture`, `design review` | Reviews architecture, owns design patterns |
| scribe | `update docs`, `add api key`, `add mcp`, ... | Sole editor of `.md` files |

## Shared Rules

All agents inherit these rules (source: `agents/shared/MEMORY.md` + `AGENT.md`).

!!! info "Permissions"
    - Only **deployer** may kubectl write and use Redis MCP
    - Only **sauron** may use Grafana MCP
    - Only **scribe** may edit `.md` files (hook-enforced)
    - Never invoke an agent's operational commands directly — spawn the owning agent

!!! note "Conventions"
    - Credentials live in `pass` under `kordinate/`. Auth locks in `profile/locks/`.
    - Follow existing patterns — no new libraries, frameworks, or conventions
    - Commit with `[<agent-name>]` in message
    - Project artifacts go in the project repo, not kordinate

!!! tip "Memory"
    - Generic knowledge → `memory/static/`
    - Site-specific notes → `memory/dynamic/`
    - Project-specific → `<repo>/.claude/agent-memory/<agent>/`
    - Agent resumption: check `.claude/agent-state/<name>.json` for `agent_id`

## Agent Specifics

=== "Deployer"

    | | |
    |---|---|
    | **Authority** | kubectl writes, container registry, Redis |
    | **Exclusive Tools** | postgres.py, Redis MCP |
    | **Memory Owns** | infra.md, migration.md, troubleshooting.md |
    | **Style** | Reactive — executes on request |

=== "Sauron"

    | | |
    |---|---|
    | **Authority** | Grafana, code fixes, standards testing |
    | **Exclusive Tools** | nokrashi-tools, klog, Grafana MCP |
    | **Memory Owns** | monitoring.md, logging.md, dashboards/ |
    | **Style** | Act first, report after |

=== "Designer"

    | | |
    |---|---|
    | **Authority** | Pattern definitions, architecture review |
    | **Exclusive Tools** | Gemini (design validation) |
    | **Memory Owns** | patterns/\*.md, libraries/\*.md |
    | **Style** | Analytical — validates against patterns |

=== "Scribe"

    | | |
    |---|---|
    | **Authority** | All `.md` file edits |
    | **Exclusive Tools** | Gemini (doc review) |
    | **Memory Owns** | templates/ |
    | **Style** | Coordinate — write-gate for all docs |

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

### Consultation Matrix

| Consulter | Consultant | Provides |
|-----------|-----------|----------|
| deployer | designer | Pattern deployment perspective, architecture constraints for a component |
| deployer | sauron | Monitoring impact of infra changes, metric dependencies to preserve |
| sauron | designer | Pattern monitoring perspective — what to observe for a given pattern |
| sauron | deployer | Live cluster state, pod health, resource usage for monitoring targets |
| designer | deployer | Current infrastructure reality — what's actually deployed, constraints |
| designer | sauron | Observability coverage gaps, metric/dashboard inventory |
| scribe | designer | Architecture context for documentation accuracy |
| scribe | sauron | Monitoring context for documentation accuracy |
| scribe | deployer | Infrastructure context for documentation accuracy |

The matrix is bidirectional — designer can ground architecture reviews in live cluster state from deployer, sauron can discover monitoring targets from deployer, etc.

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
