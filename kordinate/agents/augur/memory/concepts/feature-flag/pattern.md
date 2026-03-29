---
description: Feature Flag/Toggle architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [deployment, design]
---
# Feature Flag/Toggle

## Recognition

How to identify this pattern in code.

### Signatures

- Conditional checks like `if feature_enabled("X")`, `is_feature_on()`, `hasFeature()`
- Feature flag configuration files (JSON/YAML with flag names and boolean/percentage values)
- `FEATURE_*` environment variables controlling behavior toggles
- SDK imports: LaunchDarkly (`ldclient`), Unleash (`unleash-client`), Flagsmith, Split
- Remote flag evaluation endpoints or polling for flag state changes
- Flag context objects passing user attributes for targeting rules

### Confidence

- **high** -- feature flag SDK initialized with flag evaluation calls gating code paths, plus a flag management config or service
- **medium** -- `FEATURE_*` env vars or config-file-driven toggles controlling conditional branches
- **low** -- simple boolean config values that enable/disable behavior but lack flag lifecycle management

## Architecture

Look for code paths gated by externally managed toggles with clean separation between flagged and unflagged behavior.

### Review Checklist

- Flags have clear ownership and a planned removal date (no permanent feature flags)
- Flag evaluation has a sensible default when the flag service is unavailable
- Code paths for both flag states are tested independently
- Flag naming convention is consistent and descriptive
- Stale flags are tracked and cleaned up regularly
- Targeting rules are reviewed for correctness (percentage rollouts, user segments)

### Anti-patterns

- Flags that never get removed, accumulating permanent conditional complexity
- Nested feature flags creating combinatorial explosion of code paths
- Using feature flags for configuration that should be in application config
- No default behavior when the flag service is unreachable
