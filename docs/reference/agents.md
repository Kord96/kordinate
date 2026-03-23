# Agent Reference

=== "Root"

    The orchestrator. All items below are inherited by every subagent.

    **Requirements:** none

    ### Commands

    | Command | Purpose |
    |---------|---------|
    | `/boot` | Catch up on parent context and code changes |
    | `/consult` | Invoke an agent via kord protocol |
    | `/merge` | Merge session branch forward |

    ### Guards

    | Guard | Protects |
    |-------|----------|
    | `guard-git.sh` | Branch protection |
    | `guard-md.sh` | Structured files — scribe only |

    ### Hooks

    | Hook | Trigger | Purpose |
    |------|---------|---------|
    | `auto-merge-to-dev.sh` | PostToolUse (Bash) | Fast-forward main after push |
    | `agent-memory.sh` | PreToolUse (Agent) | Regenerate agent MEMORY.md before spawn |

=== "Scribe"

    Documentation gate — sole structured file editor.

    **Requirements:** none

    ### Commands

    | Command | Purpose |
    |---------|---------|
    | `/scribe:onboard` | Add a new agent to the team |
    | `/scribe:kord` | Define a new kord |
    | `/scribe:update-agent-docs` | Update agent documentation |
    | `/scribe:update-project-docs` | Update project documentation |

=== "Beorn"

    **Requirements:** beorn server (Node.js MCP server)

    A short-lived agent clone. Takes the skin of the agent it clones — inheriting its identity, memory, commands, and rules. Has no tools, commands, or hooks of its own.

    See [Subagent P2P](../framework/beorn.md) for the beorn server (MCP factory) architecture.

=== "Deployer"

    Infrastructure operations — sole kubectl write authority.

    **Requirements:** container registry, kubectl access

    ### Commands

    | Command | Purpose |
    |---------|---------|
    | `/deployer:roll` | Roll between environments |
    | `/deployer:stop` | Scale down an environment |
    | `/deployer:clean` | Clean up environment data |
    | `/deployer:diff` | Stage incremental data changes |
    | `/deployer:bootstrap` | Bootstrap cluster infrastructure |
    | `/deployer:migrate-workstation` | Prepare workstation migration handover |

    ### Guards

    | Guard | Protects |
    |-------|----------|
    | `guard-kubectl.sh` | kubectl write operations — deployer only |

    ### Tools

    | Tool | Purpose |
    |------|---------|
    | postgres.py | Local database operations |

=== "Sauron"

    Monitoring, observability, and code validation.

    **Requirements:** Grafana, Prometheus, Loki, Alloy (deployed on demand)

    ### Commands

    | Command | Purpose |
    |---------|---------|
    | `/sauron:scan` | Scan a project for monitoring gaps |
    | `/sauron:diagnose` | Diagnose a specific issue |

    ### Guards

    | Guard | Protects |
    |-------|----------|
    | `guard-grafana.sh` | Grafana MCP tools — sauron only |

    ### Tools

    | Tool | Purpose |
    |------|---------|
    | Grafana MCP | Dashboard management |
    | nokrashi-tools | Code analysis |
    | klog | Log analysis |

=== "Designer"

    Architecture review and pattern authority.

    **Requirements:** none

    ### Commands

    | Command | Purpose |
    |---------|---------|
    | `/designer:detect-patterns` | Scan a project for recognized patterns |
