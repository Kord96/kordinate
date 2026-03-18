Debug a production issue using the project's observability catalog as a guide.

**Input**: $ARGUMENTS (required: symptom description. Optional: `--cluster <name>` defaults to first cluster in ~/.claude/profile/config.yaml, `--catalog <path>` defaults to `docs/observability-catalog.yaml`)

## Context

This skill uses the observability catalog (produced by `/sauron/inventory`) to systematically investigate issues. The catalog maps every metric, log event, and health check in the project, so we know exactly what signals are available.

## Steps

1. **Load the catalog** — read `docs/observability-catalog.yaml` (or specified path). If it doesn't exist, tell the user to run `/sauron/inventory` first.

2. **Classify the symptom** — based on the user's description, identify:
   - Which **health section(s)** are likely affected
   - Which **metrics** are relevant to the symptom
   - Which **log events** would show evidence of the problem

3. **Query health status** — check overall pipeline health first:
   ```
   ssh $CLUSTER "curl -s 'http://alloy-gateway.gateway.svc:9090/api/v1/query?query=pipeline_status{component=\"sentinel\",namespace=\"prod\"}'"
   ```
   Map results to health_checks from the catalog to identify which checks are failing.

4. **Query relevant metrics** — for each metric identified in step 2:
   ```
   ssh $CLUSTER "curl -s 'http://alloy-gateway.gateway.svc:9090/api/v1/query?query=<metric_name>'"
   ```
   For rate metrics, also query the rate over 5m and 1h windows.
   For gauges, compare current value against recent history (query_range over 1h).

5. **Search relevant logs** — for each log event identified in step 2:
   Use the catalog's `component` field to construct targeted Loki queries:
   ```
   ssh $CLUSTER "curl -s 'http://alloy-gateway.gateway.svc:3100/loki/api/v1/query_range' \
     --data-urlencode 'query={namespace=\"prod\",component=\"<component>\"} |= \"<event>\"' \
     --data-urlencode 'limit=20' \
     --data-urlencode 'start=<15min_ago_ns>' \
     --data-urlencode 'end=<now_ns>'"
   ```
   Also search for error/warning level logs from the same components:
   ```
   {namespace="prod",component="<component>"} | json | level=~"error|warning"
   ```

6. **Correlate signals** — cross-reference:
   - Which health checks are failing → what metrics drive those checks (from catalog)
   - Which metrics are anomalous → what log events correspond (from catalog, same file/component)
   - Which log events show errors → what operations were affected

7. **Check pods** — for affected components:
   ```
   ssh $CLUSTER "kubectl get pods -n prod -l component=<component>"
   ```

8. **Diagnose** — produce a structured report:

   ```
   ## Diagnosis: <symptom summary>

   ### Affected Components
   | Component | Health | Key Metric | Current Value | Expected |
   |-----------|--------|------------|---------------|----------|
   | ...       | ...    | ...        | ...           | ...      |

   ### Evidence
   - **Metrics**: <what metrics show>
   - **Logs**: <what log events reveal> (cite event names from catalog)
   - **Health**: <which checks failed and why>

   ### Root Cause
   <most likely explanation based on correlated evidence>

   ### Recommended Actions
   1. <immediate action>
   2. <follow-up action>

   ### For Further Investigation
   Full observability catalog: `<project>/docs/observability-catalog.yaml`
   - Metrics consulted: <list metric names from catalog used in this diagnosis>
   - Log events checked: <list event names from catalog>
   - Health checks verified: <list section.check names from catalog>
   - Related metrics not yet queried: <other catalog metrics in the same component that may help narrow root cause>
   ```

## Rules

- Always start from the catalog — don't guess at metric/log names
- If the catalog is stale (>7 days old), warn the user and suggest re-running `/sauron/inventory`
- Query Prometheus and Loki directly via SSH + curl (not via Grafana API)
- Keep Loki queries narrow — use component labels from the catalog
- If the symptom maps to multiple sections, investigate them in dependency order (ingestion → processing → enrichment → derived → serving)
