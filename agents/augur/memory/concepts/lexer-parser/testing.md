---
description: Lexer/Parser — testing guidance
type: supplementary
---
## Testing

Test the lexer and parser independently, then verify end-to-end parsing with a golden test corpus.

### Lexer Tests

- Tokenize known input strings and assert the exact token sequence (type, value, position)
- Test edge cases: empty input, unterminated strings, nested comments, escape sequences
- Verify that source locations (line, column) are accurate for error reporting

### Parser Tests

- Parse token streams into ASTs and assert structural equality with expected trees
- Test error recovery: malformed input should produce a useful error message with source location, not a crash
- Verify precedence and associativity rules with ambiguous expressions

### End-to-End Tests

- Maintain a corpus of valid and invalid source files with expected AST output or error messages
- Add a regression test for every parser bug fix to prevent recurrence
