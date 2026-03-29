---
description: ETL — deployment guidance
---
## Deployment

Job scheduling and bookmark state must be coordinated to avoid partial loads or duplicate processing.

### Rollout Implications

- Deploying new transform logic while a job is running may cause the in-flight job to produce inconsistent output — pause scheduling before rollout
- Bookmark/checkpoint format changes require migration — new code reading old bookmarks must handle the previous format
- Schema changes in the load target (new columns, type changes) must be applied before new ETL code deploys
- Parallel job execution during rollout can cause duplicate loads if both old and new versions process the same bookmark window

### Pre-deploy Checklist

- Verify no ETL jobs are currently running or scheduled to start during the deployment window
- Confirm bookmark/checkpoint state is compatible with the new code version
- Validate that target schema migrations are applied before deploying new transform or load logic
