---
description: Infrastructure as Code — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Validate infrastructure definitions before apply to catch misconfigurations and drift early.

### Unit Tests

- Validate IaC templates with linters (`tflint`, `cfn-lint`, `pulumi preview`) and assert zero errors
- Test Terraform modules with `terraform validate` and plan output assertions
- Assert that no secrets or credentials appear in `.tf`, template, or overlay files

### Integration Tests

- Apply infrastructure to an ephemeral environment and verify all resources are created as expected
- Run drift detection against a known-good state and assert no out-of-band changes
- Destroy and recreate the environment to verify full reproducibility from code

### Policy Tests

- Use OPA/Rego or Sentinel policies to enforce tagging, encryption, and network rules on plan output
- Validate that state is stored remotely with locking enabled (not committed to git or stored locally)
