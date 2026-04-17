---
description: God Object/Class anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - big-ball-of-mud
  - god-endpoint
  - feature-envy
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# God Object/Class

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Classes exceeding 1000 lines of code
- Classes with 20+ public methods
- A single class importing from nearly every package in the project
- Methods touching unrelated concerns (e.g., HTTP handling, database access, email sending, and PDF generation in one class)
- Class names containing "Manager", "Handler", "Processor", "Utils", or "Helper" that accumulate all miscellaneous logic
- Instance variables numbering 15+ covering disparate domains

### Confidence

- **high** -- class has 1000+ lines, 20+ methods, and imports from 5+ unrelated packages
- **medium** -- class has 500+ lines with methods spanning multiple domains (I/O, business logic, presentation)
- **low** -- class name is generic ("AppManager", "MainService") and growing steadily over time

## Impact

Impossible to test, modify, or understand in isolation because the class owns too many responsibilities.

### Symptoms

- Unit tests require mocking dozens of dependencies to instantiate the class
- Every feature change touches the same file, causing constant merge conflicts
- New team members cannot understand what the class is responsible for
- A bug fix in one area of the class introduces regressions in unrelated functionality
- The class is the most-changed file in git history

### Remediation

- Identify distinct responsibilities by grouping related methods and fields
- Extract each responsibility into its own class with a focused interface
- Use composition: the original class delegates to the new smaller classes
- Apply the Single Responsibility Principle as a litmus test for each extraction
- Set a hard line limit (300-400 lines) in linting to prevent regrowth

### Relationship To Other Concepts

- Related to [big-ball-of-mud](/concepts/big-ball-of-mud) because god objects are often one localized symptom of broader architectural entanglement.
- Related to [god-endpoint](/concepts/god-endpoint) as the route-level analogue of excessive responsibility concentration.
- Related to [feature-envy](/concepts/feature-envy) when methods cling to the god object despite logically belonging with other domain data or collaborators.

### Boundary

Use `god-object` when one class or module absorbs too many unrelated responsibilities, dependencies, and decisions.

Do not use it for any large class. The key issue is responsibility concentration that distorts the design.
