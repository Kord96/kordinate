# Claude Code Checklist

Level 3 resource for the onboard skill. Verify after onboarding or syncing.

## Kordinate Source (~/.kord/)

- [ ] `$KORDINATE_HOME/agents/<name>/IDENTITY.md` exists with frontmatter (name, description, tools, model, curated, preloaded, scope)
- [ ] `$KORDINATE_HOME/agents/<name>/memory/scratchpad.md` exists (curated: false, scope: global)
- [ ] `$KORDINATE_HOME/kords/<name>-default/contract.md` exists for each agent
- [ ] `$KORDINATE_HOME/shared/memory-protocol.md` exists (preloaded: all)
- [ ] `$KORDINATE_HOME/shared/auth-protocol.md` exists (preloaded: all)
- [ ] `$KORDINATE_HOME/KORD.md` is current — run `generate-kord.sh` if needed

## Claude Native (~/.claude/)

### Per Agent

- [ ] `~/.claude/agents/<name>.md` exists
- [ ] Frontmatter has: `name`, `description`, `tools`, `model`
- [ ] Frontmatter has `memory: user` (enables native global memory as fallback)
- [ ] Markdown body matches kordinate IDENTITY.md body
- [ ] Agent skills copied to `~/.claude/skills/<name>/` (if any)

### Kord Wiring

- [ ] Stateless kords: borrowed skill listed in each requester agent's `skills:` frontmatter in `~/.claude/agents/<name>.md`
- [ ] Stateful kords: Beorn MCP server running and registered in `.mcp.json`

### Shared

- [ ] `~/.claude/CLAUDE.md` contains `Run /boot before starting work.`
- [ ] `preloaded: all` files `@imported` in `~/.claude/CLAUDE.md`:
    ```
    @~/.kord/shared/memory-protocol.md
    @~/.kord/shared/auth-protocol.md
    ```
- [ ] Global skills copied to `~/.claude/skills/`:
    - `boot/SKILL.md`
    - `kord/SKILL.md`
    - `authenticate/SKILL.md`
    - `merge/SKILL.md`
- [ ] Guard hook registered in `~/.claude/settings.json` as **PreToolUse** (not PostToolUse):
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

## Project Level (.kord/)

- [ ] `.kord/` directory exists in project root (if project-scoped memory is needed)

## Quick Test

- [ ] `/boot` loads shared protocols and agent memory without errors
- [ ] `/kord <agent> test` reaches the agent (stateful) or runs skill (stateless)
- [ ] Writing to `~/.kord/` without scribe auth is blocked by guard
- [ ] `/kord remember test note` writes to kordinate + Claude native paths
- [ ] `generate-kord.sh` produces valid KORD.md
