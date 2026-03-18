# Agents

## Overview

| Agent    | Triggers                                           | Purpose                    |
|----------|---------------------------------------------------|----------------------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff`        | GitOps deployments         |
| sauron   | `add monitoring`, `add metrics`, `health check`, `dashboard`, `run tests`, ... | Observability & validation |
| designer | `review architecture`, `design review`            | Architecture review + pattern authority |
| scribe   | `update docs`, `add api key`, `add mcp`, `write readme`, ... | Documentation (sole `.md` editor) |

```
User message
 │
 ├── matches trigger ──► spawn agent
 │   ├── deployer ──► kubectl ops   (guard-kubectl, guard-git, guard-redis)
 │   ├── sauron ────► monitoring    (guard-grafana)
 │   ├── designer ──► architecture
 │   └── scribe ────► .md edits     (guard-md)
 │
 └── /consult <agent> "question"
     └── agent reads knowledge ──► returns answer
```

## Hooks

| Hook                 | What It Guards                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| `guard-kubectl.sh`   | Blocks kubectl write operations via SSH unless deployer is authorized. Master namespace requires bootstrap auth. Workstation resources always blocked. |
| `guard-md.sh`        | Blocks `.md` file edits unless scribe is authorized.                          |
| `guard-grafana.sh`   | Blocks Grafana MCP calls unless sauron is authorized.                         |
| `guard-redis.sh`     | Blocks Redis MCP calls unless deployer is authorized.                         |
| `guard-git.sh`       | Blocks git push to test/prod branches unless deployer is authorized.          |
| `auto-merge-to-dev.sh` | Post-push hook that auto-merges session branches to main.                  |

## Lock-Based Authorization

Agents authorize themselves by placing a lock file before operating:

1. Agent copies lock from `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Hook compares lock file with `/tmp/` file
3. Agent removes lock file after completing work

## Consultation Protocol

Ask an agent a question without transferring full control:

```
/consult deployer "Is your-app healthy on cluster-a?"
```

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, design patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |

## Commands

| Command           | Description                                          |
|-------------------|------------------------------------------------------|
| `/boot`           | Initialize the workstation environment               |
| `/consult`        | Query an agent without full handoff                  |
| `/merge`          | Merge current session branch                         |
| `/deployer:roll`  | Roll between environments                            |
| `/deployer:stop`  | Scale down an environment                            |
| `/deployer:clean` | Clean up environment data                            |
| `/deployer:diff`  | Stage incremental data changes                       |
| `/deployer:bootstrap` | Bootstrap cluster infrastructure                 |

## Memory

Each agent has a `memory/` directory with two layers:

```
agents/<agent>/
├── AGENT.md
├── commands/
└── memory/
    ├── *.md              # curated knowledge (generic)
    ├── libraries/        # library reference docs
    └── operational/      # auto-managed memory (encrypted)
```

Claude auto-loads `MEMORY.md` from `operational/` on startup. Curated knowledge at the parent `memory/` level is read on demand.

| What | Where |
|------|-------|
| Generic knowledge | `agents/<agent>/memory/` |
| Site-specific auto-memory | `agents/<agent>/memory/operational/` (encrypted) |
| Project-specific | `<project-repo>/.claude/agent-memory/<agent>/` |
| Project manifests | `<project-repo>/manifests/` |
| Project monitoring | `<project-repo>/monitoring/` |
