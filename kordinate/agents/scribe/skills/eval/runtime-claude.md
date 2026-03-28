# Runtime Checks: Claude Code

Level 3 resource for the eval skill (health mode). Checks specific to the Claude Code runtime. These verify that kordinate is correctly linked to `~/.claude/`.

Separate from structural health checks so kordinate can support other runtimes in the future without modifying the core checks.

## MEMORY.md sync

For each agent's runtime MEMORY.md (`~/.claude/agent-memory/<name>/MEMORY.md`), verify two-way consistency:

- **Broken link** — every entry in MEMORY.md references a target file path. That file must exist on disk.
    - Severity: **ERROR**
- **Missing entry** — every memory file in the agent's kordinate memory directory should have a corresponding entry in MEMORY.md.
    - Severity: **WARNING**

## MEMORY.md purity

MEMORY.md files must be pure indexes — a list of links to memory files with one-line descriptions. They must not contain:

- Inline memory content (more than one sentence per entry)
- Lifecycle instructions (boot sequences, load-order directives, preload lists)
- Agent identity or behavioral instructions

Severity:
- **WARNING** — MEMORY.md contains lifecycle instructions or inline content

## Agent-runtime alignment

Verify that kordinate agent definitions and runtime agent registrations are in sync:

- **Runtime agent file exists** — every agent directory under `$KORDINATE_HOME/agents/` (except `main`) must have a corresponding `~/.claude/agents/<name>.md`.
    - Severity: **ERROR**
- **Agent memory directory exists** — every agent must have `~/.claude/agent-memory/<name>/` with a MEMORY.md.
    - Severity: **WARNING**
- **Name consistency** — the `name` field in `~/.claude/agents/<name>.md` must match the `name` in `$KORDINATE_HOME/agents/<name>/IDENTITY.md`.
    - Severity: **ERROR**
- **No kordinate properties in runtime** — `~/.claude/agents/<name>.md` should not have `curated`, `preloaded`, or `scope` in frontmatter (those are kordinate-only).
    - Severity: **WARNING**

## Hook validation

Verify that hooks registered in `~/.claude/settings.json` are correctly configured:

- **Hook file exists** — every `command` path referenced in hooks must resolve to an existing file.
    - Severity: **ERROR**
- **Hook is executable** — each referenced hook script must have the executable bit set (`-x`).
    - Severity: **ERROR**
- **KORDINATE_HOME set** — `env.KORDINATE_HOME` in settings.json must point to an existing directory.
    - Severity: **ERROR**

## CLAUDE.md integrity

Verify `~/.claude/CLAUDE.md` contains expected content:

- **Boot instruction** — contains "Run /boot before starting work": **WARNING** if missing
- **Shared protocol imports** — `@` imports for memory-protocol.md, auth-protocol.md, credentials-protocol.md all resolve to existing files: **ERROR** if broken

## Skills linked

Verify that kordinate skills are available in the runtime:

- **Global skills** — boot, kord, authenticate, merge, install-k should exist in `~/.claude/skills/`: **ERROR** if missing
- **Agent skills** — each agent's skills should exist in `~/.claude/skills/`: **WARNING** if missing
