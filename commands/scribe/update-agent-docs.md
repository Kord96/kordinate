Update an agent's documentation files under `agents/<name>/`.

**Input**: $ARGUMENTS (expect: agent name and what to update)

## Steps

1. Confirm the agent exists: check `agents/<name>/` directory
2. Read the target file(s) under `agents/<name>/`
3. Understand the current content before making changes
4. `chmod u+w` the target file
5. Apply the requested changes — this can be:
   - Updating the agent's knowledge docs (e.g., `monitoring.md`, `logging.md`, `patterns.md`)
   - Updating the agent's `CLAUDE.md` (workflow, triggers, tools)
6. `chmod 444` the target file
7. Commit: `docs: update <agent> agent docs [scribe]`

## Restrictions

- Only edit files under the specified agent's directory
- Never edit another agent's files in the same operation
- Never edit root `CLAUDE.md`
- Never remove existing content unless explicitly asked to replace it
