# Claude Code Checklist

Level 3 resource for the onboard skill. Verify after onboarding or syncing.

## Per Agent

- [ ] `~/.claude/agents/<name>.md` exists with correct frontmatter (`name`, `description`, `tools`, `model`, `memory`)
- [ ] Frontmatter `description` matches kordinate IDENTITY.md description
- [ ] Markdown body matches kordinate IDENTITY.md body
- [ ] `memory: user` set in frontmatter (for global persistence)
- [ ] `~/.claude/agent-memory/<name>/` directory exists
- [ ] Agent skills copied to `~/.claude/skills/<name>/` (if any)

## Kords

- [ ] Stateless kords: borrowed skills listed in requester agents' `skills:` frontmatter
- [ ] Stateful kords: Beorn MCP server is running and registered

## Shared

- [ ] `~/.claude/CLAUDE.md` contains `Run /boot before starting work.`
- [ ] `preloaded: all` files are `@imported` in `~/.claude/CLAUDE.md`
- [ ] Global skills (boot, kord, authenticate, merge) copied to `~/.claude/skills/`
- [ ] Guard hook registered in `~/.claude/settings.json`:
  ```json
  {
    "hooks": {
      "PostToolUse": [
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

## Quick Test

- [ ] `/boot` runs without errors
- [ ] `/kord <agent> test` spawns the agent or runs borrowed skill
- [ ] Writing to `~/.kord/` without scribe auth is blocked by guard
