# Claude Code Checklist

Level 3 resource for the onboard skill. Verify after onboarding or syncing.

## Kordinate Source ($KORDINATE_HOME)

- [ ] `agents/<name>/IDENTITY.md` exists with:
    - Kordinate properties: `curated`, `preloaded: <name>`, `scope: global`
    - Claude fields: `name`, `description`, `tools`, `model`, `color`, `memory`
- [ ] `agents/<name>/memory/scratchpad.md` exists (`curated: false`, `scope: global`)
- [ ] `kords/<name>-default/contract.md` exists (if agent has kord expertise)
- [ ] `shared/memory-protocol.md` exists (`preloaded: all`)
- [ ] `shared/auth-protocol.md` exists (`preloaded: all`)
- [ ] `KORD.md` is current — run `generate-kord.sh` if needed

## Claude Native (~/.claude/)

### Per Agent

- [ ] `~/.claude/agents/<name>.md` exists
- [ ] Frontmatter: `name`, `description`, `tools`, `model`
- [ ] Frontmatter: `memory: user` (fallback — boot handles full 2D memory)
- [ ] Markdown body matches kordinate IDENTITY.md body
- [ ] Agent skills directory copied to `~/.claude/skills/<name>/` including Level 3 resources (not just SKILL.md)

### Kords

- [ ] Stateless kords: borrowed skills exist in `~/.claude/skills/` (Claude discovers them globally — no `skills:` frontmatter needed)
- [ ] Stateful kords: Beorn MCP server running and registered in `~/.claude/.mcp.json`

### Shared

- [ ] `~/.claude/CLAUDE.md` contains `Run /boot before starting work.`
- [ ] `preloaded: all` files `@imported` in `~/.claude/CLAUDE.md` (survives compaction):
    ```
    @~/.kord/shared/memory-protocol.md
    @~/.kord/shared/auth-protocol.md
    ```
- [ ] Global skills copied to `~/.claude/skills/` (with Level 3 resources):
    - `boot/` (SKILL.md + claude-session-structure.md)
    - `kord/` (SKILL.md)
    - `authenticate/` (SKILL.md)
    - `merge/` (SKILL.md)
- [ ] Guard hook in `~/.claude/settings.json` as **PreToolUse**:
    ```json
    {
      "hooks": {
        "PreToolUse": [
          {
            "matcher": "Write|Edit",
            "hooks": [
              {
                "type": "command",
                "command": "$KORDINATE_HOME/agents/scribe/skills/remember/guard.sh"
              }
            ]
          }
        ]
      }
    }
    ```

## Project Level

- [ ] `.kord/` exists in project root (if project-scoped memory is needed)

## Quick Test

- [ ] `/boot` loads shared protocols and agent memory without errors
- [ ] `/kord deployer what pods are running?` reaches deployer (stateful test)
- [ ] `/kord remember checklist verification note` writes successfully (stateless test)
- [ ] Attempt to write directly to `~/.kord/agents/scribe/memory/test.md` — should be blocked by guard
- [ ] `generate-kord.sh` produces valid KORD.md with all agents and kords listed
