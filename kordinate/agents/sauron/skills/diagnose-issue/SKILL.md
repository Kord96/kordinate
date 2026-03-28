---
name: diagnose-issue
description: Debug a production issue using the project's observability catalog as a guide.
argument-hint: "<symptom> [--cluster <name>] [--catalog <path>]"
curated: true
scope: global
---

Debug a production issue using the project's observability catalog as a guide.

**Input**: $ARGUMENTS (required: symptom description. Optional: `--cluster <name>` defaults to first cluster in `$KORDINATE_HOME/profile/config.yaml`, `--catalog <path>` defaults to `docs/observability-catalog.yaml`)

## Context

This skill uses the observability catalog (produced by `/sauron/scan-observability`) to systematically investigate issues. The catalog maps every metric, log event, and health check in the project, so we know exactly what signals are available.

## Steps

1. **Load the catalog** — read `docs/observability-catalog.yaml` (or specified path). If it doesn't exist, tell the user to run `/sauron/scan-observability` first.

2. **Classify the symptom** — based on the user's description, identify:
   - Which **health section(s)** are likely affected
   - Which **metrics** are relevant to the symptom
   - Which **log events** would show evidence of the problem

3. **Resolve service endpoints** — read `$KORDINATE_HOME/profile/config.yaml` and extract the cluster's service ports:
   - `PROM_PORT` from `clusters.<name>.services.metrics.port` (default: 9090)
   - `LOKI_PORT` from `clusters.<name>.services.logs.port` (default: 3100)
   - `CLUSTER_IP` from `clusters.<name>.tailscale_ip`

   Prometheus URL: `http://<CLUSTER_IP>:<PROM_PORT>`
   Loki URL: `http://<CLUSTER_IP>:<LOKI_PORT>`

4. **Query health status** — use health-related metrics from the catalog to check overall pipeline health:
   ```
   ssh $CLUSTER "curl -s 'http://<CLUSTER_IP>:<PROM_PORT>/api/v1/query?query=<health_metric_from_catalog>'"
   ```
   Map results to health_checks from the catalog to identify which checks are failing.

5. **Query relevant metrics** — for each metric identified in step 2:
   ```
   ssh $CLUSTER "curl -s 'http://<CLUSTER_IP>:<PROM_PORT>/api/v1/query?query=<metric_name>'"
   ```
   For rate metrics, also query the rate over 5m and 1h windows.
   For gauges, compare current value against recent history (query_range over 1h).

6. **Search relevant logs** — for each log event identified in step 2:
   Use the catalog's `component` field to construct targeted Loki queries:
   ```
   NOW_NS=$(date +%s)000000000
   START_NS=$(( $(date +%s) - 900 ))000000000
   ssh $CLUSTER "curl -s 'http://<CLUSTER_IP>:<LOKI_PORT>/loki/api/v1/query_range' \
     --data-urlencode 'query={namespace=\"prod\",component=\"<component>\"} |= \"<event>\"' \
     --data-urlencode 'limit=20' \
     --data-urlencode 'start=$START_NS' \
     --data-urlencode 'end=$NOW_NS'"
   ```
   Also search for error/warning level logs from the same components:
   ```
   {namespace="prod",component="<component>"} | json | level=~"error|warning"
   ```

7. **Correlate signals** — cross-reference:
   - Which health checks are failing → what metrics drive those checks (from catalog)
   - Which metrics are anomalous → what log events correspond (from catalog, same file/component)
   - Which log events show errors → what operations were affected

8. **Check pods** — for affected components:
   ```
   ssh $CLUSTER "kubectl get pods -n prod -l component=<component>"
   ```

9. **Diagnose** — produce a structured report:

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
- If the catalog is stale (>7 days old), warn the user and suggest re-running `/sauron/scan-observability`
- Query Prometheus and Loki directly via SSH + curl (not via Grafana API)
- Keep Loki queries narrow — use component labels from the catalog
- If the symptom maps to multiple sections, investigate them in dependency order (ingestion → processing → enrichment → derived → serving)
