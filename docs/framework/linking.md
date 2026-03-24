# Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

## Kordinate

```
~/.kord/
├── MAP.md                          # router — auto-generated from frontmatter
├── team/
│   ├── memory/*.md                 # shared conventions, standards
│   └── kords/
│       └── <kord>/
│           ├── contract.md         # consultation protocol
│           └── data.md             # cached results with expiry
├── <agent>/                            # general, scribe, deployer, etc.
│   ├── identity.md                 # role, tools, workflow, rules
│   ├── skills/<name>/SKILL.md      # per-agent skills
│   └── memory/*.md                 # domain knowledge, notes
├── settings.json                   # permissions, hooks, env vars
└── .mcp.json                       # MCP server configuration
```

Every agent has the same structure. `general` is the default main session agent.

## Claude Code

Claude Code reads from `~/.claude/` (user scope) and `.claude/` (project scope). The linker targets user scope.

### Direct Copy

No transformation needed.

| Source | Target |
|--------|--------|
| `settings.json` | `~/.claude/settings.json` |
| `.mcp.json` | `~/.claude/.mcp.json` |
| `<agent>/skills/` | `~/.claude/skills/<agent>/` |

### Remaining

These require thoughtful linking — they don't map 1:1 from kordinate.

=== "Main Agent"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/CLAUDE.md` | Loaded into every session and inherited by all subagents. Developer-written instructions, not agent-generated. |
    | auto memory | `~/.claude/projects/<project>/memory/MEMORY.md` | Claude writes this itself as it works. First 200 lines auto-loaded at startup. Claude keeps this concise as a router: each line links to a topic file with a one-line description. Detailed notes go into topic files (e.g. `debugging.md`) in the same directory — Claude reads those on-demand. Same pattern as kordinate's `MAP.md`. |

=== "Subagents"

    | File | Path | Description |
    |------|------|-------------|
    | system prompt | `~/.claude/agents/<name>.md` | Flat markdown file with YAML frontmatter (`name`, `description`, `tools`, `model`, `memory`, `hooks`, etc.) and markdown body as system prompt. |
    | auto memory | `~/.claude/agent-memory/<name>/MEMORY.md` | Single file, first 200 lines auto-injected at startup. Beyond 200, agent is nudged to curate but lines are not loaded unless explicitly instructed. No topic files. |
