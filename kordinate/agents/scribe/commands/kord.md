Kord a new agent into the team — create all required files interactively.

**Input**: $ARGUMENTS (optional: `<agent-name> "<description>"`)

## Usage

```
/scribe:kord
/scribe:kord myagent
/scribe:kord myagent "manages database migrations"
```

## Procedure

1. **Gather information** — parse agent name and description from arguments. If missing, ask:
   - Agent name (required)
   - One-line description (required)
   - Triggers — what words spawn this agent (required)
   - Exclusive tools — what tools only this agent can use (optional, default: none)
   - Consultation expertise — what this agent answers when consulted (required)

   Use the AskUserQuestion tool for any missing information. If the description provides enough detail, extract triggers/tools/expertise from it without asking.

2. **Create agent directory structure:**
   ```
   agents/<name>/
   ├── AGENT.md
   ├── instructions/
   │   └── consultation.md
   ├── memory/
   │   ├── static/
   │   └── dynamic/
   └── commands/
   ```

3. **Generate AGENT.md** from template:
   ```markdown
   ---
   name: <name>
   model: inherit
   memory: user
   tools:
     - Read
     - Edit
     - Write
     - Bash
     - Glob
     - Grep
   triggers:
     - "<trigger1>"
     - "<trigger2>"
   ---

   # <Name>

   <description>

   ## Commands

   | Command | Purpose |
   |---------|---------|

   ## Rules

   - <any rules inferred from description>

   ## Consultation

   <expertise>. See `memory/consultation.md`.
   ```

4. **Generate instructions/consultation.md:**
   ```markdown
   # Consultation

   ## Cache Sources

   Directories to hash for cache invalidation:

   - `instructions/`
   - `memory/static/`
   - `memory/dynamic/`

   When consulted, answer about:
   - <expertise items>

   ## How to answer

   1. Use project memory as primary source
   2. Scan project source if needed
   3. Answer with specific facts
   4. Keep responses under 50 lines
   ```

5. **Update root AGENT.md** — read agents/AGENT.md (the root agent). Add the new agent to:
   - The agents table (name, triggers, purpose)
   - The consultation table (name, expertise)

6. **Create guard hook** (if exclusive tools specified):
   - Generate `hooks/guard-<name>.sh` following the same pattern as guard-kubectl.sh
   - The hook should check for `/tmp/.<name>-auth`
   - Add the hook to settings.json

7. **Run link-claude.sh** to register the new agent.

8. **Report** what was created and what the user should do next:
   - "Agent <name> kord'd. Files created: ..."
   - "Next: add domain knowledge to memory/static/, define commands in commands/"

## Notes

- Use scribe auth for all .md file edits
- Follow the exact AGENT.md frontmatter format (Claude Code requires it)
- The generated files are starting points — the user customizes them
