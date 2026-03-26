---
description: Canary Release architectural pattern
type: pattern
observable: true
distributed: true
curated: true
scope: global
preloaded: none
---
# Canary Release

## Recognition

How to identify this pattern in code.

### Signatures

- Traffic splitting with explicit percentages (e.g., 5%, 10%, 50%, 100%)
- Canary annotations in K8s manifests or Ingress resources
- Istio `VirtualService` with traffic weights between stable and canary subsets
- Argo Rollouts `Rollout` resources with `canary` strategy and `steps`
- Flagger `Canary` CRDs with `stepWeight` and `maxWeight` fields
- Metrics comparison logic between canary and stable (error rate, latency thresholds)
- CI/CD pipeline stages named `canary-deploy`, `canary-promote`, `canary-rollback`

### Confidence

- **high** -- traffic weight configuration with gradual step increments and automated promotion/rollback based on metrics
- **medium** -- canary-labeled deployments or pods alongside stable, manual promotion steps in pipeline
- **low** -- separate deployment for a subset of traffic but no automated analysis or rollback

## Architecture

Look for gradual traffic shifting with metrics-driven promotion or rollback decisions.

### Review Checklist

- Promotion criteria are defined with measurable thresholds (error rate, p99 latency)
- Automatic rollback triggers on metric degradation before reaching full traffic
- Canary and stable run the same configuration except for the image version
- Metrics comparison uses a statistically meaningful sample size and time window
- Canary traffic percentage steps are small enough to limit blast radius

### Anti-patterns

- Promoting canary based on time alone without checking metrics
- Starting canary at too high a percentage (defeats the purpose of gradual rollout)
- No automated rollback -- relying on human intervention to catch regressions
- Comparing canary metrics against static thresholds instead of the live stable baseline
