# Testing

- Test each `visit_*` method independently with a single element type to verify correct behavior
- Verify double dispatch: `accept(visitor)` calls the correct `visit_*` method for each element type
- Test traversal order (depth-first, breadth-first) with a known tree structure and recorded visit sequence
- Test the fallback handler (`generic_visit`) for unvisited element types
- Verify that adding a new visitor does not require modifying element classes
- Test visitor state accumulation: verify reset boundaries between independent traversals
- Assert that visitors access only the element's public interface, not private internals
- Test with deeply nested and wide trees to verify no stack overflow or performance degradation

