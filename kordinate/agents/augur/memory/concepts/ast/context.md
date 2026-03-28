## Testing

Test parsing correctness, tree traversal, and transformation output for representative input cases.

### Unit Tests

- Parse known input strings and assert the resulting AST structure matches expected node types and hierarchy
- Test visitor/walker traversal visits nodes in the correct order (pre-order, post-order)
- Verify transformation: apply a rewrite rule and assert the output AST reflects the change

### Integration Tests

- Round-trip test: parse input to AST, transform, then serialize back and verify semantic equivalence
- Test with real-world input samples to catch edge cases in grammar handling

### Failure Injection

- Feed malformed input and verify the parser produces clear syntax errors with line/column positions

