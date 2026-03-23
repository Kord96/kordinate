# Root

The orchestrator. Root is the user's existing agent — Claude Code, Codex, Cursor, or any compatible runtime. It defines the team, and all subagents inherit its rules, commands, and hooks.

## Claude Code Filesystem

Claude Code reads from two locations: `~/.claude/` (user scope) and `.claude/` (project scope). Project scope takes precedence when names collide.

### Agents

Flat markdown files with YAML frontmatter. No nested directories — each agent is a single file.

```
~/.claude/agents/agent-name.md        # user scope (all projects)
.claude/agents/agent-name.md          # project scope (committed to repo)
```

The filename must match the `name` frontmatter field. Example:

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

Each agent with a `memory` field gets its own `MEMORY.md`. The first 200 lines are auto-injected into the agent's context at startup.

| Scope | Path | Git |
|-------|------|-----|
| `user` | `~/.claude/agent-memory/<name>/MEMORY.md` | Outside repo |
| `project` | `.claude/agent-memory/<name>/MEMORY.md` | Committed — shared with developer team |
| `local` | `.claude/agent-memory-local/<name>/MEMORY.md` | Gitignored — personal to developer |

`Read`, `Write`, and `Edit` tools are auto-enabled when memory is set, even if not listed in `tools`.

### Skills

Skills are global — not agent-scoped. Agents reference them by name; the content is injected at startup.

```
~/.claude/skills/<name>/SKILL.md      # user scope
.claude/skills/<name>/SKILL.md        # project scope
```

Skills support nested directories (unlike agents).

### Hooks

Two kinds:

1. **Inline hooks** — defined in agent frontmatter, scoped to agent lifetime
2. **Global hooks** — defined in `settings.json`, run for the entire session

Global hooks also support `SubagentStart` and `SubagentStop` events for reacting to subagent lifecycle.

### Other Definition Methods

Agents can also be defined via:

- `claude --agent <name>` — run a session as a specific agent
- `claude --agents '<json>'` — inline JSON definitions (session only, not persisted)
- `"agent"` field in `settings.json` — set a default agent for a project
- `/agents` interactive UI — create/manage agents

### Invocation

| Method | Who | When |
|--------|-----|------|
| `claude --agent name` | Developer (CLI) | Session start — becomes the root agent |
| `@agent-name` in prompt | Developer (interactive) | Mid-session — forces delegation to named agent |
| Agent tool (`subagent_type`) | Agent (programmatic) | Mid-session — one agent spawns another |
| Natural language | Developer or agent | Mid-session — Claude auto-delegates |

Subagents cannot spawn other subagents (no recursive Agent tool).

### Priority

When multiple scopes define the same agent name:

1. `--agents` CLI flag (highest)
2. `.claude/agents/` (project)
3. `~/.claude/agents/` (user)
4. Plugin agents (lowest)

## Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in kordinate's format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

### Claude Code

Claude Code reads from `~/.claude/`. Some files are direct copies:

| `~/.claude/` | `~/.kord/` | Transform |
|-------------|-----------|-----------|
| `settings.json` | `settings.json` | copy |
| `.mcp.json` | `mcp.json` | rename |
| `keybindings.json` | `keybindings.json` | copy |

These require linking:

| `~/.claude/` | Purpose | `~/.kord/` source | Transform |
|-------------|---------|-------------------|-----------|
| `CLAUDE.md` | Root system prompt — inherited by all subagents | `root/identity.md` + `team/manifest.md` | rename + merge |
| `agents/<name>.md` | Subagent identity | `<agent>/identity.md` | rename, generate frontmatter |
| `commands/*.md` | Slash commands | `root/commands/*.md` | copy |
| `agent-memory/<name>/` | Agent writable memory | `<agent>/memory/` | restructure |

No symlinks. Claude Code works with real files. `~/.kord/` is the portable format.

### How Linking Works

1. Read each file in `~/.kord/`
2. Check frontmatter for memory properties (structured, on-demand, owner, scope, expiry)
3. Apply defaults where no frontmatter exists
4. Transform and copy to the paths the runtime expects

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
