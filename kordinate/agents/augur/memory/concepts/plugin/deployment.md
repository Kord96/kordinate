---
description: Plugin Architecture — deployment guidance
---
## Deployment

Plugin compatibility during rolling updates depends on interface versioning and registration order.

### Rollout Implications

- Core and plugin versions must be compatible — deploying a new core version may break plugins that depend on the old interface
- Plugin registration order can create startup race conditions during rolling updates if plugins depend on each other
- Rolling restart may temporarily leave some pods with the old plugin set and others with the new — verify both sets are functional
- Hot-reloading plugins at runtime requires careful lifecycle management to avoid resource leaks

### Pre-deploy Checklist

- Verify all loaded plugins are compatible with the target core plugin interface version
- Confirm plugin registration order is deterministic and does not depend on pod startup timing
- Test that the core functions correctly if a plugin fails to load (graceful degradation)
