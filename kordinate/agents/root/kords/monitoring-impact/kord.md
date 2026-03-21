---
description: Monitoring impact assessment for infrastructure changes
requester: deployer
provider: sauron
---

## Provider Guidelines

Assess monitoring coverage for the affected service.
Report gaps, not what's already working.
Keep under 50 lines.

### Response Format

| Field | Required |
|-------|----------|
| Gaps by severity (blocking, warning, info) | yes |
| Missing dashboards or metrics | yes |
| Missing alerts | yes |
| Summary | no |
