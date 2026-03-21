Consult an agent — resolve a kord, check freshness, delegate via beorn, cache the result.

Results are cached per kord. Cached results are served if the kord's `.valid` marker exists (freshness check). The invalidation hook deletes `.valid` when provider knowledge changes.

**Input**: $ARGUMENTS (required: `<agent-or-kord> "<prompt>"`, e.g. `deployer "what pods are running in prod?"`)

## Usage

```
/consult deployer "what's running in prod?"
/consult sauron "what metrics does the enricher expose?"
/consult designer "review the beorn deployment manifest"
/consult deployer "deploy the new gateway config"
/consult pattern-review "review the deployment changes for design impact"
```

## Procedure

1. Parse the target and prompt from the arguments.

2. **Resolve kord**:
   a. Resolve `KORDINATE_HOME` from the kordinate repo root (`git rev-parse --show-toplevel` + `/kordinate`).
   b. If target matches a kord directory name under `$KORDINATE_HOME/agents/root/kords/<target>/`, use that kord directly.
   c. Otherwise, treat target as an agent name and use `default-<target>` as the kord.
   d. Read `kord.md` from the resolved kord directory to get provider and guidelines.

3. **Freshness check**:
   a. Run the kord's `freshness.sh`:
      ```bash
      bash "$KORDINATE_HOME/agents/root/kords/<kord>/freshness.sh"
      echo $?
      ```
   b. If exit code is 0 (fresh), check for cached result:
      - Cache file: `$KORDINATE_HOME/agents/root/memory/dynamic/consultations/<kord>.md`
      - If it exists and the first line matches `<!-- kord:<kord> prompt: <exact prompt> -->`, return the cached content. Done.
   c. Otherwise (stale or no cache): proceed to step 4.

4. **Delegate via beorn**:
   a. Read the provider name from the kord's `kord.md` (under `## Provider`).
   b. Read the `## Guidelines` section from `kord.md`.
   c. Build the delegation prompt: "You are being consulted via the `<kord>` kord. Follow these guidelines:\n\n<guidelines>\n\nPrompt: <prompt>"
   d. Call `mcp__beorn__delegate` with `agent=<provider>` and `prompt=<delegation prompt>`.

5. **Cache the result**:
   a. Write the agent's response to the consultation cache:
      ```
      <!-- kord:<kord> prompt: <the exact prompt> -->
      <agent's response>
      ```
      File: `$KORDINATE_HOME/agents/root/memory/dynamic/consultations/<kord>.md`
   b. Create the `.valid` marker:
      ```bash
      touch "$KORDINATE_HOME/agents/root/kords/<kord>/.valid"
      ```

6. Return the agent's response to the user.

## Available agents

| Agent | Default Kord | Expertise |
|-------|-------------|-----------|
| deployer | `default-deployer` | Cluster state, pod status, deployment status, versions, networking |
| sauron | `default-sauron` | Metrics, health checks, log events, dashboards, alerting |
| designer | `default-designer` | Architecture, components, failure modes, data flow, dependencies |
| scribe | `default-scribe` | Templates, document formats, formatting conventions |

## Named kords

| Kord | Requester → Provider |
|------|---------------------|
| `pattern-review` | deployer, sauron → designer |
| `monitoring-impact` | deployer → sauron |
