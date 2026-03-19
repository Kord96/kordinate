# Agents

## Overview

| Agent | What it does |
|-------|-------------|
| **deployer** | Rolls deployments between environments, manages infrastructure |
| **sauron** | Adds monitoring, validates code, manages dashboards |
| **designer** | Reviews architecture, owns design patterns |
| **scribe** | Sole editor of `.md` files |

## Shared

All agents inherit these rules (source: `agents/shared/MEMORY.md` + `AGENT.md`).

### Rules

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
    `static/` (pre-defined structure) + `dynamic/` (free-form) — same model at [global and project scope](memory.md#memory-model). Agent resumption: check `.claude/agent-state/<name>.json` for `agent_id`.

### Commands

| Command | Description |
|---------|-------------|
| `/boot` | Initialize the workstation environment |
| `/consult` | Query an agent without full handoff |
| `/merge` | Merge current session branch |
| `/invalidate` | Force re-consultation for an agent |

## Agents

=== "Deployer"

    Triggers: `roll`, `roll forward`, `roll backward`, `publish`, `migrate`

    Authority
    :   kubectl writes, container registry, Redis

    Exclusive Tools
    :   postgres.py, Redis MCP

    Style
    :   Reactive — executes on request

    Consults
    :   [designer](consultation.md) (pattern perspective), [sauron](consultation.md) (monitoring impact)

    **Commands**

    | Command | Description |
    |---------|-------------|
    | `/deployer:roll` | Roll between environments |
    | `/deployer:stop` | Scale down an environment |
    | `/deployer:clean` | Clean up environment data |
    | `/deployer:diff` | Stage incremental data changes |
    | `/deployer:bootstrap` | Bootstrap cluster infrastructure |

    **Memory**

    | | Static | Dynamic |
    |---|---|---|
    | **Global** | infra.md, migration.md, troubleshooting.md | auto-managed |
    | **Project** | `deployer/static/` — k8s manifests | `deployer/dynamic/` — operational notes |

=== "Sauron"

    Triggers: `add monitoring`, `add metrics`, `health check`, `prometheus`, `dashboard`, `set up logging`, `add logging`, `review logs`, `run tests`, `code validation`, `validate code`

    Authority
    :   Grafana, code fixes, standards testing

    Exclusive Tools
    :   nokrashi-tools, klog, Grafana MCP

    Style
    :   Act first, report after

    Consults
    :   [designer](consultation.md) (pattern monitoring perspective), [deployer](consultation.md) (cluster state)

    **Commands**

    | Command | Description |
    |---------|-------------|
    | `/sauron:scan` | Scan a project for monitoring gaps |
    | `/sauron:diagnose` | Diagnose a specific issue |

    **Memory**

    | | Static | Dynamic |
    |---|---|---|
    | **Global** | monitoring.md, logging.md, dashboards/ | auto-managed |
    | **Project** | `sauron/static/` — dashboards, alert rules | `sauron/dynamic/` — monitoring notes |

=== "Designer"

    Triggers: `review architecture`, `design review`

    Authority
    :   Pattern definitions, architecture review

    Exclusive Tools
    :   Gemini (design validation)

    Style
    :   Analytical — validates against patterns

    Consults
    :   [deployer](consultation.md) (infrastructure reality), [sauron](consultation.md) (observability gaps)

    **Commands**

    | Command | Description |
    |---------|-------------|
    | `/designer:detect-patterns` | Scan a project for recognized patterns |

    **Memory**

    | | Static | Dynamic |
    |---|---|---|
    | **Global** | patterns/\*.md, libraries/\*.md | auto-managed |

=== "Scribe"

    Triggers: `update docs`, `update profile docs`, `update project docs`, `add api key`, `store api key`, `add mcp`, `update agent docs`, `write readme`, `update readme`

    Authority
    :   All `.md` file edits

    Exclusive Tools
    :   Gemini (doc review)

    Style
    :   Coordinate — write-gate for all docs

    Consults
    :   [designer](consultation.md) (architecture context), [sauron](consultation.md) (monitoring context), [deployer](consultation.md) (infrastructure context)

    **Commands**

    | Command | Description |
    |---------|-------------|
    | `/scribe:add-mcp` | Add a new MCP server entry |
    | `/scribe:update-agent-docs` | Update an agent's documentation |
    | `/scribe:update-project-docs` | Update project-level docs |
    | `/scribe:update-subagent-memory` | Update agent memory files |

    **Memory**

    | | Static | Dynamic |
    |---|---|---|
    | **Global** | templates/ | auto-managed |
