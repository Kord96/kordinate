Send an async message to an agent's inbox.

**Input**: $ARGUMENTS (expect: `<agent> "<message>"`)

## Steps

1. Parse the target agent name and message from the arguments
2. Validate the agent exists: check that `agents/<agent>/inbox.md` exists
3. Read `agents/<agent>/inbox.md` to get current contents
4. Append a new entry at the end of the file:
   ```
   - <ISO 8601 timestamp> | <sender> | <message>
   ```
   Where `<sender>` is the agent or user who triggered the send (use "parent" if triggered by the user directly, or the calling agent's name if forwarded from another agent).
5. Commit: `docs: send message to <agent> inbox [scribe]`

**Notes**:
- Do not remove or modify existing inbox entries — append only.
- Keep the `# Inbox` header at the top of the file.
- Use UTC timestamps in ISO 8601 format (e.g., `2026-03-12T14:30:00Z`).
