# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

Key behaviors ([source](https://code.claude.com/docs/en/sub-agents)):

=== "Global CLAUDE.md"

    `~/.claude/CLAUDE.md`

    - Developer-written and curated — Claude does not auto-write to it unless explicitly asked.
    - Loaded into the main session only. Not inherited by subagents.

=== "Auto Memory"

    `~/.claude/projects/<project>/memory/`

    - Claude writes this itself as it works — not developer-written.
    - Per-project only. No global auto memory exists.
    - `MEMORY.md` acts as an index — each line links to a topic file. First 200 lines auto-loaded at startup.
    - Topic files (`*.md`) hold detailed notes, read on-demand.

=== "Subagents"

    `~/.claude/agents/<name>.md` + `~/.claude/agent-memory/<name>/MEMORY.md`

    - Start with only: own system prompt (markdown body), environment details, inherited MCP servers and permissions.
    - No CLAUDE.md, no conversation history, no rules, no skills unless listed in `skills:` frontmatter.
    - Auto memory only if `memory:` is set in frontmatter. First 200 lines auto-injected. No topic files.
    - Context isolation — parent receives a summary, not the subagent's full exploration.
