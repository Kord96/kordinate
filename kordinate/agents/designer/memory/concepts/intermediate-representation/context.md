## Testing

Verify that IR construction, optimization passes, and lowering produce correct and well-typed output.

### Unit Tests

- Assert that AST-to-IR lowering produces the expected IR instructions for known input programs
- Test each optimization pass in isolation: feed a known IR, run the pass, and assert the transformed output
- Verify IR is well-typed: every instruction's operand types match the expected types

### Round-trip Tests

- Serialize IR to text or binary, deserialize, and assert structural equality with the original
- Lower source to IR, then to output, and verify the output matches a golden reference for each test case

### Regression Tests

- Maintain a corpus of input programs with expected IR output to catch regressions in lowering or optimization
- Add a new test case for every bug found in IR construction or pass ordering
- Verify that debug info (source locations) survives all transformation passes

