---
description: Lexer/Parser architectural pattern
type: pattern
testable: true
curated: true
scope: global
preloaded: none
graphable: true
---
# Lexer/Parser

## Recognition

How to identify this pattern in code.

### Signatures

- Two-phase processing: tokenization (lexer/scanner) followed by parsing into a tree structure
- `Token` type or enum with variants like `Identifier`, `Number`, `StringLiteral`, `Keyword`
- `Lexer` or `Scanner` class with `next_token()`/`scan()` methods consuming character input
- `Parser` class producing an AST from a token stream
- `peek()`, `advance()`, `expect()`, `consume()` methods on the parser
- Grammar rules encoded as recursive descent functions or parser combinators
- Libraries: ANTLR, tree-sitter, pest (Rust), PLY (Python), nom (Rust), yacc/bison, PEG.js, pyparsing

### Confidence

- **high** — `Lexer`/`Scanner` class producing `Token` values consumed by a `Parser` with `peek()`/`advance()`/`expect()` methods
- **medium** — token enum with keyword and operator variants, plus recursive functions matching grammar productions
- **low** — string splitting into labeled chunks followed by structured interpretation of the chunks

## Architecture

Look for clean separation between lexical analysis (characters to tokens) and syntactic analysis (tokens to tree).

### Review Checklist

- Lexer handles all whitespace, comments, and string escaping before tokens reach the parser
- Token types carry source location (line, column) for error reporting
- Parser methods map one-to-one to grammar productions for readability
- Error recovery produces useful messages with source location, not just "unexpected token"
- Lexer and parser are independently testable (token stream tests, parse tree tests)
- Grammar is unambiguous or ambiguities are resolved with explicit precedence rules

### Anti-patterns

- Parser operating directly on raw characters instead of a token stream (mixed concerns)
- No source location tracking, making error messages useless for users
- Deeply nested recursive descent with no precedence climbing (stack overflow on expressions)
- Grammar rules scattered across unrelated modules instead of grouped by language construct
