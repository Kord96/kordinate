# Claude Code Native Paths

Level 3 resource for the remember skill.

## Memory Paths

When writing a memory, also write to the Claude native path so Claude can auto-load it.

| Kordinate path | Claude native path | Notes |
|---|---|---|
| `~/.claude/kord/agents/<name>/memory/` | `~/.claude/agent-memory/<name>/MEMORY.md` | Global scope. Single file. First 200 lines auto-loaded on subagent spawn. |
| `.claude/kord/agents/<name>/memory/` | `.claude/agent-memory/<name>/MEMORY.md` | Project scope. Same behavior. |

## How Claude Uses MEMORY.md

- First 200 lines auto-injected into subagent context at startup (if `memory:` is set in agent frontmatter).
- Beyond 200 lines, the agent is nudged to curate but extra lines are not loaded.
- No topic files — Claude native subagent memory is a single flat file.
- The main session's auto memory at `~/.claude/projects/<project>/memory/` is separate and managed by Claude itself.

## What to Write to Claude Native

Since Claude's subagent memory is a single file with a 200-line soft limit, write a concise summary. The kordinate memory directory can have multiple detailed topic files; the Claude native MEMORY.md should be an index or condensed version.

## Main Session Memory

The main session's auto memory at `~/.claude/projects/<project>/memory/` is managed by Claude itself — do not write to it directly. It supports topic files and uses MEMORY.md as an index.
