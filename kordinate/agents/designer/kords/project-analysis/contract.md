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

2. **Parallel scan** — run these three simultaneously (they are independent):
   - `/detect-patterns` — write patterns.md
   - `/map-dependencies` — write dependencies.md
   - `/review-api` — write api-review.md (skip if no HTTP endpoints detected)

3. **Debt assessment** — after detect-patterns completes:
   - `/assess-debt` — write debt-assessment.md (skip if detect-patterns found nothing)

4. **Architecture** — after all above complete:
   - `/architect` — write architecture.yaml (reads all previous outputs)

5. **Synthesize** — re-read all 5 outputs together. Check for coherence:
   - Do component boundaries in architecture.yaml reflect what patterns and debt revealed? (e.g., a god-object anti-pattern might mean a component should be split)
   - Do dependency edges match what map-dependencies found?
   - Do failure modes account for the resilience patterns (or lack thereof) detected?
   - Does the architecture.yaml tell a consistent story across all analyses?

   Adjust architecture.yaml if the synthesis reveals inconsistencies. This is not a mechanical merge — it's a second look with the full picture.

6. Write all outputs to `<project>/.kord/agents/designer/memory/`

7. Return a manifest listing what was produced and what was skipped with reasons

### Response Format

| Field | Required |
|-------|----------|
| Manifest of produced artifacts with paths | yes |
| Manifest of skipped artifacts with reasons | yes |
| Summary of key findings | yes |
| Synthesis adjustments made (if any) | yes |

## Cache Inputs

Hash the project source directories (passed as $1 to expiry.sh).
