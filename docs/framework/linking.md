# Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

## Kordinate

Every agent follows the same layout:

```
~/.kord/
├── team/
│   └── manifest.md              # agent roster and shared rules
├── <agent>/
│   ├── identity.md              # role, tools, auth, workflow, rules
│   ├── skills/<name>/SKILL.md   # per-agent skill definitions
│   └── memory/
│       ├── index.md             # on-demand file listing
│       └── *.md                 # domain knowledge, notes
├── kords/
│   ├── index.md                 # available kords directory
│   ├── <kord>/contract.md       # consultation protocol
│   └── <kord>/data.md           # cached results with expiry
├── settings.json                # permissions, hooks, env vars
└── mcp.json                     # MCP server configuration
```

## Claude Code

Claude Code reads from two scopes: `~/.claude/` (user — all projects) and `.claude/` (project — committed to repo). The linker targets user scope.

| Path | Purpose |
|------|---------|
| `~/.claude/CLAUDE.md` | Global system prompt — inherited by all subagents |
| `~/.claude/agents/<name>.md` | Subagent identity — flat file, YAML frontmatter + markdown body |
| `~/.claude/agent-memory/<name>/MEMORY.md` | Agent memory — first 200 lines auto-injected at startup; beyond 200, agent is nudged to curate but lines are not loaded unless explicitly instructed |
| `~/.claude/projects/<project>/memory/MEMORY.md` | Auto memory — Claude writes this itself; main session's accumulated knowledge. First 200 lines auto-loaded, topic files on-demand |
| `~/.claude/rules/*.md` | Path-scoped rules — conditional instructions that load when Claude works with matching file globs |
| `~/.claude/skills/<name>/SKILL.md` | Skills — injected into agent context by name reference. Also invocable as `/name` slash commands |
| `~/.claude/settings.json` | Permissions, hooks, env vars |
| `~/.claude/.mcp.json` | MCP server configuration |
| `~/.claude/keybindings.json` | Keyboard shortcuts |

??? example "Examples"

    ??? example "Agent file — `~/.claude/agents/scribe.md`"

        ```markdown
        ---
        name: scribe
        description: Documentation specialist. Use for docs audits, page creation, and style enforcement.
        tools: Read, Write, Edit, Grep, Glob, Bash
        model: sonnet
        memory: project
        skills:
          - docs-style
        hooks:
          PostToolUse:
            - matcher: "Write|Edit"
              hooks:
                - type: command
                  command: "./scripts/lint-docs.sh"
        ---

        You are the scribe — the team's documentation agent.
        Maintain docs accuracy, enforce style, and keep pages current.
        ```

    ??? example "Agent memory — `~/.claude/agent-memory/scribe/MEMORY.md`"

        ```markdown
        # Scribe Memory

        - Docs site uses MkDocs Material with slate theme
        - Navigation defined in mkdocs.yml, not auto-generated
        - Admonitions and collapsibles are enabled
        - Keep pages concise — no verbose explanations
        ```

        First 200 lines are auto-injected. Beyond that, the agent is nudged to curate.

    ??? example "Skill — `~/.claude/skills/docs-style/SKILL.md`"

        ```markdown
        ---
        name: docs-style
        description: Documentation style conventions for the project
        ---

        - Use sentence case for headings
        - No emoji unless requested
        - Tables over bullet lists for structured data
        - Code blocks must specify language
        ```

        Referenced by name in agent frontmatter (`skills: [docs-style]`). Content injected at startup. Also invocable as `/docs-style`.

### Differences

| | Kordinate | Claude Code |
|---|---|---|
| **Hierarchy** | No hierarchy — any agent can be root or subagent | Fixed hierarchy — one main session, subagents below it |
| **Identity** | Every agent has `<agent>/identity.md`, same format whether root or sub | Main session has no identity file; subagents defined at `agents/<name>.md` |
| **Shared context** | `team/manifest.md` — explicit team-level file, independent of any agent | `CLAUDE.md` — inherited from main session to all subagents |
| **Memory model** | Agent-owned folders with explicit `index.md`, per-file properties (structured, on-demand, expiry) via frontmatter | Main session: auto memory (Claude writes for itself). Subagents: single `MEMORY.md`, 200-line preload, no index, no expiry |
| **Memory lifecycle** | Expiry property — files can declare staleness via scripts or markdown | No expiry — memory grows indefinitely, agent nudged to curate at 200 lines |
| **Structure enforcement** | `structured` property + guards restrict who can write structured files | No enforcement — all memory is freeform markdown |
| **Skills** | Per-agent: `<agent>/skills/*.md` — scoped to the owning agent | Global: `skills/<name>/SKILL.md` — available to all agents by name reference |
| **Rules** | No separate concept — instructions live in identity or team manifest | `rules/*.md` — path-scoped, load conditionally on file glob match |
