---
description: A/B Experiment Framework — monitoring guidance
type: supplementary
---
## Monitoring

Track experiment assignment, exposure, and metric collection to ensure statistical validity and catch guardrail violations.

### Key Metrics

- `experiment_assignments_total` (counter) — users assigned to each variant, by experiment
- `experiment_exposures_total` (counter) — users actually exposed to the treatment (may differ from assignment)
- `experiment_guardrail_violations_total` (counter) — guardrail metric breaches that should trigger auto-shutdown
- `experiment_metric_samples` (gauge) — sample size per variant to track statistical power accumulation

### Alerts

- Sample ratio mismatch: assignment counts diverge from expected split (indicates a bug in randomization)
- Guardrail metric degradation beyond the pre-set threshold (experiment is causing harm)
- Experiment running past its planned end date without a decision (resource leak)
