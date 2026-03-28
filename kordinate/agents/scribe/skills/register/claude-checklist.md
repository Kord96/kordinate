# Claude Code Checklist

Level 3 resource for the register skill. Verify after registration or syncing.

## Structural Checks

These can be verified immediately — no session restart required.

### Kordinate Source ($KORDINATE_HOME)

- [ ] `agents/<name>/IDENTITY.md` exists with:
    - Recall properties: `curated`, `preloaded: <name>`
    - Claude fields: `name`, `description`, `tools`, `model`, `color`, `memory`
- [ ] `agents/<name>/memory/scratchpad.md` exists (`curated: false`)
- [ ] `agents/<provider>/kords/<name>-default/contract.md` exists (if agent has kord expertise)
- [ ] `shared/memory-protocol.md` exists (`preloaded: all`)
- [ ] `shared/auth-protocol.md` exists (`preloaded: all`)
- [ ] `shared/credentials-protocol.md` exists (`preloaded: all`)
- [ ] `KORD.md` is current — run `generate-kord.sh` if needed
- [ ] `KORD.json` is valid JSON and lists all agents and kords

### Claude Native (~/.claude/)

**Per Agent:**

- [ ] `~/.claude/agents/<name>.md` exists
- [ ] Frontmatter has Claude fields (`name`, `description`, `tools`, `model`) — no recall properties (`curated`, `preloaded`)
- [ ] Frontmatter: `memory: user` (fallback — boot handles full 2D memory)
- [ ] Markdown body matches kordinate IDENTITY.md body
- [ ] Agent skills copied to `~/.claude/skills/` (entire directory including Level 3 resources)

**Agent Memory:**

- [ ] `~/.claude/agent-memory/<name>/MEMORY.md` exists for each agent
- [ ] MEMORY.md is an **index** — contains links to `$KORDINATE_HOME/agents/<name>/memory/` files, not content copies
- [ ] Every link in MEMORY.md points to an existing file
- [ ] MEMORY.md is under 200 lines

**Kords:**

- [ ] Stateless kords: borrowed skills exist in `~/.claude/skills/`
- [ ] Stateful kords: Beorn MCP server registered in `.mcp.json` (local or project)

**Shared:**

- [ ] `~/.claude/CLAUDE.md` contains `Run /boot before starting work.`
- [ ] `preloaded: all` files `@imported` in `~/.claude/CLAUDE.md`:
    ```
    @~/.kord/shared/memory-protocol.md
    @~/.kord/shared/auth-protocol.md
    @~/.kord/shared/credentials-protocol.md
    ```
- [ ] Global skills copied to `~/.claude/skills/`:
    - `boot/` (SKILL.md + claude-session-structure.md)
    - `kord/` (SKILL.md)
    - `authenticate/` (SKILL.md)
    - `merge/` (SKILL.md)

**Guard:**

- [ ] `~/.claude/settings.json` has PreToolUse hook on `Write|Edit`
- [ ] Hook command points to `$KORDINATE_HOME/hooks/guard.sh`
- [ ] Guard blocks writes to `~/.kord/` without scribe auth
- [ ] Guard allows writes to `~/.kord/` with scribe auth (`/tmp/.scribe-auth`)
- [ ] Guard allows non-curated, non-templated files without auth

### Manifest

- [ ] `$KORDINATE_HOME/.manifest.json` exists
- [ ] Manifest `source` field is set (type, path/url)
- [ ] Manifest `runtime` field matches detected runtime
- [ ] All files listed in manifest exist on disk
- [ ] Manifest hashes match on-disk hashes for curated files

### Dev Mode (if active)

- [ ] `$KORDINATE_HOME/.dev-source` exists and points to a valid repo
- [ ] Dev repo contains `kordinate/` package directory
- [ ] Post-commit hook is installed in dev repo (`.git/hooks/post-commit` contains dev-sync)

### Project Level

- [ ] `.kord/` exists in project root (if project-scoped memory is needed)

## Runtime Checks

These require a live Claude session. Run [smoke-test.sh](smoke-test.sh) to verify, or test manually in a fresh session.

- [ ] **Subagent spawning** — each agent spawns and responds with correct identity
- [ ] **Boot** — `/boot` loads shared protocols and agent memory without errors
- [ ] **Stateless kord** — `/kord remember <note>` writes to correct paths
- [ ] **Stateful kord** — `/kord deployer <question>` spawns deployer and returns answer
- [ ] **Cache** — second stateful kord call returns `[cached]` when data is fresh
- [ ] **Cache invalidation** — removing `.valid` marker causes re-spawn on next call
- [ ] **Agent memory** — agents can read their own memory from kordinate paths
- [ ] **Memory index sync** — new memory written via `/remember` appears in both `~/.kord/` and `~/.claude/agent-memory/` MEMORY.md
- [ ] **Manifest integrity** — `manifest_update --dry-run` reports no unexpected drift
- [ ] **Guard enforcement** — direct write to curated kordinate file is blocked
- [ ] **Template enforcement** — templated files reject edits that remove required sections
