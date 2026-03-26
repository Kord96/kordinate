---
description: Micro-Frontend — deployment guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Deployment

Deploy micro-frontends independently while ensuring shared dependencies and the shell remain compatible.

### Rollout Implications

- Each micro-frontend should be independently deployable without requiring a full application redeploy
- Shared dependency versions (React, Angular) must be compatible across all deployed micro-frontends
- The shell application must handle missing or failed micro-frontend loads gracefully (error boundaries)
- Version the contract between shell and micro-frontends to detect breaking changes before deployment

### Pre-deploy Checklist

- Verify shared dependency versions are aligned across all micro-frontends and the shell
- Test the new micro-frontend version in isolation and composed within the shell before production
- Confirm import map or Module Federation remote URLs point to the correct deployment target
- Validate that CSS scoping prevents style leaks between the new version and existing micro-frontends
