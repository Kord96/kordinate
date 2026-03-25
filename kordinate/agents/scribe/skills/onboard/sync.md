# Sync

Level 3 resource for the onboard skill.

When invoked with `/onboard sync`, sync all agents from kordinate to the runtime.

Useful after: first install, adding an agent manually, or switching runtimes.

## Procedure

For each agent found in `$KORDINATE_HOME/agents/`:

1. Read `IDENTITY.md`
2. Write to the runtime's native agent path — see [claude-native.md](../remember/claude-native.md)
3. Ensure memory paths exist in the runtime
4. Check kord contracts — for stateless kords, add borrowed skills to requester agents
5. Ensure `preloaded: all` files are `@imported` in CLAUDE.md

Report what was synced.
