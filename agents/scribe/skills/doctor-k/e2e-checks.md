# End-to-End Checks

Level 3 resource for the doctor-k skill. These checks actually invoke the system — spawning agents, calling capability tools, writing memories. They verify behavior, not just structure.

Run these after structural and runtime checks pass. They have side effects (spawn agents, write temp memories) and take longer to execute.

## Agent spawning

For each agent in `$KORDINATE_HOME/agents/` (except `main`):

1. Spawn via Agent tool with `subagent_type` set to the agent name
2. Prompt: "Reply with only your name and one-line description."
3. Verify the response contains the agent's `name` from IDENTITY.md

- **PASS** — agent responds with correct identity
- **FAIL** — agent not found, wrong identity, or spawn error

## Beorn capability tools

For one agent (pick the first alphabetically), test capability tool invocation via Beorn:

1. Call a capability tool exposed by the agent's route (e.g., `write_memory` for scribe)
2. Verify the tool returns a structured response (not an error)
3. Verify the agent processed the request (check for expected output fields)

- **PASS** — capability tool returned expected response
- **PARTIAL** — tool responded but with unexpected format
- **FAIL** — tool errored or agent could not process the request

## Memory write tool

Test the `write_memory` capability tool:

1. Call `write_memory` with a test payload: `"test-e2e-check: this is a health check probe"`
2. Scribe should authenticate, write the memory, and report success
3. Verify the memory was written to `$KORDINATE_HOME/agents/<caller>/memory/scratchpad.md`
4. Clean up: remove the test entry from scratchpad

- **PASS** — memory written and cleaned up
- **FAIL** — tool error, auth failure, or write failure

## Memory persistence

1. Write a test memory via `write_memory` tool: `e2e-probe: <timestamp>`
2. Verify it appears in the agent's scratchpad at `$KORDINATE_HOME`
3. Verify the runtime MEMORY.md index at `~/.claude/agent-memory/<name>/MEMORY.md` has an entry for scratchpad.md
4. Clean up the test entry

- **PASS** — memory persisted to both kordinate and runtime paths
- **FAIL** — missing from one or both paths

## Guard enforcement

1. Attempt to write directly to a curated kordinate file (e.g., `$KORDINATE_HOME/agents/scribe/IDENTITY.md`) without scribe auth
2. The guard hook should block the write

- **PASS** — write blocked with appropriate message
- **FAIL** — write succeeded (guard not enforcing)

Note: this test depends on the guard hook being active. Skip if hooks are disabled.

## Kord worktree isolation

Only run if `$KORDINATE_HOME` is a git repo:

1. Check if session branches exist in `$KORDINATE_HOME` (`git branch --list 'session/*'`)
2. If any exist, verify they have their own worktree paths
3. Verify `KORDINATE_HOME` env var in the current session points to the correct worktree (or main if window 0)

- **PASS** — isolation is correctly configured
- **SKIP** — `$KORDINATE_HOME` is not a git repo
- **FAIL** — branches exist but worktrees are missing or KORDINATE_HOME points wrong

## Per-agent capability checks

Each agent's IDENTITY.md has a `## Capabilities` section listing testable assertions (e.g., "Can detect architectural concepts via /detect-concepts"). For each capability:

1. Read the agent's IDENTITY.md and extract the Capabilities list
2. For each capability, design a minimal probe that tests it:
   - Skills that analyze: provide a small test input and verify structured output
   - Skills that write: invoke and verify the artifact was created, then clean up
   - Skills that require infrastructure (kubectl, Grafana): **SKIP** if not available, don't fail
3. Invoke the agent's capability tool via Beorn with a minimal task

- **PASS** — capability produced expected result
- **SKIP** — required infrastructure unavailable
- **FAIL** — skill errored, produced wrong output, or agent couldn't perform the capability

Keep probes minimal — the goal is "does this work at all," not "does it work perfectly." A detect-concepts probe might scan a 3-file test fixture, not a full repo.

## Output format

Present as a checklist grouped by category:

```
System E2E:
  [PASS] Agent spawning: augur, charon, sauron, scribe, warden, alfred
  [PASS] Beorn capability tools: augur responded via capability tool
  [PASS] Memory write tool: write_memory wrote and cleaned up
  [PASS] Memory persistence: scratchpad + runtime index updated
  [PASS] Guard enforcement: curated write blocked
  [SKIP] Kord worktree isolation: not a git repo

Per-Agent Capabilities:
  augur:
    [PASS] detect architectural concepts via /detect-concepts
    [PASS] produce architecture.yaml via /architect
    [SKIP] review API surfaces — no test fixture
  charon:
    [SKIP] bootstrap cluster — no kubectl access
    [SKIP] add worker node — no kubectl access
  scribe:
    [PASS] write agent memories via write_memory
    [PASS] link kordinate to runtime via /register --link
  ...
```

Follow with summary: `E2E: X passed, Y failed, Z skipped | Capabilities: X passed, Y failed, Z skipped`
