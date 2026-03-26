---
description: Contract Testing architectural pattern
type: pattern
testable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# Contract Testing

## Recognition

How to identify this pattern in code.

### Signatures

- Pact files (`.json` contracts) in a `pacts/` or `contracts/` directory
- `@Pact`, `@PactVerification` annotations in Java/Kotlin tests
- `pact-jvm`, `pact-js`, `pact-python`, `pact-go` library imports
- Consumer-driven contract definitions with `interaction()` or `upon_receiving()`
- Provider verification test suites that replay contracts against a running service
- Contract broker configuration (Pact Broker URL, publish/verify steps in CI)
- Spring Cloud Contract DSL files (`.groovy` or `.yml` stubs)

### Confidence

- **high** — Pact contract files present with both consumer-side generation and provider-side verification tests
- **medium** — Contract broker configured in CI but only one side (consumer or provider) has tests
- **low** — API schema validation (OpenAPI) in tests without explicit consumer-driven contracts

## Architecture

Look for bidirectional contract verification: consumers define expectations, providers verify against them.

### Review Checklist

- Consumer tests generate contracts that are published to a broker or shared artifact store
- Provider verification tests run against the latest contracts from all consumers
- Contract versions are tied to git commits or semantic versions for traceability
- Breaking changes are caught before deployment via CI contract checks (can-i-deploy gates)
- Contracts cover error responses and edge cases, not just happy paths
- Provider states are set up explicitly so verification runs against realistic conditions

### Anti-patterns

- Only testing the happy path in contracts, missing error and edge-case interactions
- Contracts maintained manually instead of generated from consumer tests
- Provider verification skipped in CI, running only locally
- Tight coupling in contracts that specify implementation details (exact headers, timestamps) instead of semantic content
