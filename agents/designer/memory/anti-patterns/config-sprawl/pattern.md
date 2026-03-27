---
description: Configuration Sprawl anti-pattern
curated: true
scope: global
preloaded: none
---
# Configuration Sprawl

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Config values spread across environment variables AND yaml files AND code constants AND database settings
- No single source of truth for configuration: same logical setting defined in 3+ places
- Same configuration key appears in multiple files with potentially different values
- Config key typos cause silent failures because there is no schema or validation
- Startup code pulls configuration from multiple unrelated sources with no unified loader

### Confidence

- **high** -- the same logical setting (e.g., database URL, timeout value) is defined in 3+ distinct sources with no clear precedence order
- **medium** -- configuration is loaded from 2+ sources (env vars, config file, code defaults) with ad-hoc precedence logic scattered across modules
- **low** -- configuration exists in one primary source but a few hardcoded fallback values in code shadow the intended settings

## Impact

Inconsistent behavior across environments because no one knows which configuration source actually wins.

### Symptoms

- Changing a config value in one place has no effect because another source overrides it
- Different environments behave differently despite "identical" deployments because config sources vary
- Debugging requires checking env vars, config files, database rows, and code defaults to find the effective value
- New team members cannot determine where to change a setting without reading all config-loading code
- Outages caused by config key typos that silently fell back to default values

### Remediation

- Establish a single configuration loader that reads from sources in a documented, deterministic precedence order
- Validate all configuration at startup with a schema that fails fast on missing or invalid values
- Eliminate duplicate definitions: each setting is defined in exactly one canonical source
- Use typed configuration objects that centralize all settings with default values and validation in one module
- Add integration tests that verify configuration loading produces expected values for each environment
