# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

Key behaviors ([source](https://code.claude.com/docs/en/sub-agents)):

=== "Main Session"

    - **Spawn prompt**: `~/.claude/CLAUDE.md` — developer-written and curated. Claude does not auto-write to it unless explicitly asked.
    - **Auto memory**: `~/.claude/projects/<project>/memory/` — Claude writes this itself. Per-project only, no global auto memory.
    - `MEMORY.md` acts as an index — each line links to a topic file. First 200 lines auto-loaded at startup.
    - Topic files (`*.md`) in the same directory hold detailed notes, read on-demand.

=== "Subagents"

    - **Spawn prompt**: `~/.claude/agents/<name>.md` — YAML frontmatter + markdown body.
    - **Auto memory**: `~/.claude/agent-memory/<name>/MEMORY.md` — only if `memory:` is set. First 200 lines auto-injected. No topic files.
    - Start with only: own system prompt, environment details, inherited MCP servers and permissions.
    - No CLAUDE.md, no conversation history, no rules, no skills unless listed in `skills:` frontmatter.
    - Context isolation — parent receives a summary, not the subagent's full exploration.
