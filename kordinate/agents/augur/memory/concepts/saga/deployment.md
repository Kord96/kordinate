---
description: Saga — deployment guidance
---
## Deployment

Step ordering and compensation compatibility must be maintained across old and new code versions during rollout.

### Rollout Implications

- In-flight sagas started by old code must be completable by new code — compensation logic must remain backward-compatible
- Adding or reordering saga steps during rollout requires that both old and new step orderings can reach a terminal state
- Saga state persistence format changes need migration before new code deploys — old saga records must be readable by new code
- Rolling back a saga participant service without rolling back the coordinator leaves sagas in an inconsistent state

### Pre-deploy Checklist

- Verify compensation actions for all steps are compatible across old and new code versions
- Confirm saga state store migrations are applied before deploying new coordinator logic
- Check that no long-running sagas are in a mid-step state that would be incompatible with the new step definitions
- Validate timeout values for each step still make sense with the new deployment topology
