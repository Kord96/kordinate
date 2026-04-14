# Tension Signals

Use this reference when turning semantic findings into grounded architecture tensions.

## High-Signal Tension Patterns

- reliability depends on critical external calls without enough resilience
- boundary layers own business logic that should live deeper in the system
- multiple components share mutable state without a clear coordination model
- operational simplicity trades off against strict isolation or modularity
- a workflow spans several components but observability or ownership is fragmented

## Cross-Cutting Signals

- hardcoded production assumptions in config or deployment paths
- missing health visibility for long-running workers or queues
- repeated fallback gaps around the same dependency type
- direct infrastructure access leaking across intended boundaries

## Reporting

- group repeated instances into one tension when they share a root trade-off
- keep tensions architecture-level, not backlog-level
- tie every tension to concrete components and evidence
