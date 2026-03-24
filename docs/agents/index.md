# Agent Reference

## Agent Structure

Every agent follows the same layout. Use `/scribe:onboard` to add new agents to the team.

```
<agent>/
├── identity.md          # role, tools, auth, workflow, rules
├── skills/<name>/SKILL.md  # skill definitions
└── memory/
    ├── index.md          # on-demand file listing
    └── *.md              # domain knowledge, notes
```

Any agent can be invoked as root (the main session) or as a subagent through [beorn](beorn.md). The structure is the same either way — identity, skills, and memory travel with the agent regardless of how it's invoked.

## Roster

=== "General"

    The default agent. Provides shared skills, guards, and hooks inherited by every subagent.

    **Requirements:** none

    | Type | Name | Purpose |
    |------|------|---------|
    | skill | `/boot` | Catch up on parent context and code changes |
    | skill | `/consult` | Invoke an agent via kord protocol |
    | skill | `/merge` | Merge session branch forward |
    | guard | `guard-git.sh` | Branch protection |
    | guard | `guard-md.sh` | Structured files — scribe only |
    | hook | `auto-merge-to-dev.sh` | Fast-forward main after push |
    | hook | `agent-memory.sh` | Regenerate agent MEMORY.md before spawn |

=== "Scribe"

    Documentation gate — sole structured file editor.

    **Requirements:** none

    | Type | Name | Purpose |
    |------|------|---------|
    | skill | `/scribe:onboard` | Add a new agent to the team |
    | skill | `/scribe:kord` | Define a new kord |
    | skill | `/scribe:update-agent-docs` | Update agent documentation |
    | skill | `/scribe:update-project-docs` | Update project documentation |

=== "Beorn"

    MCP server that enables any subagent to invoke any other subagent. Spawns short-lived clones that inherit the target agent's identity, memory, and skills. See [Beorn](beorn.md) for details.

    **Requirements:** beorn server (Node.js MCP server)

=== "Deployer"

    Infrastructure operations — sole kubectl write authority.

    **Requirements:** container registry, kubectl access

    | Type | Name | Purpose |
    |------|------|---------|
    | skill | `/deployer:roll` | Roll between environments |
    | skill | `/deployer:stop` | Scale down an environment |
    | skill | `/deployer:clean` | Clean up environment data |
    | skill | `/deployer:diff` | Stage incremental data changes |
    | skill | `/deployer:bootstrap` | Bootstrap cluster infrastructure |
    | skill | `/deployer:migrate-workstation` | Prepare workstation migration handover |
    | guard | `guard-kubectl.sh` | kubectl write operations — deployer only |
    | tool | `postgres.py` | Local database operations |

=== "Sauron"

    Monitoring, observability, and code validation.

    **Requirements:** Grafana, Prometheus, Loki, Alloy (deployed on demand)

    | Type | Name | Purpose |
    |------|------|---------|
    | skill | `/sauron:scan` | Scan a project for monitoring gaps |
    | skill | `/sauron:diagnose` | Diagnose a specific issue |
    | guard | `guard-grafana.sh` | Grafana MCP tools — sauron only |
    | tool | Grafana MCP | Dashboard management |
    | tool | nokrashi-tools | Code analysis |
    | tool | klog | Log analysis |

=== "Designer"

    Architecture review and pattern authority.

    **Requirements:** none

    | Type | Name | Purpose |
    |------|------|---------|
    | skill | `/designer:detect-patterns` | Scan a project for recognized patterns |
