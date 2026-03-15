Update a subagent's native memory at `~/.claude/agent-memory/<name>/`.

**Input**: $ARGUMENTS (expect: agent name and the memory content to write)

## Steps

1. Confirm the agent exists: check `~/.claude/agents/<name>/` directory
2. Read the current contents of `~/.claude/agent-memory/<name>/` (create directory if missing)
3. Write the provided content as a memory file in that directory, following the native memory format:
   ```markdown
   ---
   name: <memory name>
   description: <one-line description>
   type: <user|feedback|project|reference>
   ---

   <memory content>
   ```
4. No commit needed — agent-memory lives at `~/.claude/`, not in git

## Restrictions

- Only edit files under `~/.claude/agent-memory/<name>/`
- Never modify the agent's CLAUDE.md or other files
- Operational notes must be stable and actionable — no deployment history (use changelog), no point-in-time facts that go stale, nothing derivable from git log or live queries
- Session-ephemeral state (session_id, last_line, last_commit, last_changelog_line, context_summary) belongs in `.claude/agent-state/<name>.json`, NOT in memory
