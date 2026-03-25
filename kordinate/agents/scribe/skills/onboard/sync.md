# Sync

Level 3 resource for the onboard skill.

When invoked with `/onboard sync`, sync all kordinate agents and skills to the runtime.

Useful after: first install, adding an agent manually, or switching runtimes.

See [claude-native.md](../remember/claude-native.md) for the current runtime's paths.

## Procedure

### Agents

For each agent in `$KORDINATE_HOME/agents/`:

1. Read `IDENTITY.md`
2. Write to `~/.claude/agents/<name>.md` — frontmatter + body
3. Create `~/.claude/agent-memory/<name>/` directory
4. Copy agent skills to `~/.claude/skills/<name>/` (entire directory including Level 3 resources)

### Global Skills

Copy from `$KORDINATE_HOME/skills/` to `~/.claude/skills/`:

- `boot/`
- `kord/`
- `authenticate/`
- `merge/`

### Kords

For stateless kords: ensure the borrowed skill exists in `~/.claude/skills/` (Claude discovers it globally).

### CLAUDE.md

Ensure `~/.claude/CLAUDE.md` contains:

```
Run /boot before starting work.

@~/.kord/shared/memory-protocol.md
@~/.kord/shared/auth-protocol.md
```

### Guard

Ensure `~/.claude/settings.json` has the PreToolUse hook for the memory guard.

### KORD.md

Run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

## Report

List what was synced: agents, skills, kords, CLAUDE.md, guard status.
