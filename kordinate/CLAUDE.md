# Global Claude Code Guidelines

*Applies to all projects unless overridden in project-specific CLAUDE.md*

## Context

Kordinate repo at `~/kordinate/`. Multi-cluster k8s infrastructure — agents, commands, config, and knowledge all live here. Deploys to clusters via SSH.

For reference: `~/.claude/agent-memory/deployer/infra.md` · `~/.claude/profile/config.yaml`

---

## Rules

- Credentials live in `pass` under `kordinate/` — agents read with `pass show` and write with `pass insert` directly. Agent auth locks live in `profile/locks/`, and `profile/keystore` symlinks to the pass store.
- Follow the project's existing patterns — don't introduce new libraries, frameworks, or conventions
- Never edit profile docs directly — delegate to the scribe agent (see Profile Doc Policy below)
- Never let more than 3 user messages with code changes pass without committing and pushing
- Sessions auto-create worktrees via `bin/claude-session` — do not create worktrees manually
- After pushing to a session branch, the `auto-merge-to-dev.sh` PostToolUse hook tries a direct fast-forward push to main. If it fails, it instructs you to run `/merge` for conflict resolution.
- Only the deployer agent may run kubectl write operations (apply, delete, scale, etc.) — enforced by `guard-kubectl.sh` hook
- Only the sauron agent may use Grafana MCP tools — enforced by `guard-grafana.sh` hook. Other agents consult sauron for dashboard/metrics data.
- Only the deployer agent may use Redis MCP tools — enforced by `guard-redis.sh` hook. Other agents consult deployer for Redis state.
- When launching subagents, check `.claude/agent-state/<name>.json` for the agent's `agent_id`. If one exists, pass it as the `resume` parameter; if not, omit `resume` to spawn a fresh agent. Always store the returned agent ID back to `.claude/agent-state/<name>.json` after invocation.
- Never invoke an agent's operational commands directly via the Skill tool — spawn the owning agent instead. Operational commands require the agent's CLAUDE.md, auth, and context. Only `consult` commands and scribe commands may be invoked directly as skills.

---

## Agent Knowledge

- **Pattern index** — `agent-memory/designer/patterns.md` — catalog of all recognized design patterns with categories and descriptions. The designer agent is the pattern authority; other agents consult the designer for pattern context.
- **Per-agent knowledge** — `agent-memory/<agent>/` — curated docs and auto-managed memory, organized by topic
- **Per-project knowledge** — `<project-repo>/.claude/agent-memory/<agent>/` — project-specific operational docs (metrics, health checks, deploy config)
- **Per-project monitoring** — `<project-repo>/monitoring/` — dashboards, health checks, alerting (discovered by convention)

## Agents

| Agent | Triggers | Purpose |
|-------|----------|---------|
| sauron | "add monitoring", "add metrics", "health check", "dashboard", "set up logging", "run tests", "code validation" | Monitoring & validation: metrics, health, logging, dashboards, testing |
| designer | "review architecture", "design review" | Architecture review + produces docs/architecture.md |
| deployer | "roll", "migrate", "stop", "clean", "diff" | GitOps: roll between environments, lifecycle management |
| scribe | "update docs", "add api key", "add project", "add mcp" | Sole editor of all documentation (.md files) |

## Branch Model

| Branch | Role | Updated by |
|--------|------|------------|
| `session/*` | Isolated Claude session work | `bin/claude-session` (auto-created) |
| `main` | Active development (dev) | auto-merge hook / `/merge` skill |
| `test` | Staging | deployer (`roll main test`) |
| `prod` | Production | deployer (`roll test prod`) |

Flow: `session/*` → main → test → prod

All projects follow this branch model regardless of deployment method (kubectl or git-branch). The branch always reflects what is deployed to each environment.

## Consultation Protocol

Agents consult each other via `/consult <agent> "<question>"` — a generic command that spawns the target agent and asks the question. Each agent's CLAUDE.md has a Consultation section defining its expertise and how it answers.

When the user says "consult <agent>", "ask <agent>", or "check with <agent>" followed by a question, run `/consult <agent> "<question>"`.

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, design patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |

## Documentation Policy

All `.md` files are protected. Only the **scribe agent** may edit them — enforced by a native PreToolUse hook with token-based auth.

## Agent Memory Model

Two-tier state:

**Agent memory (cross-project)** — `~/.claude/agent-memory/<name>/` (tracked in git):
- Curated knowledge and Claude auto-managed memory live side by side
- Cross-project docs: `agent-memory/<agent>/<topic>.md`
- Pattern index: `agent-memory/designer/patterns.md` (designer is the pattern authority)
- The `guard-md.sh` hook exempts `agent-memory/` paths so agents can write freely

**Project-specific knowledge** — lives in the project repo:
- Agent memory: `<repo>/.claude/agent-memory/<agent>/` — operational notes, metrics catalogs, debug references
- Manifests: `<repo>/manifests/` — k8s manifests discovered by convention; cluster/registry info from `profile/clusters/*.yaml`
- Monitoring: `<repo>/monitoring/` — dashboards, health checks, alerting (discovered by convention)

**Session-ephemeral** — `.claude/agent-state/<name>.json` (gitignored):
- session_id, last_line, last_commit, agent_id, context_summary

### Where does it go?

| Question | Location | Examples |
|----------|----------|---------|
| Useful across any project? | `agent-memory/<agent>/` | cAdvisor patterns, library docs, infra monitoring reference |
| Tied to a specific project? | `<project-repo>/.claude/` | agent-memory/sauron/metrics.md |
| Project monitoring artifacts? | `<project-repo>/monitoring/` | dashboards/, health.yaml, grafana-dashboards-patch.json |
