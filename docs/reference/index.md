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

Key behaviors:

- Auto memory is always per-project. No global auto memory exists.
- `~/.claude/CLAUDE.md` is developer-written and curated — Claude does not auto-write to it.
- Subagents do **not** inherit CLAUDE.md, rules, skills, or conversation history from the parent session.
- Subagents start with only: their own system prompt (markdown body), basic environment details (working directory), inherited MCP servers, and inherited permissions.
- To give a subagent knowledge, you must: write it in the agent's body, list skills in `skills:` frontmatter, or enable `memory:` for persistent MEMORY.md.
