---
kind: concept
name: infrastructure-as-code
signatures: {}
type: pattern
abstraction:
- infrastructure
- deployment
scope: backend
status: primary
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [gitops](/concepts/gitops) when declarative infrastructure and deployment state are reconciled directly from version control.
- Related to [immutable-infra](/concepts/immutable-infra) because IaC commonly provisions or replaces immutable environments and artifacts.
- Related to [config-management](/concepts/config-management) when environment-specific values and infra parameters are managed centrally alongside infra definitions.

### Boundary

Use `infrastructure-as-code` when infrastructure is declared, versioned, and applied from source-controlled definitions instead of being created manually.

Do not use it for any deployment script. The important signal is declarative or managed infrastructure definition as code.
