---
kind: concept
name: abstract-factory
signatures: {}
type: pattern
abstraction:
- design
scope: backend
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Family of related objects created through a factory interface
- `*Factory` interfaces with multiple `create*()` methods producing related types
- Theme factories (light theme factory, dark theme factory producing consistent widget sets)
- Platform-specific widget factories (Windows, macOS, Linux UI component creation)
- Factory selection based on configuration or runtime environment
- Concrete factories implementing a shared factory interface with consistent product families

### Confidence

- **high** -- Factory interface with multiple `create*()` methods, concrete factory implementations producing families of related objects, factory selected at configuration time
- **medium** -- Factory class producing multiple related objects but without a formal factory interface hierarchy
- **low** -- Single `create()` factory method that returns one type (closer to factory method than abstract factory)

## Architecture

Look for a factory interface that produces families of related objects, with concrete factories swapped to change the entire product family.

### Review Checklist

- All products within a family are consistent and compatible with each other
- New product families can be added by implementing the factory interface without modifying existing code
- Factory selection is centralized (configuration, environment, or dependency injection)
- Products created by the factory are used through their abstract interfaces, not concrete types
- Adding a new product type to the family requires updating all concrete factories (understand the cost)
- Factory does not accumulate unrelated creation methods (stays focused on one product family)

### Anti-patterns

- Factory producing unrelated objects that do not form a coherent family
- Client code depending on concrete product types instead of abstractions
- Single concrete factory with conditional logic instead of polymorphic factory hierarchy
- Over-engineering with abstract factory when only one product family will ever exist

### Relationship To Other Concepts

- Related to [builder](/concepts/builder) because both abstract object creation, though abstract factory chooses product families while builders assemble one product step by step.
- Related to [factory](/concepts/factory) as the simpler creation pattern from which abstract factory generalizes to coherent product families.
- Related to [bridge](/concepts/bridge) when families of implementations vary independently from the abstractions that consume them.

### Boundary

Use `abstract-factory` when clients create related families of objects through an abstract creation interface without binding to concrete implementations.

Do not use it for any helper with multiple factory methods. The key signal is creation of coherent product families behind an abstract boundary.
