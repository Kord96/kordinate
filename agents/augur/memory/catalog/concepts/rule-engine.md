---
description: Rule engine pattern for declarative business logic evaluation
type: pattern
category: domain-model
abstraction:
- design
- logic
status: primary
scope: backend
relationships:
  related_to:
  - feature-flag
  - specification
  - strategy
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Rule Engine

## Recognition

How to identify this pattern in code.

### Signatures

- `Rule`, `Condition`, `Action` class hierarchy or interfaces
- `decision_table` or `DecisionTable` data structures mapping conditions to outcomes
- `evaluate()`, `execute_rules()`, `fire_rules()` methods on engine or context objects
- `rule_engine`, `RuleEngine`, `BusinessRule` class or module names
- Python: `business-rules`, `durable-rules`, `rule-engine` library imports
- JS/TS: `json-rules-engine`, `nools`, rule definition objects with `conditions` and `event` keys
- Go: `grule-rule-engine`, `gorules`, custom rule evaluation with `Predicate` functions
- Rust: `zen-engine`, custom rule trait with `evaluate(&self, context: &Context) -> bool`
- Java: Drools imports (`org.kie`, `org.drools`), `@Rule` annotations, `KieSession` usage
- `predicate`, `when`, `then`, `priority`, `salience` keywords in rule definitions

### Confidence

- **high** -- Dedicated rule engine library (Drools, json-rules-engine, grule) with declarative rule definitions, evaluation context, and priority/salience ordering
- **medium** -- Custom Rule/Condition/Action classes with an evaluate loop and decision tables stored externally
- **low** -- Chain of if/else statements implementing business logic that could be expressed as rules but lacks a formal engine

## Architecture

### Relationship To Other Concepts

- `rule-engine` is for declarative policy evaluation with externalized rules, ordering, and execution context.
- Use `specification` when the main concern is composable predicates, not a full execution engine.
- Use `strategy` when behavior is chosen from a small fixed set of implementations rather than a rule set.
- Use `feature-flag` when the concern is controlled rollout or gating, not general business decisioning.

### When to use
- Complex business logic that changes frequently and should be managed by non-developers
- Decision-heavy domains (insurance underwriting, loan approval, pricing engines) with many conditional paths
- Systems where rules need to be auditable, testable in isolation, and hot-reloadable without deployment

### Anti-patterns
- Embedding rule logic in application code instead of externalizing it, making changes require deployments
- No defined evaluation order, causing rule conflicts and non-deterministic outcomes
- Rules with side effects that modify shared state, making composition unpredictable

### Complements
- [strategy](/concepts/strategy) — rules often delegate to strategy implementations for their actions
- [specification](/concepts/specification) — specification pattern formalizes the condition side of rules
- [feature-flag](/concepts/feature-flag) — rule engines sometimes subsume feature flag logic

### Boundary

Do not use `rule-engine` for ordinary configuration switches or a handful of if/else branches. Prefer it only when rules are first-class artifacts that are evaluated by an engine.

## Impact

A rule engine separates business logic from application code, enabling rapid policy changes but introducing a secondary execution model that must be tested, versioned, and monitored independently. Rule evaluation performance and conflict resolution become critical operational concerns.
