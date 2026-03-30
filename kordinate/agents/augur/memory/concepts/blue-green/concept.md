---
description: Blue-Green Deployment architectural pattern
type: pattern
observable: true
distributed: true
graphable: true
abstraction: [deployment]
---
# Blue-Green Deployment

## Recognition

How to identify this pattern in code.

### Signatures

- Two identical environments labeled `blue`/`green` or `active`/`standby`
- Traffic switching via DNS, load balancer, or service selector swap
- Environment variables like `DEPLOY_ENV=blue`, `ACTIVE_SLOT=green`
- K8s: duplicate Deployment manifests with Service selector toggling between label values
- Infrastructure-as-code with mirrored environment blocks (Terraform workspaces, duplicate modules)
- Health check validation on standby before traffic switch

### Confidence

- **high** -- two parallel deployments with identical specs differing only by environment label, plus a traffic switch mechanism
- **medium** -- blue/green naming in manifests or CI/CD pipeline stages, LB target group swaps
- **low** -- two environments exist but no automated switch mechanism is visible

## Architecture

Look for paired environments with an atomic traffic cutover and rollback path.

### Review Checklist

- Both environments are truly identical (same image, config, resource limits)
- Traffic switch is atomic (no period where both receive production traffic unintentionally)
- Database migrations are backward-compatible (both versions must work during switch window)
- Rollback procedure is tested and can revert traffic to the previous environment quickly
- Health checks validate the standby environment before the switch executes

### Anti-patterns

- Database schema changes that break the old version (no backward compatibility)
- Manual traffic switching with no automation or runbook
- Letting the idle environment drift in configuration or fall behind on patches
- No smoke tests on the standby environment before switching traffic
