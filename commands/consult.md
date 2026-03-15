Consult an agent — spawn it and ask a question.

**Input**: $ARGUMENTS (required: `<agent> "<question>"`, e.g. `deployer "what pods are running in prod?"`)

## Usage

```
/consult deployer "what's running in prod?"
/consult sauron "what metrics does the enricher expose?"
/consult designer "what are logbd's main components?"
```

## Procedure

1. Parse the agent name and question from the arguments.
2. Spawn the agent using the Agent tool:
   - Read `~/.claude/agents/<name>/memory.md` — check `## Identity` for a stored `agent_id`. If one exists, pass it as the `resume` parameter; if not, omit `resume` to start fresh.
   - Instruct the agent: "You are being consulted. Answer the following question using your Consultation guidelines from your CLAUDE.md: <question>"
3. Return the agent's response to the user.
4. Store the returned agent ID via `/scribe:update-subagent-memory`.

## Available agents

| Agent | Expertise |
|-------|-----------|
| deployer | Cluster state, pod status, deployment status, versions, networking |
| sauron | Metrics, health checks, log events, dashboards, alerting |
| designer | Architecture, components, failure modes, data flow, dependencies |
