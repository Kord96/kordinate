# Agent Guidelines

*Applies to all projects unless overridden in project-specific instructions*

## On Startup

1. Read all files in your `memory/` directory
2. If in a project repo: check for `<repo>/.claude/agent-memory/<you>/`, `<repo>/manifests/`, `<repo>/monitoring/`
3. Run `/boot`

## Rules

- Credentials live in `pass` under `kordinate/`. Agent auth locks live in `profile/locks/`.
- Follow the project's existing patterns — don't introduce new libraries, frameworks, or conventions
- All `.md` files are protected — only the scribe agent may edit them (hook-enforced)
- Never let more than 3 user messages with code changes pass without committing and pushing
- Sessions auto-create worktrees via `bin/claude-session` — do not create worktrees manually
- After pushing to a session branch, the `auto-merge-to-dev.sh` hook tries to fast-forward main. If it fails, run `/merge`.
- Only the deployer agent may run kubectl write operations — enforced by `guard-kubectl.sh`
- Only the sauron agent may use Grafana MCP tools — enforced by `guard-grafana.sh`
- Only the deployer agent may use Redis MCP tools — enforced by `guard-redis.sh`
- When launching subagents, check `.claude/agent-state/<name>.json` for `agent_id` to resume. Store the returned ID back after invocation.
- Never invoke an agent's operational commands directly — spawn the owning agent. Only `consult` and scribe commands may be invoked directly as skills.

## Agents

| Agent | Triggers | Purpose |
|-------|----------|---------|
| sauron | "add monitoring", "add metrics", "health check", "prometheus", "dashboard", "set up logging", "add logging", "review logs", "run tests", "code validation", "validate code" | Monitoring & validation |
| designer | "review architecture", "design review" | Architecture review + pattern authority |
| deployer | "roll", "migrate", "stop", "clean", "diff" | GitOps deployments |
| scribe | "update docs", "update profile docs", "update project docs", "add api key", "store api key", "add mcp", "update agent docs", "write readme", "update readme" | Documentation (sole .md editor) |

## Branch Model

`session/*` → `main` → `test` → `prod`

All projects follow this model. The branch reflects what is deployed to each environment.

## Consultation

When the user says "consult", "ask", or "check with" an agent, run `/consult <agent> "<question>"`.

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, design patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |

## Memory

| What to write | Where |
|---------------|-------|
| Generic knowledge | `memory/static/` |
| Site-specific notes | `memory/dynamic/` |
| Project-specific | `<repo>/.claude/agent-memory/<you>/` |
