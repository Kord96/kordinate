---
kind: concept
name: error-code-returns
signatures: {}
source:
  memory_concept: memory/catalog/concepts/error-code-returns.md
type: anti-pattern
abstraction: []
scope: backend
status: supporting
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Functions returning -1, 0, or 1 to indicate success/failure instead of using exceptions or Result types
- Functions returning `null`/`None`/`nil` for error conditions with no way to distinguish "not found" from "failed"
- Caller code checking `if result == -1` or `if result is None` after every call
- C-style error handling idioms in languages that have exceptions (Python, Java, C#, Ruby)
- Magic sentinel values: `return ""` for error, `return -999` for missing data
- Functions with return type documented as "returns X or null on error"

### Confidence

- **high** -- a function in Python/Java/Ruby returns -1 or null for errors, and callers check the return value with comparisons instead of try/catch
- **medium** -- functions return None for both "not found" and "error occurred" with no way to distinguish the two
- **low** -- a function returns a boolean success flag alongside the actual result via output parameter or tuple

## Impact

Unchecked error codes lead to silent failures, because nothing forces the caller to inspect the return value before proceeding.

### Symptoms

- Bugs manifest far from the actual failure point because the error code was ignored
- Null/None propagates through multiple layers before finally causing a crash
- Code is littered with `if result == -1` checks that are easy to forget
- Error handling is inconsistent: some callers check, some do not
- Impossible to distinguish between a legitimate return value and an error sentinel

### Remediation

- Use the language's native error mechanism: exceptions in Python/Java/Ruby, Result/Either types in Rust/Haskell/Kotlin
- Replace null returns with Optional/Maybe types that force the caller to handle the empty case
- If error codes are unavoidable (C, Go), use a consistent struct or tuple: `(result, error)` not magic values
- Wrap legacy error-code APIs in an adapter that throws exceptions for your application code
- Add static analysis rules to flag unchecked return values from functions known to return error codes

### Relationship To Other Concepts

- Related to [result-type](/concepts/result-type) as a stronger alternative that models success and failure explicitly in the type system.
- Related to [swallowed-exception](/concepts/swallowed-exception) because both can hide failure semantics from callers or observability systems.
- Related to [magic-numbers](/concepts/magic-numbers) when sentinel error values rely on undocumented numeric conventions.

### Boundary

Use `error-code-returns` when APIs communicate failure through sentinel values or numeric codes instead of structured error outcomes.

Do not use it for deliberate low-level C-style interfaces where explicit code returns are the intended contract.
