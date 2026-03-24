# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

Key behaviors ([source](https://code.claude.com/docs/en/sub-agents)):

=== "Global CLAUDE.md"

    `~/.claude/CLAUDE.md`

    - Developer-written and curated — Claude does not auto-write to it unless explicitly asked.
    - Loaded into the main session at startup. Persists across sessions.
    - Not inherited by subagents — they never see this file.
    - Acts as the main session's spawn prompt: project instructions, coding standards, behavioral guidance.

=== "Auto Memory"

    `~/.claude/projects/<project>/memory/`

    - Claude writes this itself as it works — not developer-written.
    - Per-project only. No global auto memory exists. All worktrees in the same git repo share one memory directory.
    - `MEMORY.md` acts as an index — each line links to a topic file with a description. First 200 lines auto-loaded at startup.
    - Topic files (`*.md`) hold detailed notes. Claude reads these on-demand when it needs the information.
    - Beyond 200 lines, Claude is nudged to curate — move details into topic files, keep MEMORY.md concise.
    - Subagents have a simpler version: single `MEMORY.md` at `~/.claude/agent-memory/<name>/MEMORY.md`, no topic files. Only created if `memory:` is set in the agent's frontmatter.

=== "Subagents"

    `~/.claude/agents/<name>.md`

    - Defined as a flat markdown file: YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`, `skills`) + markdown body as spawn prompt.
    - Start with only: own spawn prompt, basic environment details (working directory), inherited MCP servers and permissions.
    - No CLAUDE.md, no conversation history, no rules, no parent skills — isolated context.
    - Skills must be listed explicitly in `skills:` frontmatter to be injected at startup.
    - Auto memory at `~/.claude/agent-memory/<name>/MEMORY.md` — only if `memory:` is set. First 200 lines auto-injected. No topic files.
    - Context isolation — parent receives a concise summary, not every file the subagent read or explored.
