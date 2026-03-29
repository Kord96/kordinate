# Link

Level 3 resource for the register and install skills.

Link kordinate to the Claude Code runtime. Wipes stale files before copying to prevent drift.

## Procedure

### 0. Backup and wipe

**Backup** (if `~/.claude/agents/` or `~/.claude/skills/` exist):
```bash
tar czf ~/.kord/backups/claude-runtime-$(date +%Y%m%d-%H%M%S).tar.gz \
  ~/.claude/agents/ ~/.claude/skills/ ~/.claude/agent-memory/ 2>/dev/null
mkdir -p ~/.kord/backups
```

**Wipe runtime** (prevents stale files from previous installs):
```bash
rm -rf ~/.claude/agents/ ~/.claude/skills/
mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/agent-memory
```

**Preserve**:
- `~/.claude/agent-memory/` — don't wipe, update MEMORY.md indexes in place (Claude's native agent memory accumulates across sessions)
- `~/.claude/projects/` — user auto-memory (nudge hook + /remember moves files to kordinate)
- `~/.claude/settings.json` — user config (hooks section merged, not replaced)
- `~/.claude/CLAUDE.md` — will be rewritten

### 1. Agents

For each agent in `$KORDINATE_HOME/agents/` (except `main`):

1. Read `IDENTITY.md`
2. Write to `~/.claude/agents/<name>.md` — keep Claude fields (`name`, `description`, `tools`, `model`, `color`, `memory`), drop kordinate-only fields.
3. Create `~/.claude/agent-memory/<name>/MEMORY.md` — index pointing to memory files. Use descriptions from KORD.json entries (not frontmatter scanning). The 200-line limit applies.

**Main session** (no `tools:` in frontmatter):
- Do NOT write to `~/.claude/agents/`
- Surface kordinate memories by adding `@` imports to `~/.claude/CLAUDE.md`

### 2. Skills

**Team skills only** → copy to `~/.claude/skills/`:
```bash
cp -r $KORDINATE_HOME/team/skills/* ~/.claude/skills/
```

**Agent skills are NOT copied to `~/.claude/skills/`.** They are accessed via `/kord <agent> <skill>` — the kord MCP server routes based on KORD.json skill entries.

### 3. KORD.json

Assemble the global KORD.json:
```bash
python3 $KORDINATE_HOME/team/scripts/assemble-kord.py $KORDINATE_HOME
```

This merges all agent KORD.json + team/KORD.json into the global manifest.

### 4. CLAUDE.md

Write `~/.claude/CLAUDE.md`:
```
Run /boot before starting work.

@~/.kord/shared/memory-protocol.md
@~/.kord/shared/auth-protocol.md
@~/.kord/shared/credentials-protocol.md
@~/.kord/shared/gemini-protocol.md

@~/.kord/agents/main/memory/scratchpad.md
```

### 5. Hooks

Copy hooks to `$KORDINATE_HOME/hooks/`:
- `kord-guard.sh` — data-driven enforcement from KORD.json
- `agent-gate.sh` — subagent spawn control
- `auto-merge.sh` — merge session to main on commit/push

### 6. Settings

Merge hooks from `$KORDINATE_HOME/settings.json` into `~/.claude/settings.json`:

1. Read existing `~/.claude/settings.json` (preserve user settings)
2. Set `env.KORDINATE_HOME` to absolute path
3. Replace the `hooks` section with kordinate's hooks

### 7. Agent lock files

For each agent (except `main`), ensure a lock file at `$KORDINATE_HOME/profile/locks/<name>`:
```bash
mkdir -p "$KORDINATE_HOME/profile/locks"
for agent in "$KORDINATE_HOME"/agents/*/; do
  name=$(basename "$agent")
  [ "$name" = "main" ] && continue
  [ -f "$KORDINATE_HOME/profile/locks/$name" ] && continue
  head -c 16 /dev/urandom | md5sum | cut -d' ' -f1 > "$KORDINATE_HOME/profile/locks/$name"
done
```

### 8. MCP servers

Ensure `~/.claude.json` has the kord MCP server:
```json
{"mcpServers": {"kord": {"type": "http", "url": "http://kord.master.svc.cluster.local:3100/mcp"}}}
```

Read `~/.claude.json` first — only add/update `mcpServers.kord`. Off-cluster: use Tailscale endpoint.

### 9. Verify

Run the install checklist: [install-checklist.md](../../install/install-checklist.md)

## Report

Summary: agents linked, team skills copied, KORD.json assembled, hooks installed, backup location.
