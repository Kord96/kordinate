Update a subagent's memory — either global or project-local.

**Input**: $ARGUMENTS (expect: agent name and the memory content to write)

## Location detection

This command handles both memory locations:

- **Global memory** (`~/.claude/agent-memory/<name>/`): Cross-project knowledge. Git-tracked (lives in the kordinate repo at `agents/memory/`). Use when the content applies to the agent regardless of project (general operational notes, cross-project workarounds).
- **Project-local memory** (`<repo>/.claude/agent-memory/<name>/`): Project-specific knowledge. Git-tracked. Use when the content is specific to the current repo (debug reference tables, project-specific workflows, repo-specific operational notes).

How to detect which to use:
1. If the caller explicitly says "project" or "project-local", use project-local.
2. If the caller explicitly says "global", use global.
3. If the content references project-specific entities (specific metrics, endpoints, components unique to this repo), use project-local.
4. Otherwise, default to global.

## Steps

1. Confirm the agent exists: check `~/.claude/agents/<name>/` directory
2. Determine the target location (global or project-local) using the detection rules above
3. Read the current contents of the target directory (create directory if missing)
4. Write the provided content as a memory file in that directory, following the memory format:
   ```markdown
   ---
   name: <memory name>
   description: <one-line description>
   type: <user|feedback|project|reference>
   ---

   <memory content>
   ```
5. If project-local: stage and commit the file (it is git-tracked)
6. If global: stage and commit the file (it is git-tracked in the kordinate repo)

## Restrictions

- Only edit files under the determined memory directory
- Never modify the agent's CLAUDE.md or other files
- Content must be stable and actionable — no deployment history (use changelog), no point-in-time facts that go stale, nothing derivable from git log or live queries
- Session-ephemeral state (session_id, last_line, last_commit, last_changelog_line, context_summary) belongs in `.claude/agent-state/<name>.json`, NOT in memory
