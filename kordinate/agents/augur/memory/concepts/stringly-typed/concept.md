---
description: Stringly Typed anti-pattern
type: anti-pattern
graphable: false
---
# Stringly Typed

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Strings used where enums or types should be (`status = "active"` instead of an enum)
- String comparison for branching logic (`if type == "admin"`)
- String parsing to extract structured data (`role.split(":")[1]`)
- Magic string constants scattered across multiple files with no single definition
- Function parameters typed as `str`/`string` that only accept a fixed set of known values

### Confidence

- **high** -- the same string literal appears in 3+ files for comparison or branching, with no enum or constant definition
- **medium** -- function signatures accept `string` for parameters that have a known, finite set of valid values
- **low** -- string literals used for status or type fields in a single module without a defining constant

## Impact

No compile-time safety; typos in string values cause silent runtime bugs that slip past code review.

### Symptoms

- A misspelled string (`"actve"` instead of `"active"`) causes a bug that only surfaces in specific code paths
- Renaming a status value requires a project-wide search-and-replace with no compiler assistance
- IDE autocomplete and refactoring tools cannot help because values are opaque strings
- Tests must cover every string variant manually since the type system provides no exhaustiveness checking
- Code review cannot catch invalid string values without memorizing the allowed set

### Remediation

- Replace string literals with enums, union types, or constant objects defined in a single location
- Use typed enums that the compiler can check for exhaustiveness in switch/match statements
- Introduce a validation layer at system boundaries that converts incoming strings to typed values immediately
- Add linting rules that flag raw string comparisons against known domain values
- For languages without enums, define a frozen set or constant map as the single source of truth
