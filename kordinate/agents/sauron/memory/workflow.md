---
description: Sauron workflow — understand, implement, validate, report
curated: true
scope: global
preloaded: sauron
---
# Workflow

1. **Understand** — Consult augur for architecture, read project memory for metrics and health checks. Map: components → what can fail → what to measure → what to test.

2. **Implement** (if request is about monitoring/logging/metrics):

   **Metrics** — Define and implement prometheus metrics. Group into registry classes by domain. Keep label cardinality low. Wire into the project's existing collection mechanism.

   **Health Checks** — Implement health endpoints covering external dependencies. Composite status gauges (0=fail, 1=warning, 2=ok).

   **Health Logs** — Warning/error level only, with quantitative dimensions. Rate-limit high-frequency warnings. Use the project's logger.

   **Logging** — Generate project-specific logging.py using klog as the pattern. structlog with JSON renderer (prod) or ConsoleRenderer (dev). stdlib bridge, suppress noisy loggers. Review: inconsistent events, missing dimensions, wrong levels. Consult `monitoring.md` and `logging.md` for standards.

   **Dashboards** — Generate Grafana dashboard JSON or PromQL queries using the Grafana MCP. Authenticate first (see auth.md).

3. **Validate** (always):
   - Use nokrashi-tools for standards testing and metric coverage
   - Fix violations — don't just report them
   - Add E2E tests for flows identified in architecture doc
   - Verify metric coverage against key_metrics
   - Use `nokrashi.tools.extract_metrics_from_promql` + Grafana MCP to find unused/missing metrics

4. **Fix** — If validation fails, fix and re-validate. Repeat until green.

5. **Review** — Use Gemini MCP to validate complex decisions.

6. **Report** — Summarize what was implemented and verified.
