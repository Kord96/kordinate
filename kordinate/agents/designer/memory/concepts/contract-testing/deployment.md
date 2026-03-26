---
description: Contract Testing — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Run contract tests as a deploy gate to prevent breaking consumer-provider agreements.

### Rollout Implications

- Provider deploys must pass all consumer contract verifications before promotion
- New consumer contracts should be published before deploying the consumer that depends on them
- Breaking contract changes require coordinated deployment: update consumers first, then provider

### Pre-deploy Checklist

- Verify the contract broker has the latest pacts/contracts from all consumers
- Run provider verification against the pending contracts in CI before deploy
- Confirm no can-i-deploy failures for the target environment
