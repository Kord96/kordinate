Onboard a new agent into the team — create all required files interactively.

**Input**: $ARGUMENTS (optional: `<agent-name> "<description>"`)

## Usage

```
/scribe:onboard
/scribe:onboard myagent
/scribe:onboard myagent "manages database migrations"
```

## Procedure

1. **Gather information** — parse agent name and description from arguments. If missing, ask:
   - Agent name (required)
   - One-line description (required)
   - Triggers — what words spawn this agent (required)
   - Exclusive tools — what tools only this agent can use (optional, default: none)
   - Kord expertise — what this agent answers when consulted (required)

   Use the AskUserQuestion tool for any missing information. If the description provides enough detail, extract triggers/tools/expertise from it without asking.

2. **Create agent directory structure:**
   ```
   agents/<name>/
   ├── IDENTITY.md
   ├── instructions/
   ├── memory/
   │   ├── static/
   │   └── dynamic/
   │       └── consultations/
   │           └── .gitkeep
   └── commands/
   ```

3. **Generate IDENTITY.md** from template:
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

   <expertise>. See kords: `default-<name>`.
   ```

4. **Create default kord** using `/scribe:kord`:
   - Name: `default-<agent-name>`
   - Requester: any
   - Provider: `<agent-name>`
   - Guidelines: extracted from expertise

5. **Update root IDENTITY.md** — read `agents/root/IDENTITY.md`. Add the new agent to:
   - The agents table (name, triggers, purpose)
   - The kords table (default-<name>, any, <name>)

6. **Create guard hook** (if exclusive tools specified):
   - Generate `hooks/guard-<name>.sh` following the same pattern as guard-kubectl.sh
   - The hook should check for `/tmp/.<name>-auth`
   - Add the hook to settings.json

7. **Run link-claude.sh** to register the new agent.

8. **Report** what was created and what the user should do next:
   - "Agent <name> onboarded. Files created: ..."
   - "Next: add domain knowledge to memory/static/, define commands in commands/"

## Notes

- Use scribe auth for all .md file edits
- Follow the exact IDENTITY.md frontmatter format (Claude Code requires it)
- The generated files are starting points — the user customizes them
