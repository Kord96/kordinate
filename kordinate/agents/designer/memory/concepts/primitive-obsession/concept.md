---
description: Primitive Obsession anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
graphable: false
---
# Primitive Obsession

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Email addresses, phone numbers, money amounts, or URLs represented as plain strings
- Currency amounts stored as float or double with no currency code attached
- Coordinates passed as bare tuples or two separate float parameters
- Domain concepts (order ID, user ID, SKU) typed as generic `str` or `int` with no dedicated wrapper
- Validation logic for the same primitive scattered across multiple callers instead of centralized
- Functions accepting `(str, str, int, str)` where each string means something different

### Confidence

- **high** -- the same validation regex for an email or phone appears in 3+ different locations, each operating on a raw string
- **medium** -- money calculations use float arithmetic with ad-hoc rounding scattered across business logic
- **low** -- function signatures use generic types (string, int) for domain concepts but validation is at least centralized

## Impact

No encapsulation of domain rules; validation is repeated everywhere, inconsistently, and invalid values slip through the cracks.

### Symptoms

- The same regex or validation check is copy-pasted across multiple modules
- Invalid values (negative prices, malformed emails) make it into the database
- Functions accept wrong arguments with no type error: user ID passed where order ID was expected
- Arithmetic on money produces floating-point rounding errors
- Refactoring a format change (e.g., phone number format) requires touching dozens of files

### Remediation

- Create value objects or newtypes for each domain concept: `Email`, `Money`, `UserId`, `PhoneNumber`
- Put all validation and parsing in the constructor so invalid instances cannot exist
- Use the type system to prevent mixing up same-typed primitives: `UserId(int)` vs `OrderId(int)`
- Replace float money with a decimal type or integer-cents representation with currency code
- Centralize formatting and comparison logic in the value object rather than in callers
