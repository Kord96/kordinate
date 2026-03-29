---
description: Backend for Frontend — deployment guidance
type: supplementary
---
## Deployment

Each BFF can be deployed independently, but coordinate with client release schedules.

### Rollout Implications

- BFF changes may need to align with mobile app releases — old clients may call deprecated BFF endpoints
- Deploy BFF updates before or alongside the client that depends on new response shapes
- Multiple BFF instances can coexist — version endpoints to support gradual client migration

### Pre-deploy Checklist

- Verify backward compatibility with the oldest supported client version
- Confirm upstream service dependencies are available in the target environment
