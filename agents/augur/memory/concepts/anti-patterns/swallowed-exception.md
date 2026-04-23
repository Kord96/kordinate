---
kind: concept
name: swallowed-exception
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Empty `except:` or `catch {}` blocks with no logging, metrics, or re-raise
- `except Exception: pass` or `catch(e) {}` that silently discard errors
- Error silently ignored with only a `# TODO: handle this` comment
- Catch-all exception handlers that return a default value without recording the failure
- `try/except` wrapped around large blocks of code with a bare `pass` in the handler

### Confidence

- **high** -- empty catch block or `except: pass` with no logging, metric, or alternative action
- **medium** -- catch block returns a default value (null, empty list) without logging the original exception
- **low** -- catch block logs at debug level only, which may be intentional but risks hiding errors in production

## Impact

Failures go completely unnoticed, making debugging impossible because the system silently produces wrong results instead of failing visibly.

### Symptoms

- Users report incorrect data or missing results but the logs show no errors
- Bugs take days to diagnose because the actual failure point left no trace
- System appears healthy by all metrics while silently dropping or corrupting data
- Intermittent issues are impossible to reproduce because the error evidence was discarded
- Technical debt accumulates as `TODO: handle this` comments never get addressed

### Remediation

- At minimum, log every caught exception at an appropriate level (warn for expected, error for unexpected)
- Replace bare `except:` or `catch(Exception)` with specific exception types that you know how to handle
- If an exception is truly ignorable, document explicitly why with a comment and emit a metric for visibility
- Add linting rules that flag empty catch blocks and bare `except:` clauses
- Use the "let it crash" principle: prefer failing loudly over silently returning wrong results

### Relationship To Other Concepts

- Related to [log-and-throw](/concepts/log-and-throw) because both mishandle error propagation, one by duplicating it and the other by hiding it.
- Related to [result-type](/concepts/result-type) when explicit success or failure values would make silent swallowing less likely.
- Related to [hidden-side-effects](/concepts/hidden-side-effects) because suppressed failures make state changes and operational consequences difficult to see.

### Boundary

Use `swallowed-exception` when an error is caught and then suppressed or ignored without meaningful propagation, handling, or visibility.

Do not use it for deliberate, documented best-effort cleanup where failure is intentionally and safely non-fatal.
