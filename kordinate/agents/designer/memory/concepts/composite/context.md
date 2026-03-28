## Testing

Verify that leaf and composite nodes implement the same interface and tree operations work recursively.

### Unit Tests

- Call the operation on a leaf node and verify direct behavior
- Call the operation on a composite and verify it delegates to all children recursively
- Test add/remove child operations and verify the tree structure updates correctly

### Integration Tests

- Build a multi-level tree and verify the operation traverses all levels, aggregating results correctly
- Test serialization: serialize the tree, deserialize, and verify the structure and behavior are preserved

### Failure Injection

- Add a cyclic reference and verify the traversal detects it rather than looping infinitely

