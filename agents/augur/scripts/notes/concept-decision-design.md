# Augur Concept Decision Design

Design for concept decisions after the detector and facts layers.

## Core Principle

Concepts should not be decided by detector output alone.

Detectors and facts provide:

- grounded evidence
- high-precision canonical matches
- strong negative signals
- concrete file-level observations

The LLM provides:

- cross-file interpretation
- architecture-level judgment
- distinction between naming and real structure
- resolution of ambiguous broad matches

The final concept verdict should combine both.

## Decision Layers

### 1. Detector evidence

Inputs:

- `ast-grep` matches
- `semgrep` matches
- detector-side signatures
- detector-side policy

Output:

- evidence records
- local detector verdicts:
  - `confirmed`
  - `candidate`
  - `inconclusive`
  - `contradicted`

Detector evidence is strongest for concrete implementation patterns and weakest for architectural concepts.

### 2. Facts

Inputs:

- normalized route facts
- model facts
- external-client facts
- auth-surface facts
- middleware facts
- import-graph facts
- config, jobs, and events facts

Output:

- candidate concepts suggested by repo evidence
- contradictions and missing expected pairings
- architecture signals tied to real files

Facts are the stable lower layer. They should strongly constrain concept reasoning, but they should not fully determine it.

### 3. Semantic repo understanding

Inputs:

- relevant files from the repo
- fact summaries
- detector evidence
- concept semantics from `memory/catalog/concepts/`

Output:

- final architectural judgment
- answers to concept-specific questions
- confirmation or rejection of detector candidates
- explanations for broad or contradictory evidence

This layer is required for concepts where implementation signals are not enough.

## Concept Classes

Use two main concept classes for decision policy.

### Auto-confirm eligible

These may be auto-confirmed when detector evidence is precise and policy thresholds are met.

Typical properties:

- concrete library usage
- explicit framework API usage
- low ambiguity structural signals
- narrow AST or semgrep matches

Initial auto-confirm candidates:

- `timeout`
- `retry`
- `input-validation`
- `router`
- `route-guard`
- `structured-logging`
- `health-check`
- `token-auth`
- `session-auth`
- `oauth-oidc`
- `api-key-auth`
- `rbac`
- `graphql`
- `grpc`
- `websocket`
- `server-sent-events`

These still need policy control. Broad matches should stay candidates.

### Semantic-review required

These should usually require LLM semantic confirmation even when detectors fire.

Typical properties:

- architecture-level pattern
- broad naming overlap with other concepts
- distinction depends on how parts interact, not just that they exist
- easy to hallucinate from directories or class names alone

Initial semantic-review concepts:

- `hexagonal`
- `repository`
- `dependency-injection`
- `ddd`
- `cqrs`
- `event-sourcing`
- `outbox`
- `saga`
- `saga-orchestrator`
- `unit-of-work`
- `aggregate`
- `data-mapper`
- `active-record`
- `layered`
- `microservices`
- `modular-monolith`
- `service-mesh`
- `plugin`
- `workflow-engine`

For these, detectors should mostly generate candidates plus evidence, not direct final confirmations.

## Final Verdict Schema

Each concept in the final decision layer should produce a record like:

```json
{
  "concept": "retry",
  "category": "resilience",
  "verdict": "confirmed",
  "confidence": "medium",
  "decision_mode": "auto-confirm|semantic-review|fact-inference",
  "evidence_summary": {
    "ast_matches": 3,
    "semgrep_matches": 0,
    "fact_hits": 2,
    "signature_hits": 1,
    "contradictions": 0
  },
  "grounded_in": [
    "src/client.py:42",
    "src/retry.py:10"
  ],
  "detector_verdicts": [
    {
      "source": "ast-grep",
      "verdict": "confirmed"
    }
  ],
  "semantic_review": {
    "required": false,
    "performed": false,
    "summary": ""
  },
  "questions": [
    {
      "id": "retry-bounded-attempts",
      "answer": "yes",
      "weight": 3,
      "justification": "stop_after_attempt is configured in src/retry.py"
    }
  ],
  "explanation": "Explicit tenacity decorators and bounded retry configuration were detected on external client calls."
}
```

Required fields:

- `concept`
- `verdict`
- `confidence`
- `decision_mode`
- `grounded_in`
- `explanation`

Important distinction:

- detector verdicts are evidence-local
- final verdict is concept-global

## Decision Modes

### `auto-confirm`

Use when:

- concept is in the auto-confirm class
- policy allows auto-confirm
- evidence is narrow and high-confidence
- no meaningful contradiction exists

### `semantic-review`

Use when:

- concept is in the semantic-review class
- evidence is broad or architecture-level
- multiple concepts could explain the same signals
- negative signals or contradictions exist

### `fact-inference`

Use when:

- concept is suggested from stable facts rather than direct concept detectors
- the concept is concrete enough to infer safely from normalized evidence
- the inference remains grounded in facts

This mode should remain limited. It is a bridge, not the long-term primary concept engine.

## Decision Flow

Recommended order:

1. run detector rules
2. extract facts
3. produce concept candidates from:
   - detector hits
   - fact-derived suggestions
   - stack-implied expected concepts
4. classify each candidate:
   - auto-confirm eligible
   - semantic-review required
5. for auto-confirm candidates:
   - apply detector policy thresholds
   - confirm only when evidence is narrow and grounded
6. for semantic-review candidates:
   - read the repo evidence and relevant semantic docs
   - answer policy questions
   - issue final verdict
7. record contradictions and absent expected pairings
8. emit final concept decision records

## Role Of `infer_concepts_from_facts.py`

`infer_concepts_from_facts.py` should be treated as a bootstrap bridge.

It is useful for:

- producing early candidate concepts
- providing a facts-first baseline
- helping evaluation before the full concept decision layer is complete

It should not be treated as the final concept engine.

Long term:

- facts should suggest candidates
- policy should determine review requirements
- LLM semantic understanding should resolve final architectural verdicts

## Initial Auto-Confirm Policy Guidance

Safe default:

- auto-confirm only when:
  - detector strength >= 5
  - match confidence >= 4
  - specificity is `narrow`
  - contradiction count is `0`

Otherwise:

- keep as `candidate`
- or require semantic review

For architecture-level concepts, prefer:

- `auto_confirm.allowed: false`

unless a later evaluation cycle proves the detector is unusually precise.

## Evaluation Implications

Benchmarking should score both:

- detector-layer correctness
- final concept-decision correctness

This separates:

- evidence extraction failures
- concept policy failures
- semantic interpretation failures

That separation is important. Otherwise, all concept misses look the same and the system becomes hard to improve.
