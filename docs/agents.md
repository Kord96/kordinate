# Agents

## Overview

| Agent | Triggers | What it does |
|-------|----------|-------------|
| deployer | `roll`, `roll forward`, `roll backward`, `publish`, `migrate` | Rolls deployments between environments, manages infrastructure |
| sauron | `add monitoring`, `add metrics`, `health check`, `prometheus`, `dashboard`, `set up logging`, `add logging`, `review logs`, `run tests`, `code validation`, `validate code` | Adds monitoring, validates code, manages dashboards |
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

## Commands

=== "General"

    | Command | Description |
    |---------|-------------|
    | `/boot` | Initialize the workstation environment |
    | `/consult` | Query an agent without full handoff |
    | `/merge` | Merge current session branch |
    | `/invalidate` | Force re-consultation for an agent |

=== "Deployer"

    | Command | Description |
    |---------|-------------|
    | `/deployer:roll` | Roll between environments |
    | `/deployer:stop` | Scale down an environment |
    | `/deployer:clean` | Clean up environment data |
    | `/deployer:diff` | Stage incremental data changes |
    | `/deployer:bootstrap` | Bootstrap cluster infrastructure |
