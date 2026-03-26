---
description: Hardcoded URLs anti-pattern
type: anti-pattern
testable: true
curated: true
scope: global
preloaded: none
---
# Hardcoded URLs

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `http://localhost:8080` or `http://127.0.0.1` in production code paths
- `https://api.example.com` or domain-specific string literals in source files
- IP addresses embedded directly in source code (not config)
- URLs not sourced from config files, environment variables, or service discovery
- Hardcoded port numbers in connection strings outside of configuration
- API base URLs defined as constants in application code rather than injected configuration

### Confidence

- **high** -- a URL string literal containing a hostname or IP address appears in production code (not test fixtures), and there is no corresponding config/env var override mechanism
- **medium** -- URLs are defined as module-level constants in application code rather than read from environment variables or config files
- **low** -- `localhost` or `127.0.0.1` appears in code that might only run in development, but there is no environment-specific override

## Impact

Endpoints cannot be changed without a code deploy, and the application breaks when moving between environments (dev, staging, production).

### Symptoms

- Deploying to a new environment requires code changes instead of config changes
- Staging environment accidentally hits production services (or vice versa)
- Service URL changes require coordinated code deployments across multiple repositories
- Local development requires patching hardcoded URLs or running services on specific ports
- Feature branches cannot point to isolated test instances of dependencies

### Remediation

- Move all URLs and hostnames to environment variables or config files, with sensible defaults for local development only
- Use service discovery (DNS, Consul, Kubernetes service names) instead of hardcoded addresses
- Create a centralized configuration module that reads all external endpoints from the environment at startup
- Add a linting rule or grep check in CI that flags URL-like string literals in source files (excluding tests and documentation)
- For Kubernetes deployments, use ConfigMaps or environment variable injection rather than baked-in URLs

See also: config-management pattern
