# Integration

Kordinate lives inside the runtime's native structure — no separate filesystem, no linker. It adds three things:

1. **`kord/MAP.json`** — registry of all knowledge and its properties
2. **A skill** — generates MAP.json by scanning files and reading frontmatter
3. **A guard** — enforces templates on writes by checking MAP.json

## Claude Code

Kordinate files live alongside Claude Code's native files:

```
~/.claude/                              # user scope
├── CLAUDE.md                           # system prompt
├── agents/<name>.md                    # subagent identities
├── agent-memory/<name>/MEMORY.md       # subagent auto memory
├── skills/<agent>/<name>/SKILL.md      # agent skills
├── settings.json                       # permissions, hooks, env vars
├── .mcp.json                           # MCP server configuration
├── projects/<project>/memory/          # main session auto memory
└── kord/
    ├── MAP.json                        # global knowledge registry
    └── <kord-name>/
        ├── contract.md                 # consultation protocol
        └── data.md                     # cached result

.claude/                                # project scope
└── kord/
    ├── MAP.json                        # project knowledge registry
    └── <kord-name>/
        ├── contract.md
        └── data.md
```

Everything outside `kord/` is native Claude Code. Everything inside `kord/` is kordinate. The guard merges both MAP.json files when checking writes.

### Claude Code Native

These files are managed by Claude Code natively. Kordinate's MAP.json tracks them but doesn't create or modify them.

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/CLAUDE.md` | Loaded into every session and inherited by all subagents. Developer-written. |
    | auto memory | `~/.claude/projects/<project>/memory/MEMORY.md` | Claude writes this itself. First 200 lines auto-loaded at startup. Acts as router to topic files in the same directory. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`) + markdown body as system prompt. |
    | auto memory | `~/.claude/agent-memory/<name>/MEMORY.md` | Single file, first 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate. No topic files. |
