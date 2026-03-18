# Kordinate

Multi-cluster k8s infrastructure managed by specialized agents.

## Agents

| Agent | Triggers | Purpose |
|-------|----------|---------|
| deployer | "roll", "migrate", "stop", "clean", "diff" | GitOps deployments |
| sauron | "add monitoring", "add metrics", "health check", "dashboard", "run tests", ... | Monitoring & validation |
| designer | "review architecture", "design review" | Architecture review + pattern authority |
| scribe | "update docs", "add api key", "add mcp", "write readme", ... | Documentation (sole .md editor) |

## Consultation

When the user says "consult", "ask", or "check with" an agent, run `/consult <agent> "<question>"`.

| Agent | Expertise |
|-------|-----------|
| designer | Architecture, components, failure modes, data flow, design patterns |
| sauron | Metrics, health checks, log events, dashboards |
| deployer | Cluster state, pod status, deployment status, versions, networking |

## Rules

- When launching subagents, check `.claude/agent-state/<name>.json` for `agent_id` to resume. Store the returned ID back after invocation.
- Never invoke an agent's operational commands directly — spawn the owning agent. Only `consult` and scribe commands may be invoked directly as skills.
- All `.md` files are protected — only the scribe agent may edit them (hook-enforced)
- Never let more than 3 user messages with code changes pass without committing and pushing
- Sessions auto-create worktrees via `bin/claude-session` — do not create worktrees manually
- After pushing to a session branch, the `auto-merge-to-dev.sh` hook tries to fast-forward main. If it fails, run `/merge`.

## Branch Model

`session/*` → `main` → `test` → `prod`
