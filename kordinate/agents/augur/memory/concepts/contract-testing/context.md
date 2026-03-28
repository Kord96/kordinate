## Testing

Verify consumer expectations match provider capabilities using shared contract artifacts.

### Unit Tests

- Consumer side: generate a contract (pact) from consumer tests that define expected request/response pairs
- Provider side: replay the consumer contract against the real provider and verify all interactions pass
- Test contract evolution: add a new field on the provider and verify existing consumer contracts still pass

### Integration Tests

- Publish contracts to a broker and run provider verification in CI against all registered consumer contracts
- Test can-i-deploy: verify the broker correctly reports deployment safety based on verification results

### Failure Injection

- Introduce a breaking change on the provider and verify the contract test fails before deployment

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

