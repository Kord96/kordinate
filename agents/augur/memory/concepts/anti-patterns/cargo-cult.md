---
kind: concept
name: cargo-cult
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Design patterns applied without understanding their purpose (e.g., a Factory that only ever creates one type, a Singleton wrapping a stateless utility, a Repository layered over another Repository)
- Copy-pasted boilerplate with no modification or adaptation to the local context
- Over-abstracted simple code: interfaces with a single implementation and no foreseeable second one
- Cargo-culted configuration: settings copied from tutorials with no understanding of what they do
- "Best practice" applied everywhere regardless of whether the problem it solves exists here

### Confidence

- **high** -- Factory with one product, Singleton around pure functions, interface with exactly one implementation and no test doubles, Repository wrapping an ORM that is itself a repository
- **medium** -- boilerplate blocks identical across files with only names changed, configuration values matching popular tutorial defaults
- **low** -- abstractions that seem premature but might have future justification

## Impact

Adds complexity without benefit, making the codebase harder to read and maintain while solving no actual problem.

### Symptoms

- Developers must navigate through multiple indirection layers to find actual logic
- New team members ask "why is this pattern here?" and nobody can answer
- Adding a simple feature requires modifying boilerplate in 5+ files
- The codebase has more structural code (interfaces, factories, registries) than business logic
- Removing an abstraction layer causes no test failures, proving it added no value

### Remediation

- For each abstraction, document the concrete problem it solves -- delete it if no concrete problem exists
- Apply YAGNI: do not add patterns until a second use case demands them
- Replace single-implementation interfaces with concrete classes until polymorphism is actually needed
- Consolidate copy-pasted boilerplate into shared utilities or eliminate it entirely
- Review configuration values against documentation and remove or explain each non-default setting

### Relationship To Other Concepts

- Related to [golden-hammer](/concepts/golden-hammer) because both involve applying patterns uncritically rather than from fit.
- Related to [copy-paste-programming](/concepts/copy-paste-programming) when unexplained boilerplate is propagated without understanding.
- Related to [premature-optimization](/concepts/premature-optimization) when complex patterns are copied in for imagined needs rather than real constraints.

### Boundary

Use `cargo-cult` when code or architecture copies a pattern ritualistically without understanding why it exists or whether it fits.

Do not use it for any borrowed pattern. The key issue is imitation without causal understanding.
