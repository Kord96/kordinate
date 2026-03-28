---
description: Prioritize Grafana renderer for visual dashboard auditing over JSON-only analysis
curated: false
scope: global
preloaded: sauron
---

Prioritize using Grafana renderer (curl to /render/d/...) for visual investigation over JSON inspection when auditing dashboards. Visual audit catches layout issues (overlapping panels, wrong row assignments, spacing problems) that JSON gridPos analysis misses.

**How to render:** `curl -s -u "admin:$(pass show kordinate/grafana_admin/api_key)" "https://grafana.khaledkord.com/render/d/<uid>/<uid>?orgId=1&width=1400&height=1200&timeout=30&var-namespace=prod" -o /tmp/<name>.png`

**Why:** JSON gridPos looks correct but Grafana renders differently — panels bleed across rows, collapsed states behave unexpectedly, and datasource issues only show visually.

**How to apply:** After making dashboard JSON edits, always render a screenshot to verify the result before reporting success.

**Note:** For project-specific notes, use the `write_memory` tool to save memories.
