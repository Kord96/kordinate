# Testing

- Test routing layer toggle: verify requests route to legacy or new system based on feature flag state
- Test rollback by toggling a migrated feature back to legacy and confirming correct behavior
- Verify data consistency during dual-write periods with reconciliation tests comparing both stores
- Test the anti-corruption layer translating between old and new data models in both directions
- Integration test each migrated feature against both the legacy and new system to confirm parity
- Test that the legacy system is not modified — the strangler wraps it without code changes
- Load test the routing layer to verify it does not become a bottleneck as more features are migrated
- Test the end state: all features migrated, legacy fully removed, routing layer decommissioned

# Deployment

- Deploy the routing layer (proxy, gateway, feature flag) before migrating any features
- Migrate one feature at a time — deploy the new service, route traffic, verify, then move to the next
- Ensure each migrated feature has an independent rollback toggle to fall back to legacy
- Coordinate dual-write deployments carefully: both old and new stores must be written simultaneously
- Run reconciliation checks during dual-write periods to detect data drift between old and new stores
- Track migration progress as a deployment metric: percentage of traffic or features on the new system
- Plan for decommissioning the legacy system — do not let the strangler proxy become permanent infrastructure

