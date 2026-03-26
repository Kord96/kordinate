---
description: Hardcoded URLs — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
## Testing

Verify that all external endpoints are configurable and no URL literals leak into production code paths.

### Unit Tests

- Assert that HTTP client base URLs are read from configuration or environment variables, not hardcoded
- Override endpoint config in tests and verify requests target the overridden URL

### Static Analysis

- Add a CI check that scans source files (excluding tests and docs) for URL-like string literals (`http://`, `https://`)
- Validate that all environment-specific URLs have corresponding entries in config templates or `.env.example`

### Integration Tests

- Deploy to a staging environment with distinct endpoint configuration and verify all service-to-service calls route correctly
- Change a dependency URL via config and confirm the application uses the new address without redeployment
