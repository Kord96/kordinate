---
description: Magic Numbers/Strings anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - boolean-blindness
  - stringly-typed
  - inconsistent-naming
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Magic Numbers/Strings

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Hardcoded numeric values with no explanation (`if count > 42`)
- Timeout or delay values inline with no named constant (`sleep(3.5)`)
- Array indices used as business logic (`data[7]` to mean "the address field")
- String literals used as identifiers or keys across multiple files without a shared definition
- Conditional thresholds with no documentation of why that specific value was chosen

### Confidence

- **high** -- numeric literals appear in business logic conditionals or configurations with no accompanying constant name or comment
- **medium** -- inline numeric values in function calls (timeouts, retries, sizes) without named constants
- **low** -- a single hardcoded value in a localized context that could reasonably be extracted but is not yet duplicated

## Impact

Unreadable code where the intent behind values is lost, making consistent changes across the codebase error-prone.

### Symptoms

- Developers cannot understand why a specific number was chosen without git archaeology
- Changing a business rule threshold requires finding and updating the same number in multiple locations
- Bugs arise from updating the value in one place but missing another occurrence
- Code reviews cannot assess correctness because the meaning of the number is opaque
- Tests embed the same magic values, creating brittle assertions coupled to unexplained constants

### Remediation

- Extract every non-obvious literal into a named constant with a descriptive name (`MAX_RETRY_ATTEMPTS = 3`)
- Group related constants in a dedicated configuration module or constants file
- Add a brief comment or docstring explaining the rationale when the value itself is not self-evident
- Use configuration files or environment variables for values that may differ across environments
- Add linting rules that flag raw numeric and string literals in conditional expressions and function arguments

### Relationship To Other Concepts

- Related to [boolean-blindness](/concepts/boolean-blindness) because both hide intent in primitive values rather than explicit names or types.
- Related to [stringly-typed](/concepts/stringly-typed) when unexplained strings act as the implicit schema for important behavior.
- Related to [inconsistent-naming](/concepts/inconsistent-naming) because unnamed literals and drifting terminology both erode semantic clarity.

### Boundary

Use `magic-numbers` when hardcoded numeric or string literals carry hidden business meaning that should be expressed explicitly.

Do not use it for universally obvious literals like `0`, `1`, or protocol-defined constants that are already made clear by context.
