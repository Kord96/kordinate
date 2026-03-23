# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Claude Code

Claude Code reads from two scopes: `~/.claude/` (user — all projects) and `.claude/` (project — committed to repo). Project takes precedence when names collide.

### Agents

Flat markdown files with YAML frontmatter. No nested directories — each agent is a single file.

| Claude Code path | Scope | Git |
|-----------------|-------|-----|
| `~/.claude/agents/<name>.md` | user | outside repo |
| `.claude/agents/<name>.md` | project | committed |

The filename must match the `name` frontmatter field. The markdown body becomes the agent's system prompt.

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
skills:
  - api-conventions
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
---

System prompt goes here. This is the agent's identity and instructions.
```

Supported frontmatter fields:

| Field | Purpose |
|-------|---------|
| `name` | Agent identity (lowercase, hyphens) |
| `description` | When to delegate to this agent |
| `tools` | Allowed tools (e.g. `Read, Bash, Agent(worker)`) |
| `disallowedTools` | Tools to deny |
| `model` | `sonnet`, `opus`, `haiku`, or full model ID |
| `memory` | `user`, `project`, or `local` |
| `skills` | Skills to inject at startup (by name) |
| `hooks` | Inline hook definitions (scoped to agent lifetime) |
| `mcpServers` | MCP servers scoped to this agent |
| `maxTurns` | Max agentic turns before stopping |
| `permissionMode` | Permission handling mode |
| `background` | Run in background by default |
| `effort` | Effort level (`low`, `medium`, `high`, `max`) |
| `isolation` | Set to `worktree` for isolated git worktree |

### Agent Memory

Each agent with a `memory` field gets its own `MEMORY.md`. The first 200 lines are auto-injected into the agent's context at startup. `Read`, `Write`, and `Edit` tools are auto-enabled when memory is set.

| Claude Code path | Scope | Git |
|-----------------|-------|-----|
| `~/.claude/agent-memory/<name>/MEMORY.md` | user | outside repo |
| `.claude/agent-memory/<name>/MEMORY.md` | project | committed — shared with developer team |
| `.claude/agent-memory-local/<name>/MEMORY.md` | local | gitignored — personal to developer |

### Skills

Global, not agent-scoped. Agents reference them by name in frontmatter; content is injected at startup. Skills support nested directories (unlike agents).

| Claude Code path | Scope |
|-----------------|-------|
| `~/.claude/skills/<name>/SKILL.md` | user |
| `.claude/skills/<name>/SKILL.md` | project |

### Hooks

1. **Inline** — defined in agent frontmatter, scoped to agent lifetime
2. **Global** — defined in `settings.json`, run for the entire session

Global hooks support `SubagentStart` and `SubagentStop` events for reacting to subagent lifecycle.

### Invocation

| Method | Who | When |
|--------|-----|------|
| `claude --agent name` | Developer (CLI) | Session start — becomes the root agent |
| `@agent-name` in prompt | Developer (interactive) | Mid-session — forces delegation |
| Agent tool (`subagent_type`) | Agent (programmatic) | Mid-session — one agent spawns another |
| Natural language | Developer or agent | Mid-session — Claude auto-delegates |

Subagents cannot spawn other subagents (no recursive Agent tool). Priority when names collide: `--agents` CLI flag > `.claude/agents/` > `~/.claude/agents/` > plugin agents.

### Other Config

Direct copies between kordinate and Claude Code:

| Claude Code path | Purpose |
|-----------------|---------|
| `settings.json` | Permissions, hooks, env vars |
| `.mcp.json` | MCP server configuration |
| `keybindings.json` | Keyboard shortcuts |
| `CLAUDE.md` | Root system prompt — inherited by all subagents |
| `commands/*.md` | Slash commands |

## Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

| `~/.claude/` | `~/.kord/` source | Transform |
|-------------|-------------------|-----------|
| `settings.json` | `settings.json` | copy |
| `.mcp.json` | `mcp.json` | rename |
| `keybindings.json` | `keybindings.json` | copy |
| `CLAUDE.md` | `root/identity.md` + `team/manifest.md` | merge |
| `agents/<name>.md` | `<agent>/identity.md` | rename, generate frontmatter |
| `commands/*.md` | `root/commands/*.md` | copy |
| `agent-memory/<name>/` | `<agent>/memory/` | restructure |

No symlinks. Claude Code works with real files. `~/.kord/` is the portable format.

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
