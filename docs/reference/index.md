# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/CLAUDE.md` | Loaded into every session and inherited by all subagents. Developer-written. |
    | auto memory index | `~/.claude/projects/<project>/memory/MEMORY.md` | Per-project. Claude writes this itself. First 200 lines auto-loaded at startup. Acts as router to topic files. |
    | auto memory files | `~/.claude/projects/<project>/memory/*.md` | Per-project. Topic files — Claude reads these on-demand when it needs the information. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`, `skills`) + markdown body as system prompt. |
    | auto memory | `~/.claude/agent-memory/<name>/MEMORY.md` | Only if `memory:` is set in frontmatter. First 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate. |

Key behaviors ([source](https://code.claude.com/docs/en/sub-agents)):

- Auto memory is always per-project. No global auto memory exists.
- `~/.claude/CLAUDE.md` is developer-written and curated — Claude does not auto-write to it.
- "Subagents receive only this system prompt (plus basic environment details like working directory), not the full Claude Code system prompt." — no CLAUDE.md, no conversation history.
- "Subagents don't inherit skills from the parent conversation; you must list them explicitly" via `skills:` frontmatter.
- Subagents do inherit MCP servers and permissions from the parent session.
- Subagent can explore dozens of files without any of that content accumulating in the main conversation. The parent receives a concise summary, not every file the subagent read.
- To give a subagent knowledge: write it in the agent's body, list skills in `skills:`, or enable `memory:` for persistent MEMORY.md.
