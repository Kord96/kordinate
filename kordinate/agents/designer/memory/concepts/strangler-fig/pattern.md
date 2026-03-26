---
description: Strangler Fig architectural pattern
type: pattern
testable: true
distributed: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [lifecycle, architectural]
---
# Strangler Fig

## Recognition

How to identify this pattern in code.

### Signatures

- Routing layer splitting traffic between old and new systems: reverse proxy rules, feature flags, path-based routing
- Proxy or facade in front of legacy: `LegacyProxy`, `MigrationRouter`, Nginx/Envoy route splitting
- Feature-by-feature migration: new service handles some endpoints while legacy handles the rest
- Dual-write during transition: writes to both old and new data stores, reconciliation logic
- Gradual traffic shift: percentage-based routing, canary weights between legacy and replacement
- Anti-corruption layer translating between old and new data models
- Migration toggle: feature flags controlling which system handles each request

### Confidence

- **high** -- routing layer actively splits traffic between legacy and replacement systems with feature-level granularity
- **medium** -- new service exists alongside legacy with some endpoints migrated but no automated traffic shifting
- **low** -- legacy system has a proxy in front of it but no replacement services are receiving traffic yet

## Architecture

Look for a routing layer that incrementally redirects functionality from the legacy system to the replacement, feature by feature.

### Review Checklist

- A routing layer (proxy, gateway, or feature flag) controls which system handles each request
- Each migrated feature can be independently toggled back to legacy if issues arise
- Data consistency is maintained during dual-write periods with reconciliation or event replay
- The legacy system is not modified to accommodate the migration -- the strangler wraps it
- Migration progress is measurable: what percentage of traffic or features have been migrated
- There is a defined end state where the legacy system is fully decommissioned

### Anti-patterns

- Big-bang cutover disguised as strangler fig -- migrating everything at once defeats the purpose
- Dual-write without reconciliation -- data diverges silently between old and new stores
- No rollback path -- migrated features cannot fall back to legacy when problems arise
- Strangler proxy becoming permanent infrastructure with no plan to remove it after migration completes
