# Link

Level 3 resource for the register and install skills.

Link kordinate state to the Claude Code runtime. Scribe owns this procedure — it understands both kordinate's recall system and the runtime's native filesystem.

Useful after: first install, adding an agent, updating kordinate files, or a Claude Code update.

See [claude-native.md](../remember/claude-native.md) for the runtime's paths.

## Procedure

### Agents

**Dev-mode source resolution**: If `$KORDINATE_HOME/.dev-source` exists, read its contents to get the dev repo path. For each agent, check whether `<dev-repo-path>/kordinate/agents/<name>/` exists -- if so, it is a package agent and its `IDENTITY.md` and `memory/` should be read from the dev repo path instead of `$KORDINATE_HOME`. User-created agents (those not present in the dev repo's `kordinate/agents/` directory) continue to resolve from `$KORDINATE_HOME` as normal.

For each agent in `$KORDINATE_HOME/agents/`:

1. Read `IDENTITY.md`
2. **Subagents** (have `tools:` in frontmatter):
   - Write to `~/.claude/agents/<name>.md` — strip recall properties (`curated`, `preloaded`) from frontmatter, keep Claude fields (`name`, `description`, `tools`, `model`, `color`, `memory`)
   - Create `~/.claude/agent-memory/<name>/MEMORY.md` — an **index** (not a copy) that points to the actual memory files at `$KORDINATE_HOME/agents/<name>/memory/`. For each memory file, read its frontmatter `description` and add an entry: `- [filename](absolute-path) — description`. The 200-line limit applies to this index, not to the underlying files.
   - Copy agent skills to `~/.claude/skills/` (entire directory including Level 3 resources)
3. **Main session** (no `tools:` in frontmatter, e.g. `main`):
   - Do NOT write to `~/.claude/agents/` (not a subagent)
   - Do NOT create `~/.claude/agent-memory/` index (main session uses auto-memory)
   - Surface kordinate memories by adding `@` imports to `~/.claude/CLAUDE.md` for each `.md` file in `$KORDINATE_HOME/agents/main/memory/`

### Global Skills

Copy from `$KORDINATE_HOME/skills/` to `~/.claude/skills/`:

- `boot/`
- `kord/`
- `authenticate/`
- `merge/`
- `install/`
- `improve/`

### Binaries

Copy from `$KORDINATE_HOME/bin/` to the runtime. These are user-facing scripts (session management, import/export, config hydration).

Ensure `$KORDINATE_HOME/bin/` is in PATH — typically via `/kord/kordinate/bin` symlink or shell RC entry.

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

### Guard and Hooks

Merge hooks from `$KORDINATE_HOME/settings.json` into `~/.claude/settings.json`:

1. Read existing `~/.claude/settings.json` (preserve user-specific settings like `extraKnownMarketplaces`)
2. Set `env.KORDINATE_HOME` to the absolute path of `$KORDINATE_HOME`
3. Replace the `hooks` section with the one from `$KORDINATE_HOME/settings.json`, expanding `$KORDINATE_HOME` to the absolute path

This installs:
- **Unified guard** (`hooks/guard.sh`) on Write|Edit|Bash and mcp\_\_grafana — enforces scribe, deployer, sauron, and merge rules
- **Subagent invocation gate** (`hooks/subagent-invocation-gate.sh`) on Agent — blocks direct spawning of kordinate agents, redirects to `/kord`

### KORD.md

Run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

## Report

List what was linked: agents, skills, kords, CLAUDE.md, guard status.
