---
description: Pokemon Exception anti-pattern
curated: true
scope: global
preloaded: none
---
# Pokemon Exception

## Recognition

How to identify this anti-pattern in code.

### Signatures

- `except:` or `except Exception:` catching everything in Python
- `catch(Exception e)` or `catch(Throwable t)` without filtering in Java
- `catch(...)` in C++
- `rescue => e` with no specific exception class in Ruby
- Bare `catch {}` blocks in C# or JavaScript swallowing all errors
- Catching `KeyboardInterrupt`, `SystemExit`, or `OutOfMemoryError` accidentally because the catch is too broad

### Confidence

- **high** -- bare `except:` or `catch(Exception)` with no re-raise, combined with a pass/empty block or generic logging
- **medium** -- broad catch exists but logs the error and continues execution without filtering exception types
- **low** -- catch-all exists but re-raises after cleanup (may be intentional)

## Impact

Masks real errors, prevents clean shutdown on signals, and makes debugging nearly impossible because failures are silently swallowed.

### Symptoms

- Application hangs or behaves incorrectly but no errors appear in logs
- Ctrl+C or SIGTERM fails to stop the process because KeyboardInterrupt is caught
- Corrupted state persists because exceptions that should have rolled back transactions were swallowed
- Developers add increasingly desperate logging because they cannot find where errors go
- Production incidents take hours to diagnose because the real exception was eaten

### Remediation

- Catch only the specific exceptions you know how to handle: `except ValueError` not `except Exception`
- Always re-raise exceptions you cannot fully handle: `except Exception: log(); raise`
- Never catch `BaseException` in Python or `Throwable` in Java unless implementing a top-level error boundary
- Use a top-level exception handler (middleware, main loop) for truly unexpected errors, not scattered catch-alls
- Add linting rules (e.g., pylint `broad-except`, SonarQube rules) to flag overly broad catches in CI
