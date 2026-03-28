---
description: Canary Release — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Route a small percentage of traffic to the new version and promote gradually based on health signals.

### Rollout Implications

- Start with a small traffic slice (1-5%) and increase only after metrics confirm health
- Canary and baseline must run simultaneously — ensure resource capacity for both versions
- Sticky sessions may cause uneven canary exposure; verify traffic distribution is representative

### Pre-deploy Checklist

- Define success criteria (error rate, latency, business metrics) before starting the canary
- Configure automatic rollback triggers tied to the success criteria
- Verify monitoring dashboards compare canary versus baseline side-by-side
