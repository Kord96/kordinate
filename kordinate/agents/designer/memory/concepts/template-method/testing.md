---
description: Template Method — testing guidance
type: supplementary
curated: true
scope: global
preloaded: none
---
# Testing

- Test each subclass by invoking the template method and verifying that overridden hooks produce the expected outcome
- Verify that the template method itself is not overridable (final/non-virtual) in subclasses
- Test hook defaults: subclasses that do not override optional hooks should still produce correct behavior
- Test the execution order of hooks by recording call sequences in test subclasses
- Assert that subclasses override only the intended extension points, not other methods of the base class
- Test with a minimal stub subclass that only implements required abstract methods to verify defaults
- Verify that the number of hooks is manageable (3-5) and the base class documents required vs optional
