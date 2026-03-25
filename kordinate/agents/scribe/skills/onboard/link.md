# Link

Level 3 resource for the onboard and install skills.

Link kordinate state to the Claude Code runtime. Scribe owns this procedure — it understands both kordinate's recall system and the runtime's native filesystem.

Useful after: first install, adding an agent, updating kordinate files, or a Claude Code update.

See [claude-native.md](../remember/claude-native.md) for the runtime's paths.

## Procedure

### Agents

For each agent in `$KORDINATE_HOME/agents/`:

1. Read `IDENTITY.md`
2. Write to `~/.claude/agents/<name>.md` — strip kordinate properties (`curated`, `preloaded`, `scope`) from frontmatter, keep Claude fields (`name`, `description`, `tools`, `model`, `color`, `memory`)
3. Create `~/.claude/agent-memory/<name>/MEMORY.md` — an **index** (not a copy) that points to the actual memory files at `$KORDINATE_HOME/agents/<name>/memory/`. For each memory file, read its frontmatter `description` and add an entry: `- [filename](absolute-path) — description`. The 200-line limit applies to this index, not to the underlying files.
4. Copy agent skills to `~/.claude/skills/` (entire directory including Level 3 resources)

### Global Skills

Copy from `$KORDINATE_HOME/skills/` to `~/.claude/skills/`:

- `boot/`
- `kord/`
- `authenticate/`
- `merge/`
- `install/`

### Kords

For stateless kords: ensure the borrowed skill exists in `~/.claude/skills/` (Claude discovers it globally).

### CLAUDE.md

Ensure `~/.claude/CLAUDE.md` contains:

```
Run /boot before starting work.

@~/.kord/shared/memory-protocol.md
@~/.kord/shared/auth-protocol.md
@~/.kord/shared/credentials-protocol.md
```

### Guard

Ensure `~/.claude/settings.json` has the PreToolUse hook for the memory guard.

### KORD.md

Run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

## Report

List what was linked: agents, skills, kords, CLAUDE.md, guard status.
