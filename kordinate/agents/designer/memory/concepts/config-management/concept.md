---
description: Configuration Management architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
abstraction: [infrastructure, lifecycle]
---
# Configuration Management

## Recognition

How to identify this pattern in code.

### Signatures

- 12-factor config via environment variables (`os.environ`, `process.env`, `std::env`)
- Config files in YAML, TOML, JSON, or INI format (`config.yaml`, `settings.toml`)
- Config server or centralized config service (Spring Cloud Config, etcd, Consul KV)
- `settings.py`, `config.py`, `application.yml`, `.env` files with `dotenv` loading
- Feature toggles and feature flag systems (`LaunchDarkly`, `Unleash`, custom flags)
- Hierarchical config with overrides (default -> environment -> instance)
- Config validation at startup with fail-fast on missing required values
- Java: Quarkus `@ConfigMapping`, `@ConfigProperty`, `SmallRye Config` with profile support
- Java: Micronaut `@ConfigurationProperties`, `@Property`
- Java: Dropwizard `Configuration` class hierarchy with YAML loading and validation
- Java: Custom config loaders (e.g., light-4j `Config.getInstance().getJsonMapConfig()`)

### Negative signals (not sufficient for detection)

- Java: Simple `@Value` injection or `@ConfigurationProperties` on a single class without profile-based overrides or config hierarchy is standard Spring usage, not an architectural config management pattern
- Mere presence of `application.yml` or `application.properties` is standard framework configuration
- Only flag when there is deliberate config architecture: multiple profiles, config server, hierarchical overrides, or config validation

### Confidence

- **high** -- Structured config loading with environment-specific overrides, validation at startup, and no hardcoded values in business logic
- **medium** -- Environment variables or config files loaded at startup but without formal validation or override hierarchy
- **low** -- Scattered hardcoded constants with some values extracted to a config file as an afterthought

## Architecture

Look for config separated from code, loaded once at startup, validated early, and injected into components rather than globally accessed.

### Review Checklist

- All environment-specific values are externalized (no hardcoded URLs, ports, or credentials in code)
- Config is validated at startup -- missing or malformed values cause a clear failure, not a runtime surprise
- Override hierarchy is well-defined (defaults < environment < instance < explicit overrides)
- Secrets are handled separately from plain config (not in the same config file)
- Config changes can be applied without code changes or redeployment where appropriate
- Feature flags have a defined lifecycle (creation, rollout, cleanup after full adoption)

### Anti-patterns

- Secrets stored in plain config files alongside non-sensitive configuration
- No validation -- missing config values cause cryptic runtime errors instead of startup failures
- Config scattered across multiple mechanisms (env vars, files, hardcoded) with no clear precedence
- Feature flags that never get cleaned up, accumulating as permanent conditional branches
