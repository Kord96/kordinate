---
description: Domain-Driven Design — monitoring guidance
curated: true
scope: global
preloaded: none
---
## Monitoring

Track aggregate operations and cross-context communication to detect boundary violations and performance issues.

### Key Metrics

- `aggregate_command_total` (counter) — commands processed per aggregate type
- `domain_event_published_total` (counter) — events published per bounded context
- `cross_context_call_total` (counter) — calls between bounded contexts (should be low and intentional)
- `aggregate_command_duration_seconds` (histogram) — time to process commands per aggregate type
- `anti_corruption_translation_errors_total` (counter) — failures in anti-corruption layer translations

### Alerts

- Cross-context call rate increasing unexpectedly (boundary erosion)
- Aggregate command latency exceeding SLA
- Event publishing failures accumulating in any context
- Anti-corruption layer error rate exceeding threshold
