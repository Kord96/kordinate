---
description: Breaking Changes anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Breaking Changes

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Removed fields from API responses without a deprecation period
- Changed response types (string to integer, object to array) in existing endpoints
- Renamed endpoints or changed URL paths with no version bump
- No API versioning strategy: no `/v1/`, `/v2/` prefix, no `Accept` header versioning
- Clients breaking after every deploy due to contract changes
- Database column renames or type changes that break existing queries from other services

### Confidence

- **high** -- fields removed or types changed in a response schema with no version increment and no deprecation notice
- **medium** -- an API versioning scheme exists but breaking changes are shipped within the same version
- **low** -- additive changes (new optional fields) are introduced, which are usually safe but not always

## Impact

Downstream failures and broken integrations every time the API changes, eroding trust and forcing consumers to pin to old versions or break.

### Symptoms

- Consumer applications crash or show errors after an API deployment they were not warned about
- Multiple teams spend time debugging the same breaking change independently
- API consumers refuse to upgrade because previous upgrades broke them
- Changelog is empty or vague, giving no indication of what changed
- Integration test suites that worked yesterday fail today with deserialization errors

### Remediation

- Adopt a versioning strategy (URL path, header, or query parameter) and increment the version for any breaking change
- Deprecate fields before removing them: mark as deprecated, wait one or more release cycles, then remove
- Use additive-only changes within a version: new fields are optional, old fields remain
- Publish a machine-readable API schema (OpenAPI, Protobuf) and run contract tests in CI
- Notify consumers proactively through changelogs, migration guides, or deprecation headers in responses
