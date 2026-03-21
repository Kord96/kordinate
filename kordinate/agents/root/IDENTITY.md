# Kordinate

Multi-cluster k8s infrastructure managed by specialized agents.

## Agents

| Agent | Triggers | Purpose |
|-------|----------|---------|
| deployer | "roll", "migrate", "stop", "clean", "diff" | GitOps deployments |
| sauron | "add monitoring", "add metrics", "health check", "dashboard", "run tests", ... | Monitoring & validation |
| designer | "review architecture", "design review" | Architecture review + pattern authority |
| scribe | "update docs", "add api key", "add mcp", "write readme", ... | Documentation (sole .md editor) |
| beorn | (MCP — always on) | Shape-shifting agent server — delegates prompts to any agent via `mcp__beorn__delegate` |

## Beorn (MCP)

Shape-shifting agent server. Always-on service that invokes any agent's identity on demand.

| Tool | Purpose |
|------|---------|
| `mcp__beorn__delegate` | Invoke an agent: `{ agent: "deployer", prompt: "..." }` |
| `mcp__beorn__status` | Check beorn uptime, known agents, active requests |

Use `mcp__beorn__delegate` for inter-agent communication without spawning subagents. Beorn loads the target agent's identity and memory, runs `claude --print`, and returns the response.

## Kords

Agent coordination agreements. Use `/consult <agent-or-kord> "<question>"` to invoke.

| Kord | Requester | Provider |
|------|-----------|----------|
| `default-deployer` | any | deployer |
| `default-sauron` | any | sauron |
| `default-designer` | any | designer |
| `default-scribe` | any | scribe |
| `pattern-review` | deployer, sauron | designer |
| `monitoring-impact` | deployer | sauron |

Shorthand: `/consult deployer "..."` resolves to the `default-deployer` kord.

## Rules

- When launching subagents, check `.claude/agent-state/<name>.json` for `agent_id` to resume. Store the returned ID back after invocation.
- Never invoke an agent's operational commands directly — spawn the owning agent. Only `consult` and scribe commands may be invoked directly as skills.
- All `.md` files are protected — only the scribe agent may edit them (hook-enforced)
- Never let more than 3 user messages with code changes pass without committing and pushing
- Sessions auto-create worktrees via `bin/claude-session` — do not create worktrees manually
- After pushing to a session branch, the `auto-merge-to-dev.sh` hook tries to fast-forward main. If it fails, run `/merge`.

## Branch Model

`session/*` → `main` → `test` → `prod`
