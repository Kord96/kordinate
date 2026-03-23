# Linking

Kordinate is runtime-agnostic. Agent files live at `~/.kord/` in a portable format. The **linking layer** converts them to whatever the runtime expects — it's the only part that changes when switching runtimes.

## Claude Code

Claude Code reads from two scopes: `~/.claude/` (user — all projects) and `.claude/` (project — committed to repo). The linker targets user scope.

| Path | Purpose |
|------|---------|
| `~/.claude/CLAUDE.md` | Global system prompt — inherited by all subagents |
| `~/.claude/agents/<name>.md` | Subagent identity — flat file, YAML frontmatter + markdown body |
| `~/.claude/agent-memory/<name>/MEMORY.md` | Agent memory — first 200 lines auto-injected at startup; beyond 200, agent is nudged to curate but lines are not loaded unless explicitly instructed |
| `~/.claude/projects/<project>/memory/MEMORY.md` | Auto memory — Claude writes this itself; main session's accumulated knowledge. First 200 lines auto-loaded, topic files on-demand |
| `~/.claude/rules/*.md` | Path-scoped rules — conditional instructions that load when Claude works with matching file globs |
| `~/.claude/skills/<name>/SKILL.md` | Skills — injected into agent context by name reference |
| `~/.claude/commands/*.md` | Slash commands |
| `~/.claude/settings.json` | Permissions, hooks, env vars |
| `~/.claude/.mcp.json` | MCP server configuration |
| `~/.claude/keybindings.json` | Keyboard shortcuts |

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

    Referenced by name in agent frontmatter (`skills: [docs-style]`). Content injected at startup.

??? example "Slash command — `~/.claude/commands/audit-docs.md`"

    ```markdown
    ---
    description: Audit docs for broken links and stale content
    ---

    Scan all markdown files in docs/ for:
    1. Broken internal links
    2. References to removed features
    3. Outdated code examples

    Report findings as a table.
    ```

    Invoked by the developer as `/audit-docs` in the CLI.

### Adding a Runtime

To support a new runtime (Codex, Cursor, etc.), create a new link script that maps kordinate's structure to that runtime's expected paths. The `~/.kord/` files stay the same — only the linking changes.
