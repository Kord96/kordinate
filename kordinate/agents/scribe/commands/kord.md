Define a new kord — a coordination agreement between agents.

**Input**: $ARGUMENTS (optional: `<kord-name> "<description>"`)

## Usage

```
/scribe:kord
/scribe:kord pattern-review
/scribe:kord pattern-review "architecture review for deployment changes"
```

## Procedure

1. **Gather information** — parse kord name and description from arguments. If missing, ask:
   - Kord name (required, kebab-case)
   - One-line description (required)
   - Requester — which agents can invoke this kord (required, or "any")
   - Provider — which agent answers (required, exactly one)

   Use the AskUserQuestion tool for any missing information.

2. **Create kord directory structure:**
   ```
   agents/root/kords/<name>/
   ├── kord.md
   └── pre-consult.sh
   ```

3. **Generate kord.md** from this template:
   ```markdown
   ---
   description: <one-line description>
   requester: <agent(s), comma-separated, or "any">
   provider: <agent>
   ---

   ## Provider Guidelines

   <brief behavioral instructions — how to approach the answer, not how to do the job>
   <the provider already knows its domain — guidelines shape the output, not the process>

   ### Response Format

   | Field | Required |
   |-------|----------|
   | <field> | yes/no |

   ## Cache Invalidation

   Invalidate when:
   - <condition>
   ```

   **Template rules:**
   - Provider Guidelines tell the provider how to behave (concise, specific, severity-based), not how to do its job
   - Response Format defines the expected output structure so requesters can rely on it
   - Never include procedure ("check this file", "run this command") — the provider knows its domain

4. **Generate pre-consult.sh:**
   ```bash
   #!/bin/bash
   KORDINATE_HOME="${KORDINATE_HOME:-$(cd "$(dirname "$0")/../../.." && pwd)}"
   KORD_NAME="<name>"
   VALID_MARKER="$KORDINATE_HOME/agents/root/kords/$KORD_NAME/.valid"
   if [ -f "$VALID_MARKER" ]; then
     exit 0  # fresh
   fi
   exit 1  # stale
   ```
   Make it executable: `chmod +x pre-consult.sh`

5. **Update registry.md** — add the new kord to `agents/root/kords/registry.md`.

6. **Report** what was created:
   - "Kord `<name>` defined. Files: kords/<name>/kord.md, kords/<name>/pre-consult.sh"

## Notes

- Use scribe auth for all .md file edits
- Kords live under `agents/root/kords/` — each is a directory
- The `.valid` marker is created by `/consult` and deleted by the invalidation hook
