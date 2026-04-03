---
description: Sauron workflow — read atlas, implement monitoring, validate, report
---
# Workflow

1. **Understand** — Read augur's atlas for the project (the atlas IS the spec — there is no separate monitoring-spec). Key sections:
   - `failure_modes[].detection` — signals, concerns, and source patterns to monitor
   - `components` — what exists and how it connects
   - `infrastructure.monitoring` — vitals config and dashboard stubs

   Also read `infra-atlas.json` for cluster-level observability config (endpoints, scrape discovery, vitals contract).

2. **Implement** (if request is about monitoring/logging/metrics):

   **Vitals** — Standalone deployment (one per app, not sidecar). Evaluates health by querying Prometheus and Loki. Produces tri-state gauges (0=FAIL, 1=WARNING, 2=OK) on port 9131. Map atlas `failure_modes.detection.signals` to vitals evaluation sections.

   **Metrics** — Define and implement prometheus metrics. Group into registry classes by domain. Keep label cardinality low. Wire into the project's existing collection mechanism.

   **Logging** — Structured JSON to stdout. Required fields: level, component, event, timestamp. Consult `monitoring.md` and `logging.md` for standards.

   **Dashboards** — Generate Grafana dashboard JSON. Provision via ConfigMaps (Grafana polls every 30s). Store at `<project-repo>/monitoring/dashboards/`. Use Grafana MCP for management.

3. **Validate** (always):
   - Verify metric coverage against atlas failure_modes
   - Check vitals evaluations cover required sections (process, deps at minimum)
   - Ensure VitalsMissing meta-alert exists for every app
   - Use Grafana MCP to verify dashboard provisioning

4. **Fix** — If validation fails, fix and re-validate. Repeat until green.

5. **Review** — Use Gemini CLI to validate complex decisions.

6. **Report** — Summarize what was implemented and verified.
