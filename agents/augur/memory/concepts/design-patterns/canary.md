---
kind: concept
name: canary
signatures: {}
type: pattern
abstraction:
- deployment
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

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

### Relationship To Other Concepts

- Related to [blue-green](/concepts/blue-green) as another release strategy, though canary shifts traffic gradually rather than swapping whole environments.
- Related to [feature-flag](/concepts/feature-flag) when deployment rollout and feature exposure are decoupled.
- Related to [health-check](/concepts/health-check) because canary promotion typically depends on automated health and baseline comparison signals.

### Boundary

Use `canary` when a new version is exposed to a small percentage or subset of traffic first, then expanded based on observed behavior.

Do not use it for ordinary rolling deploys or environment swaps. The key signal is gradual exposure with metric-based promotion or rollback.
