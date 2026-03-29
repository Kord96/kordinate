---
name: remember
description: Register a memory file in KORD.json — decide scope and preload. Run after writing a memory file.
argument-hint: "<file-path> [--scope global|project|both] [--preload <agent>|all|none]"
---

Register a memory file that was already written. This skill doesn't write the file — it registers it in KORD.json so the system knows about it (scope, preload, owner).

A nudge hook reminds you to run this when unregistered memory files are detected.

## Arguments

`$ARGUMENTS` — Required: `<file-path>` (the memory file to register). Optional:
- `--scope global|project|both` — where this memory applies. If omitted, decide based on content.
- `--preload <agent>|all|none` — whether to load at boot. Default: `none`.

## Procedure

1. **Read the file** — extract a one-line description from the first meaningful line of content (skip frontmatter if present).

2. **Derive owner** — from the file path:
   - `agents/<name>/memory/` → owner is `<name>`
   - `shared/` → owner is `team`
   - `team/` → owner is `team`

3. **Decide scope** (if not provided):
   - Does the content mention project-specific paths, repos, or local endpoints? → `project`
   - Is it general knowledge useful across projects? → `global`
   - Could apply to both? → `both`
   - When unclear: default to `global`

4. **Decide preload** (if not provided):
   - Is this a quick observation or working note? → `none`
   - Is this reference material the agent needs every session? → `<owner-agent>`
   - Default: `none`

5. **Register in KORD.json** — add a file entry:
   ```json
   {
     "type": "file",
     "path": "<relative path from kordinate root>",
     "description": "<one-line description>",
     "owner": "<derived from path>",
     "preload": "<decided>",
     "validation": "<owner>"
   }
   ```

6. **Handle scope**:
   - `global` — file stays where it is (already in `~/.kord/`). Register in global KORD.json.
   - `project` — copy or symlink to `.kord/agents/<name>/memory/` in the current project. Register in project KORD.json if one exists.
   - `both` — keep in global, copy to project.

7. **Report** — confirm: file registered, owner, scope, preload.
