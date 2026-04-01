---
name: remember
description: Move a memory file to kordinate and register it in KORD.json. Decides scope and preload.
argument-hint: "<file-path> [--scope global|project|both] [--preload <agent>|all|none]"
---

Move a memory file to its correct kordinate path and register it in KORD.json. This ensures all memory is preserved in `~/.kord/` — the single backup point. Files in `~/.claude/` are staging; kordinate is permanent.

A nudge hook reminds you to run this when unregistered memory files are detected.

## Arguments

`$ARGUMENTS` — Required: `<file-path>` (the memory file to move and register). Optional:
- `--scope global|project|both` — where this memory applies. If omitted, decide based on content.
- `--preload <agent>|all|none` — whether to load at boot. Default: `none`.

## Procedure

1. **Read the file** — extract a one-line description from the first meaningful line of content.

2. **Determine destination** — based on the source path:
   - File is in `~/.claude/projects/*/memory/` → main session auto-memory, move to `~/.kord/agents/main/memory/`
   - File is in `~/.claude/agent-memory/<name>/` → agent memory, move to `~/.kord/agents/<name>/memory/`
   - File is already in `~/.kord/` → don't move, just register
   - File is in `.kord/` (project) → don't move, just register in project KORD.json

3. **Move the file** — copy to the kordinate destination. If the file was in `~/.claude/`, remove the original after copying (kordinate is now the source of truth).

4. **Derive owner** — from the destination path:
   - `agents/<name>/memory/` → owner is `<name>`
   - `shared/` → owner is `team`

5. **Decide scope** (if not provided):
   - Content mentions project-specific paths, repos, local endpoints → `project`
   - General knowledge useful across projects → `global`
   - Could apply to both → `both`
   - Default: `global`

6. **Decide preload** (if not provided):
   - Quick observation or working note → `none`
   - Reference material needed every session → `<owner-agent>`
   - Default: `none`

7. **Register in KORD.json** — add a file entry:
   ```json
   {
     "type": "file",
     "path": "<relative path from kordinate root>",
     "description": "<one-line description>",
     "owner": "<derived>",
     "preload": "<decided>",
     "validation": "<owner>"
   }
   ```

8. **Handle scope**:
   - `global` — file is in `~/.kord/`. Register in global KORD.json.
   - `project` — copy to `.kord/agents/<name>/memory/` in the current project. Register in project KORD.json if one exists.
   - `both` — keep in global, copy to project.

9. **Report** — confirm: file moved from → to, owner, scope, preload, registered.
