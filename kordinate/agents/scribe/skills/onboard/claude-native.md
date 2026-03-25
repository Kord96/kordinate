# Claude Code Native Agent File

Level 3 resource for the onboard skill.

## Mapping

When onboarding an agent, create both:
1. `agents/<name>/identity.md` — kordinate's portable format
2. `~/.claude/agents/<name>.md` — Claude Code's native format

The Claude native file uses the same frontmatter as identity.md. The markdown body becomes the agent's system prompt.

## Claude Native Path

`~/.claude/agents/<name>.md`

The filename must match the `name` field in frontmatter. Flat file, not a directory.

## What Claude Does With It

- Discovered at session start (restart required if added mid-session)
- Spawnable via `@agent-name` mention or programmatically via the Agent tool
- Frontmatter controls: tools, model, memory scope, hooks, skills
- Markdown body becomes the subagent's system prompt
- Subagent does NOT inherit CLAUDE.md, rules, or parent skills
