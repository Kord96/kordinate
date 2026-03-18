Update project-level documentation files (root `CLAUDE.md`, `commands/*.md`, `README.md`).

**Input**: $ARGUMENTS (expect: file path(s) and what to update)

## Steps

1. Confirm the target file exists and is a project-level `.md` file (root `CLAUDE.md`, `commands/`, or `README.md`)
2. Read the target file(s)
3. Understand the current content before making changes
4. `chmod u+w` the target file
5. Apply the requested changes
6. `chmod 444` the target file
7. Commit: `docs: update <filename> [scribe]`

## Restrictions

- Only edit project-level files: root `CLAUDE.md`, `commands/*.md`, `README.md`
- Never edit files under `agents/` — use `update-agent-docs` for those
- Never edit files under `~/.claude/profile/` — use the appropriate profile command
- Never remove existing content unless explicitly asked to replace it
