# Agents

## What is an Agent?

In Kordinate, an **agent** is a specialized Claude Code subagent with its own role, memory, tools, and permissions. Each agent owns a narrow domain — deployments, monitoring, architecture, documentation — and operates independently within that domain.

Agents are **kord'd into a team**: they share common rules, a consultation protocol, and a memory model, but each has exclusive authority over its own tools and resources. The framework enforces boundaries via [hooks](hooks.md) so agents cannot step outside their domain. Teams are composed by defining agents and wiring them together through shared rules, consultation matrices, and hook guards.

The scribe agent is a **core framework agent** — it manages all `.md` file edits and is present in every Kordinate team. Other agents are team-specific and defined per deployment.

## Overview

| Agent | What it does |
|-------|-------------|
| **scribe** | Sole editor of `.md` files (core framework agent) |
| *team agents* | Defined per team — e.g., deployer, sauron, designer |

## Rules

All agents inherit these rules (source: `agents/shared/MEMORY.md` + `AGENT.md`).

!!! info "Permissions"
    - Only **scribe** may edit `.md` files (hook-enforced)
    - Never invoke an agent's operational commands directly — spawn the owning agent
    - Each team defines additional exclusive permissions per agent

    Permissions are per-agent and enforced by guard hooks. For instance, in the infra team: deployer has exclusive kubectl and Redis MCP access, sauron has exclusive Grafana MCP access.

!!! note "Conventions"
    - Credentials live in `pass` under `kordinate/`. Auth locks in `profile/locks/`.
    - Follow existing patterns — no new libraries, frameworks, or conventions
    - Commit with `[<agent-name>]` in message
    - Project artifacts go in the project repo, not kordinate

!!! tip "Memory"
    `static/` (pre-defined structure) + `dynamic/` (free-form) — same model at [global and project scope](memory.md#memory-model). Agent resumption: check `.claude/agent-state/<name>.json` for `agent_id`.

## Commands

=== "Shared"

    | Command | Description |
    |---------|-------------|
    | `/boot` | Initialize the workstation environment |
    | `/consult` | Query an agent without full handoff |
    | `/merge` | Merge current session branch |
    | `/invalidate` | Force re-consultation for an agent |

=== "Scribe"

    | Command | Description |
    |---------|-------------|
    | `/scribe:add-mcp` | Add a new MCP server entry |
    | `/scribe:update-agent-docs` | Update an agent's documentation |
    | `/scribe:update-project-docs` | Update project-level docs |
    | `/scribe:update-subagent-memory` | Update agent memory files |

## Scribe Details

| | |
|---|---|
| **Triggers** | `update docs`, `update profile docs`, `update project docs`, `add api key`, `store api key`, `add mcp`, `update agent docs`, `write readme`, `update readme` |
| **Authority** | All `.md` file edits |
| **Exclusive Tools** | Gemini (doc review) |
| **Style** | Coordinate — write-gate for all docs |
| **Consults** | [designer](consultation.md) (architecture context), [sauron](consultation.md) (monitoring context), [deployer](consultation.md) (infrastructure context) |

**Memory**

| | Static | Dynamic |
|---|---|---|
| **Global** | templates/ | auto-managed |
