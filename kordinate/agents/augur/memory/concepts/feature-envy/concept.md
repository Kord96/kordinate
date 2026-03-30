---
description: Feature Envy anti-pattern
type: anti-pattern
testable: true
graphable: false
---
# Feature Envy

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Methods that access more fields from another class than from their own class
- Getter chains to extract data from other objects (`order.customer.address.city`)
- Utility methods that should live on the data class they operate on
- Functions taking an object as a parameter and accessing 3+ of its attributes
- Methods that destructure or unpack another object's internals to perform logic
- Static methods or free functions that operate entirely on another class's data
- Long parameter lists where all parameters come from a single other object

### Confidence

- **high** -- a method accesses 4+ fields of another class and 0-1 fields of its own, and this pattern repeats across multiple methods
- **medium** -- a method primarily operates on data from one other object, using getter chains or attribute access
- **low** -- a utility function takes an object and reads a couple of its fields, but the logic may legitimately belong elsewhere

## Impact

Misplaced responsibility and tight coupling, where behavior lives apart from the data it operates on, making both classes harder to change independently.

### Symptoms

- Changing a class's internal structure breaks methods in other unrelated classes
- Logic for a concept is scattered across multiple classes instead of being cohesive
- Getter methods exist solely to support external methods that should be internal
- Refactoring one class requires updating logic in distant modules
- Duplicated logic appears because multiple classes implement similar operations on the same data

### Remediation

- Move the method to the class whose data it primarily uses
- If the method uses data from multiple classes, extract the shared logic into the data-owning class and call it
- Replace getter chains with methods that encapsulate behavior (Tell, Don't Ask)
- Eliminate trivial getters by moving the computation to the data class
- Apply the Information Expert principle: assign responsibility to the class with the information needed to fulfill it
