Consult an agent — spawn it and ask a question.

Results are cached per consulter-consultant pair. Cached results are served if the consultant's knowledge hasn't changed. Use `/invalidate <agent>` to force re-consultation.

**Input**: $ARGUMENTS (required: `<agent> "<question>"`, e.g. `deployer "what pods are running in prod?"`)

## Usage

```
/consult deployer "what's running in prod?"
/consult sauron "what metrics does the enricher expose?"
/consult designer "what are logbd's main components?"
```

## Procedure

1. Parse the agent name (consultant) and question from the arguments.

2. **Check consultation cache**:
   a. Resolve paths:
      - `KORDINATE_HOME` from the kordinate repo root (find it via `git rev-parse --show-toplevel` + `/kordinate`)
      - Cache file: `$KORDINATE_HOME/agents/shared/memory/dynamic/<your-agent-name>-<consultant>.cache`
      - Hash file: `$KORDINATE_HOME/agents/shared/memory/dynamic/.<your-agent-name>-<consultant>.hash`
      - Source dirs: `$KORDINATE_HOME/agents/<consultant>/instructions/`, `.../memory/static/`, `.../memory/dynamic/`
   b. If cache file exists and has content, run:
      ```bash
      source "$KORDINATE_HOME/lib/cache.sh"
      cache_check "<hash_file>" "<source_dir1>" "<source_dir2>" "<source_dir3>"
      echo $?
      ```
   c. If exit code is 0 (fresh), read the first line of the cache file. If it starts with `<!-- cache:question:` and the question inside matches the current question — read the rest of the file and return it to the user. Done.
   d. Otherwise (stale, missing, or different question): proceed to step 3.

3. Spawn the agent using the Agent tool:
   - Check `.claude/agent-state/<name>.json` for the agent's `agent_id`. If one exists, pass it as the `resume` parameter; if not, omit `resume` to start fresh.
   - Instruct the agent: "You are being consulted. Answer the following question using your Consultation guidelines from your CLAUDE.md: <question>"

4. **Cache the result**:
   a. Write the agent's response to the cache file, with a question header on the first line:
      ```
      <!-- cache:question: <the exact question> -->
      <agent's response>
      ```
   b. Store the hash:
      ```bash
      source "$KORDINATE_HOME/lib/cache.sh"
      cache_store "<hash_file>" "<source_dir1>" "<source_dir2>" "<source_dir3>"
      ```

5. Return the agent's response to the user.
6. Store the returned agent ID via `/scribe:update-subagent-memory`.

## Available agents

| Agent | Expertise |
|-------|-----------|
| deployer | Cluster state, pod status, deployment status, versions, networking |
| sauron | Metrics, health checks, log events, dashboards, alerting |
| designer | Architecture, components, failure modes, data flow, dependencies |
