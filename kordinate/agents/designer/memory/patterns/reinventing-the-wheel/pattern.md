---
description: Reinventing the Wheel anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Reinventing the Wheel

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Custom JSON parser when `json.loads()` or equivalent exists
- Custom HTTP client wrapping raw sockets instead of using `requests`, `httpx`, or `fetch`
- Custom retry logic reimplementing exponential backoff instead of using `tenacity`, `resilience4j`, or similar
- Custom logging framework instead of the language's standard logging library
- Hand-rolled ORM or query builder instead of using established libraries
- Reimplemented standard library functions (custom `deepcopy`, `uuid`, `base64`, string formatting)

### Confidence

- **high** -- a module reimplements functionality that is available in the standard library or a widely-adopted, well-maintained library, and the custom version lacks edge case handling present in the established solution
- **medium** -- a utility module provides functionality (retry, caching, validation) that overlaps significantly with a popular library already in the project's dependency tree
- **low** -- a helper function reimplements a small piece of standard library functionality, possibly for a legitimate reason (performance, reduced dependencies) but without documentation of the rationale

## Impact

Bugs in already-solved problems, ongoing maintenance burden, and missing edge cases that battle-tested libraries handle correctly.

### Symptoms

- Custom implementations break on edge cases (Unicode, timezone, encoding) that standard libraries handle
- Team members spend time maintaining infrastructure code instead of business logic
- Security vulnerabilities in custom crypto, parsing, or serialization code
- New developers are confused by bespoke utilities instead of recognizable standard patterns
- Bug reports trace back to reimplemented functionality rather than business logic

### Remediation

- Audit utility and infrastructure code for overlap with standard library or well-established packages
- Replace custom implementations with standard libraries, documenting any edge cases that motivated the original code
- If a custom implementation is justified (performance, zero-dependency constraint), document the rationale and add comprehensive tests covering known edge cases
- Add dependency review to the design phase: before writing a utility, check if a maintained solution exists
- Create a "build vs. buy" decision log for infrastructure components so the rationale is preserved
