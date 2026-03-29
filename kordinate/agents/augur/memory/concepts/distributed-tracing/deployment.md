---
description: Distributed Tracing Instrumentation — deployment guidance
type: supplementary
---
## Deployment

Maintain trace continuity across service versions during rollouts so traces are not broken mid-flight.

### Rollout Implications

- Old and new versions must propagate the same trace context headers — changing propagation format requires a two-phase rollout
- Deploy collector/agent infrastructure updates before application changes that emit new span attributes
- Rolling restarts may cause brief gaps in trace coverage — expected, but verify traces resume within one rollout cycle
- If changing sampling rates, roll out the new rate gradually to avoid overwhelming the collector

### Pre-deploy Checklist

- Verify the trace collector endpoint is reachable from the target environment
- Confirm context propagation format (W3C, B3, Jaeger) matches across all communicating services
