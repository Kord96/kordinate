Add a new MCP entry to `~/.claude/profile/mcps.md`.

**Input**: $ARGUMENTS (expect: MCP name, purpose, and key operations)

## Steps

1. Read `~/.claude/profile/mcps.md`
2. Verify the MCP isn't already documented
3. Determine which section it belongs to (Infrastructure, Development, AI)
4. `chmod u+w ~/.claude/profile/mcps.md`
5. Add the entry to the appropriate section. Follow the existing format:
   - If simple (like postgres/redis): add a row to the table
   - If complex (like serena/tmux-agent): add a subsection with bullet points
6. `chmod 444 ~/.claude/profile/mcps.md`
7. Commit: `docs: add <mcp> to MCP reference [scribe]`

**Never** rewrite or restructure existing entries.
