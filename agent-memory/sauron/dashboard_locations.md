---
name: dashboard-locations
description: Where to read/write dashboard JSON files — never work directly with kordinate
type: feedback
---

Dashboard source of truth locations:
- **~/.claude/dashboards/**: Core/infra dashboards (physical-resources.json)
- **.claude/dashboards/**: Project-specific dashboards (operational-health, operational-detail, overview, classifier, drill/*)

**Never edit dashboards in kordinate directly.** The kordinate copies are deployment artifacts — the deployer syncs from the above locations when building ConfigMaps.

**Why:** We moved dashboards out of kordinate to decouple editing from deployment. Editing kordinate directly bypasses the source of truth and creates drift.

**How to apply:** When auditing or editing dashboards, always read/write from ~/.claude/dashboards/ or .claude/dashboards/. After editing, tell the deployer to sync and rebuild ConfigMaps.
