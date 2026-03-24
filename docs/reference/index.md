# Reference

- **[Patterns](patterns/index.md)** — recognized architectural patterns (designer)
- **[Libraries](libraries/index.md)** — shared libraries and third-party dependencies (designer)
- **[Source Map](source-map.md)** — maps doc pages to implementation sources (scribe)

## Claude Code

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | spawn prompt | `~/.claude/CLAUDE.md` | Loaded into the main session only. Developer-written. Not inherited by subagents. |
    | auto memory index | `~/.claude/projects/<project>/memory/MEMORY.md` | Per-project. Claude writes this itself. First 200 lines auto-loaded at startup. Acts as router to topic files. |
    | auto memory files | `~/.claude/projects/<project>/memory/*.md` | Per-project. Topic files — Claude reads these on-demand when it needs the information. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | spawn prompt | `~/.claude/agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`, `skills`) + markdown body as system prompt. |
    | auto memory | `~/.claude/agent-memory/<name>/MEMORY.md` | Only if `memory:` is set in frontmatter. First 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate. |

Key behaviors ([source](https://code.claude.com/docs/en/sub-agents)):

- **Global CLAUDE.md** (`~/.claude/CLAUDE.md`)
    - Developer-written and curated — Claude does not auto-write to it unless explicitly asked.
    - Loaded into the main session only. Not inherited by subagents.
- **Auto memory** (`~/.claude/projects/<project>/memory/`)
    - Claude writes this itself as it works — not developer-written.
    - Always per-project. No global auto memory exists.
    - Main agent uses `MEMORY.md` as an index — each line links to a topic file. Detailed notes go into separate `*.md` files in the same directory, read on-demand.
    - Subagents get a single `MEMORY.md` only — no topic files, no index pattern.
- **Subagents**
    - Receive only their own system prompt (markdown body) plus basic environment details — no CLAUDE.md, no conversation history, no rules.
    - Don't inherit skills from the parent conversation. Must be listed explicitly via `skills:` frontmatter.
    - Do inherit MCP servers and permissions from the parent session.
    - Can explore dozens of files without any of that content accumulating in the main conversation. The parent receives a concise summary, not every file the subagent read.
    - To give a subagent knowledge: write it in the agent's body, list skills in `skills:`, or enable `memory:` for persistent MEMORY.md.
