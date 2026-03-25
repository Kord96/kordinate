# New Agent

Level 3 resource for the onboard skill.

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Agent name (required, kebab-case)
    - One-line description (required)
    - Tools (optional, defaults to standard set)
    - Exclusive tools (optional) — tools only this agent should use
    - Kord expertise — what this agent provides when consulted (required)

2. **Create agent directory** in kordinate:
    ```
    $KORDINATE_HOME/agents/<name>/
    ├── IDENTITY.md
    ├── skills/
    └── memory/
        └── scratchpad.md
    ```

3. **Generate IDENTITY.md** — see [identity-template.md](../remember/identity-template.md) for the template. Add frontmatter properties (`curated: true`, `preloaded: <name>`, `scope: global`).

4. **Generate scratchpad.md** with empty frontmatter (`curated: false`, `scope: global`).

5. **Create default kord** — use `/create-kord default-<name>` with the expertise from step 1.

6. **Create guard hook** (if exclusive tools specified):
    - Generate `$KORDINATE_HOME/hooks/guard-<name>.sh`:
      ```bash
      #!/bin/bash
      INPUT=$(cat)
      if [ -f "/tmp/.<name>-auth" ]; then
        exit 0
      fi
      echo "Only <name> may perform this operation. Delegate to <name>." >&2
      exit 2
      ```
    - Make executable: `chmod +x guard-<name>.sh`
    - Add to settings.json under the appropriate `PreToolUse` matcher

7. **Sync to runtime** — write this agent to the runtime's native paths per [claude-native.md](../remember/claude-native.md).

8. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh`.

9. **Report** what was created and next steps:
    - "Agent `<name>` onboarded. Files: ..."
    - "Next: add domain knowledge to memory/, define skills in skills/"
