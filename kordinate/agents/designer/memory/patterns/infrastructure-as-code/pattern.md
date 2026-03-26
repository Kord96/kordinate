---
description: Infrastructure as Code architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Infrastructure as Code

## Recognition

How to identify this pattern in code.

### Signatures

- Declarative infrastructure definitions in version-controlled files
- Terraform `.tf` files with `resource`, `data`, and `module` blocks
- Pulumi programs defining infrastructure in a general-purpose language
- CloudFormation templates (`.yaml`/`.json` with `AWSTemplateFormatVersion`)
- Ansible playbooks and roles (`tasks/main.yml`, `playbook.yml`)
- `terraform plan`, `terraform apply`, `pulumi up` in CI/CD pipelines
- State files (`terraform.tfstate`, `pulumi.stack.json`)
- Resource definitions with explicit dependencies and lifecycle rules

### Confidence

- **high** -- all infrastructure defined in versioned declarative files with automated apply via CI/CD
- **medium** -- infrastructure files exist but some resources are still created manually or out of band
- **low** -- scripts that call cloud APIs imperatively but are version-controlled

## Architecture

Look for all infrastructure defined declaratively in version control with automated, reproducible provisioning.

### Review Checklist

- All infrastructure is defined in code -- no manually created resources outside the IaC scope
- State is stored remotely with locking (S3+DynamoDB, GCS, Terraform Cloud)
- Changes go through plan/review before apply -- no direct `apply` without review
- Secrets are not stored in IaC files -- referenced via secret manager or external store
- Modules are used to avoid duplication across environments
- Drift detection is in place to catch out-of-band changes

### Anti-patterns

- State file committed to git or stored locally without locking
- Hardcoded secrets or credentials in `.tf` or template files
- No plan step -- applying changes directly without previewing the diff
- Snowflake environments with copy-pasted configs instead of parameterized modules
