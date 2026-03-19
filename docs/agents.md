# Agents

## Overview

| Agent | Triggers | What it does |
|-------|----------|-------------|
| deployer | `roll`, `roll forward`, `roll backward`, `publish`, `migrate` | Rolls deployments between environments, manages infrastructure |
| sauron | `add monitoring`, `add metrics`, `health check`, `prometheus`, `dashboard`, `set up logging`, `add logging`, `review logs`, `run tests`, `code validation`, `validate code` | Adds monitoring, validates code, manages dashboards |
| designer | `review architecture`, `design review` | Reviews architecture, owns design patterns |
| scribe | `update docs`, `update profile docs`, `update project docs`, `add api key`, `store api key`, `add mcp`, `update agent docs`, `write readme`, `update readme` | Sole editor of `.md` files |

## Agent Specifics

=== "Shared"

    All agents inherit these rules (source: `agents/shared/MEMORY.md` + `AGENT.md`).

    | | |
    |---|---|
    | **Permissions** | deployer: kubectl + Redis MCP. sauron: Grafana MCP. scribe: `.md` edits (hook-enforced). Never invoke an agent's operational commands directly — spawn the owning agent. |
    | **Conventions** | Credentials in `pass` under `kordinate/`. Auth locks in `profile/locks/`. Follow existing patterns. Commit with `[<agent-name>]`. Project artifacts go in the project repo. |
    | **Memory** | `static/` (pre-defined structure) + `dynamic/` (free-form) — same model at [global and project scope](memory.md#memory-model). Agent resumption: check `.claude/agent-state/<name>.json` for `agent_id`. |
    | **Commands** | `/boot` (initialize workstation), `/consult` (query agent), `/merge` (merge session branch), `/invalidate` (force re-consultation) |

=== "Deployer"

    | | |
    |---|---|
    | **Authority** | kubectl writes, container registry, Redis |
    | **Exclusive Tools** | postgres.py, Redis MCP |
    | **Commands** | `/deployer:roll` (roll between envs), `/deployer:stop` (scale down), `/deployer:clean` (clean env data), `/deployer:diff` (stage incremental changes), `/deployer:bootstrap` (bootstrap cluster) |
    | **Global Static** | infra.md, migration.md, troubleshooting.md |
    | **Global Dynamic** | auto-managed notes |
    | **Project Static** | `deployer/static/` — k8s manifests |
    | **Project Dynamic** | `deployer/dynamic/` — operational notes |
    | **Style** | Reactive — executes on request |

=== "Sauron"

    | | |
    |---|---|
    | **Authority** | Grafana, code fixes, standards testing |
    | **Exclusive Tools** | nokrashi-tools, klog, Grafana MCP |
    | **Commands** | `/sauron:scan` (scan for monitoring gaps), `/sauron:diagnose` (diagnose issue) |
    | **Global Static** | monitoring.md, logging.md, dashboards/ |
    | **Global Dynamic** | auto-managed notes |
    | **Project Static** | `sauron/static/` — dashboards, alert rules |
    | **Project Dynamic** | `sauron/dynamic/` — monitoring notes, findings |
    | **Style** | Act first, report after |

=== "Designer"

    | | |
    |---|---|
    | **Authority** | Pattern definitions, architecture review |
    | **Exclusive Tools** | Gemini (design validation) |
    | **Commands** | `/designer:detect-patterns` (scan for recognized patterns) |
    | **Global Static** | patterns/\*.md, libraries/\*.md |
    | **Global Dynamic** | auto-managed notes |
    | **Project Static** | — |
    | **Project Dynamic** | — |
    | **Style** | Analytical — validates against patterns |

=== "Scribe"

    | | |
    |---|---|
    | **Authority** | All `.md` file edits |
    | **Exclusive Tools** | Gemini (doc review) |
    | **Commands** | `/scribe:add-mcp` (add MCP entry), `/scribe:update-agent-docs` (update agent docs), `/scribe:update-project-docs` (update project docs), `/scribe:update-subagent-memory` (update agent memory) |
    | **Global Static** | templates/ |
    | **Global Dynamic** | auto-managed notes |
    | **Project Static** | — |
    | **Project Dynamic** | — |
    | **Style** | Coordinate — write-gate for all docs |
