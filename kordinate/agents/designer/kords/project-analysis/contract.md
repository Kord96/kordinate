---
description: Full project analysis — architecture, patterns, dependencies, API surface, tech debt
requester: scribe
provider: designer
mode: stateful
curated: true
scope: global
---

## Provider Guidelines

Run a full analysis suite against the target project. The message starts with the project path.

1. Parse the project path from the first word of the message
2. Run analyses in dependency order — each step feeds the next:
   - `/detect-patterns` — write patterns.md
   - `/map-dependencies` — write dependencies.md
   - `/review-api` — write api-review.md (skip if no HTTP endpoints detected)
   - `/assess-debt` — write debt-assessment.md (skip if detect-patterns produced no results)
   - `/architect` — write architecture.yaml (runs last, reads all previous outputs)
3. Write all outputs to `<project>/.kord/agents/designer/memory/`
4. Return a manifest listing what was produced and what was skipped with reasons

### Response Format

| Field | Required |
|-------|----------|
| Manifest of produced artifacts with paths | yes |
| Manifest of skipped artifacts with reasons | yes |
| Summary of key findings | yes |

## Cache Inputs

Hash the project source directories (passed as $1 to expiry.sh).
