# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

Claude Code has no global auto memory. Auto memory is always per-project. `~/.claude/CLAUDE.md` is developer-written and curated — Claude does not auto-write to it.

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/CLAUDE.md` | Loaded into every session and inherited by all subagents. Developer-written. |
    | auto memory index | `~/.claude/projects/<project>/memory/MEMORY.md` | Per-project. Claude writes this itself. First 200 lines auto-loaded at startup. Acts as router to topic files. |
    | auto memory files | `~/.claude/projects/<project>/memory/*.md` | Per-project. Topic files — Claude reads these on-demand when it needs the information. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`) + markdown body as system prompt. |
    | auto memory index | `~/.claude/agent-memory/<name>/MEMORY.md` | First 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate. May support topic files (same architecture as main session). |
