---
description: Full project analysis — architecture, concepts, dependencies, API surface, debt
requester: scribe
provider: augur
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Run a full project analysis. The message starts with the project path.

1. Parse the project path from the first word of the message

2. **Run `/analyze`** — produces architecture.yaml v2, which includes concepts, dependencies, API surface, and debt assessment in a single pass.

3. **Verify** — confirm architecture.yaml was written. Re-read it and check:
   - Components section is populated (not empty)
   - Concepts section has scan_metadata showing the catalog was scanned
   - Debt section has a grade

4. Return a manifest listing what was produced and key findings

### Response Format

| Field | Required |
|-------|----------|
| Path to architecture.yaml | yes |
| Summary of key findings (purpose, component count, concept count, debt grade) | yes |
| Any warnings or issues encountered | yes |

## Cache Inputs

Hash the project source directories (passed as $1 to expiry.sh).
