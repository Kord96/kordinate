---
description: Shotgun Surgery anti-pattern
type: anti-pattern
testable: true
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - copy-paste-programming
  - tight-coupling
  - god-object
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: none
examples: []
---
# Shotgun Surgery

## Recognition

How to identify this anti-pattern in code.

### Signatures

- One logical change requires editing 10+ files across different modules or packages
- Feature implementation spread across many packages with no central module
- Cross-cutting concerns (logging, auth, validation) duplicated in every module instead of centralized
- A single bug fix touching files in 5+ directories
- Git commits that routinely modify files across unrelated packages for a single feature
- Configuration values repeated in multiple files rather than sourced from one location
- The same conditional logic (`if feature_x:`) scattered across many modules

### Confidence

- **high** -- a single feature branch consistently modifies 10+ files across 5+ directories, and this pattern repeats across multiple features
- **medium** -- cross-cutting concerns like authorization checks or logging formats are duplicated in many modules
- **low** -- a recent feature required changes in more directories than expected, but it may be a one-off

## Impact

Changes are expensive and error-prone because a single logical modification requires coordinated edits across many scattered locations.

### Symptoms

- Simple feature requests take disproportionately long to implement
- Bug fixes frequently miss one of the many locations that need updating
- Code reviews are large and span many unrelated files
- Developers fear making changes because they cannot be sure they found every location
- Regression rate is high despite thorough-looking changes

### Remediation

- Identify the scattered concern and consolidate it into a single module or class
- Use decorators, middleware, or aspect-oriented techniques for cross-cutting concerns
- Apply the DRY principle by extracting shared logic into one authoritative location
- Introduce a facade or service layer that centralizes the scattered operations
- Set up architectural linting rules to prevent the concern from spreading again

### Relationship To Other Concepts

- Related to [copy-paste-programming](/concepts/copy-paste-programming) because duplicated logic is one common cause of changes being scattered across many files.
- Related to [tight-coupling](/concepts/tight-coupling) because widespread dependency entanglement makes one logical change ripple everywhere.
- Related to [god-object](/concepts/god-object) when one over-centralized class forces many callers and extensions to change together.

### Boundary

Use `shotgun-surgery` when one logical change repeatedly forces coordinated edits across many scattered files or modules.

Do not use it for large but cohesive refactors that touch many places for a clearly centralized reason.
