---
description: A/B Experiment Framework — testing guidance
type: supplementary
---
## Testing

Verify deterministic assignment, correct metric attribution, and guardrail enforcement.

### Unit Tests

- Assert that the same user ID always maps to the same variant (deterministic hashing)
- Verify mutual exclusion: a user in one experiment layer cannot be assigned to conflicting experiments
- Test that exposure logging fires only when the user actually sees the treatment, not just on assignment
- Assert guardrail checks evaluate correctly and return a shutdown signal when thresholds are breached

### Integration Tests

- Run an experiment end-to-end: assign users, expose them to variants, collect metrics, and verify the results pipeline produces correct aggregates
- Test experiment lifecycle: create, activate, pause, resume, and conclude — each state transition should behave as documented
- Verify that feature flags tied to experiments respect the experiment assignment rather than their standalone rollout percentage

### Statistical Tests

- Run the assignment algorithm over a large synthetic population and verify variant splits match the configured ratio within expected variance
- Test that metric collection correctly attributes conversions to the variant the user was exposed to at the time of the action
