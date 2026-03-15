# Global Claude Code Guidelines

*Applies to all projects unless overridden in project-specific CLAUDE.md*

## Context

Multi-cluster k8s infrastructure. Code lives in this repo, deploys to clusters via SSH.

For reference: `~/.claude/agents/deployer/knowledge/infra.md` · `~/.claude/profile/conventions.md` · `agents/changelog.md`

---

## Rules

- Credentials live in `pass` under `kordinate/` — agents read with `pass show` and write with `pass insert` directly.
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

Each agent has a `knowledge/` directory with docs organized by scope:
- **Cross-project** — `knowledge/<topic>.md` (e.g., `infra-monitoring.md`, `stoik.md`) — general expertise
- **Project-specific** — `knowledge/projects/<project>/` — per-project reference docs (metrics catalogs, debug references, etc.)

Agents read their own knowledge docs instead of fetching metadata at runtime.

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
| designer | Architecture, components, failure modes, data flow |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |

For async inter-agent messaging, use `/scribe:text <agent> "<message>"` to append a timestamped message to the target agent's inbox (`~/.claude/agents/<name>/inbox.md`). Agents check their inbox on startup, periodically, and before returning results.

## Changelog Protocol

`agents/changelog.md` is a shared append-only operational log. Agents append entries after significant changes (deployments, infra updates, monitoring changes, architecture decisions). Other agents check it before consulting to avoid unnecessary subagent invocations.

- **Format**: `## YYYY-MM-DD HH:MM [agent] topic` followed by a brief description
- **Topics**: `infra`, `dashboards`, `monitoring`, `deployment`, `architecture`, `docs`, `migration`
- **Read before consulting**: If no new entries from the target agent since your last check, use cached knowledge instead of spawning a consultation
- Each agent tracks `last_changelog_line` in `.claude/agent-state/<name>.json` to know what's new

## Documentation Policy

All `.md` files are protected. Only the **scribe agent** may edit them — enforced by a native PreToolUse hook with token-based auth.

## Agent Memory Model

Three-tier state:

**Knowledge** — `~/.claude/agents/<name>/knowledge/` (profile repo):
- Cross-project docs: `knowledge/<topic>.md`
- Project-specific docs: `knowledge/projects/<project>/`
- Authoritative reference material — agents read these instead of fetching at runtime

**Native memory** — `~/.claude/agent-memory/<name>/` (enabled via `memory: user` in frontmatter):
- Claude auto-manages persistent memory files across sessions
- The `guard-md.sh` hook exempts `agent-memory/` paths so agents can write freely
- Use for behavioral preferences and cross-project operational notes only

**Local** — `.claude/agent-state/<name>.json` (gitignored):
- session_id, last_line, last_commit, last_changelog_line, agent_id, context_summary

The repo contains agent definitions (CLAUDE.md, commands/, knowledge/) but no runtime state.

---

*Last Updated*: 2026-03-15
