Update a subagent's project-local memory at `.claude/agent-memory/<name>/` in the current repo.

**Input**: $ARGUMENTS (expect: agent name and the memory content to write)

## Steps

1. Confirm the agent exists: check `~/.claude/agents/<name>/` directory
2. Read the current contents of `.claude/agent-memory/<name>/` in the project root (create directory if missing)
3. Write the provided content as a memory file in that directory, following the memory format:
   ```markdown
   ---
   name: <memory name>
   description: <one-line description>
   type: <user|feedback|project|reference>
   ---

   <memory content>
   ```
4. Stage and commit the file — project-local memory is git-tracked

## When to use this vs update-subagent-memory

- **This command** (`update-project-agent-memory`): For knowledge specific to the current project/repo. Git-tracked, shared across sessions on this repo. Examples: debug reference tables, project-specific workflows, repo-specific operational notes.
- **`update-subagent-memory`**: For global agent knowledge that applies across all projects. Lives at `~/.claude/agent-memory/`, not git-tracked. Examples: general operational notes, cross-project workarounds.

## Restrictions

- Only edit files under `.claude/agent-memory/<name>/` in the project root
- Never modify the agent's CLAUDE.md or other files
- Content must be stable and actionable — no deployment history, no point-in-time facts
- Session-ephemeral state belongs in `.claude/agent-state/<name>.json`, NOT in memory
