---
description: Boolean Blindness anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Boolean Blindness

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Functions taking 3 or more boolean parameters: `create(true, false, true)`
- Boolean arguments with no name visible at the call site, making intent unclear
- Parameters named `flag1`, `flag2`, `flag3` or single-letter booleans
- Long chains of `if flag_a and not flag_b or flag_c` with no explanation of what the combination means
- Functions where adding a new option means adding another boolean parameter

### Confidence

- **high** -- a function call passes 3+ boolean literals with no keyword names: `process(true, false, true, false)`
- **medium** -- a function signature has 2 boolean parameters and callers never use keyword arguments
- **low** -- a boolean parameter exists but is always called with a named argument or has a self-documenting name

## Impact

Unreadable call sites where the meaning of each `true`/`false` is invisible, leading to subtle errors when arguments are swapped or misunderstood.

### Symptoms

- Developers must jump to the function definition to understand what each boolean means at every call site
- Arguments accidentally swapped (both are bool, compiler does not catch it) cause silent logic errors
- Adding a new boolean option to an existing function creates a combinatorial explosion
- Code reviews cannot verify correctness without cross-referencing the function signature
- Boolean parameters accumulate over time as quick fixes for "just one more flag"

### Remediation

- Replace boolean parameters with enums or named constants: `Mode.STRICT` instead of `True`
- Use a configuration object or builder pattern when a function needs multiple options
- In languages that support it, require keyword-only arguments for booleans: `def create(*, strict: bool, verbose: bool)`
- Split the function into separate methods if the booleans select fundamentally different behavior
- As a minimum, always use named arguments at call sites: `create(strict=True, validate=False)`
