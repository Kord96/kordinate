# Augur Concept Decision External Audit

External audit summary for the current concept decision design and detector/fact/semantic-review split.

Sources:

- DeepSeek `deepseek-reasoner`
- Anthropic `claude-opus`
- Gemini `gemini-2.5-pro` was attempted twice and returned repeated `503 Service Unavailable`, so it is marked inconclusive for this pass.

## Consensus

Both DeepSeek and Opus agree on the main structural judgment:

- the split between detector evidence, facts, and semantic review is directionally correct
- fact extraction is still too weak to act as a concept confirmation layer by itself
- semantic-review concepts should require LLM review even when detector evidence is strong
- contradiction handling is underdefined
- policy files are not yet fully consistent with the intended concept classes

## Highest-Value Actions

### 1. Make semantic-review concepts mandatory review concepts

Both audits called out the same inconsistency:

- `event-sourcing`
- `outbox`

These currently allow auto-confirm in policy, but they should require semantic review.

Planned change:

- set `auto_confirm.allowed: false` for semantic-review concepts unless a concept is intentionally split into a narrow auto-confirmable subtype

### 2. Facts should produce candidates, not final concept confirmations

`infer_concepts_from_facts.py` is still acting too much like a concept confirmer.

Planned change:

- use fact extraction to emit:
  - candidate concepts
  - contradiction signals
  - missing pairings
  - review triggers
- reserve final confirmation for:
  - narrow auto-confirm concepts with strict policy thresholds
  - semantic review for architecture-level concepts

### 3. Add contradiction and override rules explicitly

Both audits flagged the same missing logic:

- what happens when detectors say yes but facts are weak
- what happens when facts contradict detector matches
- what happens when a concept has broad textual matches but no structural support

Planned change:

- add explicit contradiction handling in the decision flow
- add a contradiction-aware verdict field
- define override rules for:
  - detector evidence vs fact evidence
  - semantic review vs heuristic candidate generation

### 4. Separate detector evidence from fact evidence in verdicts

Opus specifically called out the need for a clearer split in the final verdict schema.

Planned change:

- keep detector evidence and fact evidence as separate fields
- add contradiction resolution notes
- expose confidence factors instead of a single opaque confidence value

## Model-Specific Notes

### DeepSeek

Most useful recommendations:

- enforce concept class consistency in policy files
- strengthen negative signals from facts and detectors
- always route semantic-review concepts to LLM review
- allow auto-confirm only for narrow, high-confidence, contradiction-free concepts
- use evaluation failures to tighten detector policy over time

### Opus

Most useful recommendations:

- `route-guard` may be concrete enough for auto-confirm in some stacks
- `repository` should likely be conditional:
  - framework-backed repository implementations may be auto-confirmable
  - architectural repository pattern claims should still require review
- add or prepare semantic-review support for:
  - `ddd`
  - `cqrs`
  - `saga`
  - `microservices`
  - `modular-monolith`

Most useful schema additions:

- `contradiction_resolution`
- `fact_evidence`
- `confidence_factors`

## Recommended Immediate Changes

1. Fix policy consistency first.
   - `event-sourcing` and `outbox` should not auto-confirm.

2. Change fact inference semantics.
   - `infer_concepts_from_facts.py` should emit candidate concepts for semantic-review concepts rather than final confirmations.

3. Extend the verdict schema.
   - Add contradiction-aware fields and separate fact evidence from detector evidence.

4. Define the decision precedence rules.
   - Detector matches can nominate.
   - Facts can strengthen or contradict.
   - Semantic review decides architecture-level concepts.

5. Keep improving fact extraction before broad concept tuning.
   - Better route, model, auth, client, and middleware facts will improve concept quality downstream.
